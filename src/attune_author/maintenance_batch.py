"""Batched help maintenance via Anthropic's Message Batches API.

Sibling module to :mod:`attune_author.maintenance`. The
synchronous default path lives there; this module owns the
opt-in batch path triggered by ``attune-author maintain --batch``.

Two phases that run in two separate CLI invocations:

- **Submit** — :func:`submit_maintenance_batch` resolves stale
  features, builds a list of polish prompts, posts a single
  batch to Anthropic, and persists the resulting batch ID + a
  per-request manifest to ``.help/.batch-state.json``.

- **Resume** — :func:`resume_maintenance_batch` loads that
  state file, polls Anthropic until the batch terminates,
  splices results back into per-feature ``GenerationResult``
  records, writes templates, and deletes the state file.

Connecting the phases is the on-disk state file. We do NOT
persist *partial* polling progress; if a resume polling loop is
killed mid-flight, the next ``--resume`` re-polls from where
Anthropic says the batch is. Anthropic's view is the source of
truth.

See ``specs/author-batch-maintain/design.md`` for the full
state-file layout and resume-ergonomics design choices.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from attune_author.generator import PolishPreparation

from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    BatchPolishResult,
    adaptive_timeout_secs,
    poll_batch,
    submit_batch,
)

logger = logging.getLogger(__name__)


#: Filename under ``<help_dir>/`` where pending-batch metadata is stored.
STATE_FILENAME = ".batch-state.json"

#: Schema version for the state file. Bump if the on-disk shape changes
#: in an incompatible way; older files surface :class:`BatchStateExpired`
#: with a clean cleanup message.
STATE_SCHEMA_VERSION = 1

#: Anthropic retains batch results for 29 days. After that, ``retrieve``
#: returns 404 and ``results`` returns nothing. We surface a clear
#: cleanup hint before crashing on the network call.
BATCH_RETENTION_DAYS = 29


class BatchStateError(RuntimeError):
    """Base class for state-file errors."""


class BatchAlreadyPending(BatchStateError):
    """Raised when ``--batch`` is run while a state file already exists.

    The CLI surfaces a helpful message: pass ``--force`` to
    overwrite, or run ``--resume`` / ``--cancel`` on the
    existing batch first.
    """


class BatchStateExpired(BatchStateError):
    """Raised when the state file is older than Anthropic's retention.

    The CLI surfaces a clean cleanup hint instead of a stack
    trace. Users should delete ``.help/.batch-state.json`` and
    resubmit.
    """


class BatchStateNotFound(BatchStateError):
    """Raised when ``--resume`` / ``--status`` / ``--cancel`` runs
    but no state file exists. The CLI surfaces "no pending batch"."""


@dataclass(frozen=True)
class BatchStateRequest:
    """Per-request entry inside the state file's ``requests`` list."""

    custom_id: str
    feature: str
    depth: str

    def to_dict(self) -> dict[str, str]:
        return {
            "custom_id": self.custom_id,
            "feature": self.feature,
            "depth": self.depth,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, str]) -> BatchStateRequest:
        return cls(
            custom_id=raw["custom_id"],
            feature=raw["feature"],
            depth=raw["depth"],
        )


@dataclass(frozen=True)
class BatchState:
    """Persisted metadata for a submitted-not-yet-resumed batch.

    The state file is written at submit time and deleted at
    resume completion (success OR permanent failure). On a
    poll-loop timeout the file is intentionally **kept**, so
    the user's next ``--resume`` re-picks-up cleanly.
    """

    schema_version: int
    batch_id: str
    submitted_at: datetime
    expected_completion_at: datetime
    model: str
    requests: tuple[BatchStateRequest, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "batch_id": self.batch_id,
            "submitted_at": self.submitted_at.isoformat(),
            "expected_completion_at": self.expected_completion_at.isoformat(),
            "model": self.model,
            "requests": [r.to_dict() for r in self.requests],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> BatchState:
        # Tolerate "Z" suffix (datetime.fromisoformat handles it on
        # Python 3.11+; we normalize for 3.10 compatibility).
        sub = _parse_iso(raw["submitted_at"])
        eta = _parse_iso(raw["expected_completion_at"])
        return cls(
            schema_version=int(raw["schema_version"]),
            batch_id=str(raw["batch_id"]),
            submitted_at=sub,
            expected_completion_at=eta,
            model=str(raw["model"]),
            requests=tuple(BatchStateRequest.from_dict(r) for r in raw.get("requests", [])),
        )

    def to_polish_requests(
        self,
        prompt_lookup: dict[tuple[str, str], BatchPolishRequest],
    ) -> list[BatchPolishRequest]:
        """Reconstruct ``BatchPolishRequest`` objects for resume polling.

        The state file persists only the (custom_id, feature, depth)
        triples — the actual system/user prompts are reproducible
        from the manifest at resume time. ``prompt_lookup`` maps
        ``(feature, depth)`` to the freshly-rebuilt
        ``BatchPolishRequest`` so the order is preserved.
        """
        out: list[BatchPolishRequest] = []
        for r in self.requests:
            req = prompt_lookup.get((r.feature, r.depth))
            if req is None:
                # Manifest changed between submit and resume — surface
                # via missing_in_results downstream rather than crashing.
                req = BatchPolishRequest(
                    custom_id=r.custom_id,
                    feature=r.feature,
                    depth=r.depth,
                    system="",
                    user_message="",
                    model=self.model,
                    max_tokens=0,
                )
            out.append(req)
        return out


def state_path(help_dir: str | Path) -> Path:
    """Resolve the on-disk state file path for ``help_dir``."""
    return Path(help_dir) / STATE_FILENAME


def write_batch_state(help_dir: str | Path, state: BatchState) -> Path:
    """Write the state file atomically.

    Uses a tempfile + rename so a half-written file never lands
    on disk if the process is killed mid-write.
    """
    target = state_path(help_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
    return target


def read_batch_state(
    help_dir: str | Path,
    *,
    now: datetime | None = None,
) -> BatchState:
    """Load the state file, validating schema + retention.

    Raises:
        BatchStateNotFound: No state file exists at ``help_dir``.
        BatchStateExpired: State file is older than Anthropic's
            29-day retention window, or its schema version is
            unrecognized.
    """
    target = state_path(help_dir)
    if not target.exists():
        raise BatchStateNotFound(f"no pending batch at {target}")

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BatchStateExpired(
            f"state file at {target} is corrupt; delete it and rerun --batch: {exc}"
        ) from None

    schema_version = int(raw.get("schema_version", 0))
    if schema_version != STATE_SCHEMA_VERSION:
        raise BatchStateExpired(
            f"state file at {target} has unsupported schema_version "
            f"{schema_version}; delete it and rerun --batch"
        )

    state = BatchState.from_dict(raw)

    horizon = (now or _now_utc()) - timedelta(days=BATCH_RETENTION_DAYS)
    if state.submitted_at < horizon:
        raise BatchStateExpired(
            f"batch submitted {state.submitted_at.isoformat()} is older than "
            f"Anthropic's {BATCH_RETENTION_DAYS}-day retention window; "
            f"delete {target} and rerun --batch"
        )

    return state


def delete_batch_state(help_dir: str | Path) -> None:
    """Remove the state file, no-op if it doesn't exist."""
    target = state_path(help_dir)
    if target.exists():
        target.unlink()


def has_pending_batch(help_dir: str | Path) -> bool:
    """Lightweight check for a state file's existence.

    Used by the bare ``maintain`` command to surface a one-liner
    hint without parsing the whole file. Does NOT raise on stale
    state — that surfaces only when a real load is attempted.
    """
    return state_path(help_dir).exists()


# --- helpers ---------------------------------------------------------------


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, normalizing the trailing Z."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# --- prompt construction ---------------------------------------------------


def custom_id_for(feature: str, depth: str) -> str:
    """Stable Anthropic ``custom_id`` for one (feature, depth) request."""
    return f"feat__{feature}__{depth}"


def _build_polish_request(
    feature_name: str,
    depth: str,
    rendered_content: str,
    source_summary: str,
    augmented_context: str | None,
) -> BatchPolishRequest:
    """Build a :class:`BatchPolishRequest` for one polish call.

    Uses the same ``build_polish_prompt`` helper the synchronous
    path calls, so the wire-level prompts are byte-identical.
    """
    from attune_author.polish import (
        _POLISH_MODEL,
        POLISH_CACHE_SYSTEM,
        POLISH_MAX_TOKENS,
        build_polish_prompt,
    )

    system, user = build_polish_prompt(
        rendered_content,
        feature_name,
        source_summary,
        depth,
        augmented_context=augmented_context,
    )
    return BatchPolishRequest(
        custom_id=custom_id_for(feature_name, depth),
        feature=feature_name,
        depth=depth,
        system=system,
        user_message=user,
        model=_POLISH_MODEL,
        max_tokens=POLISH_MAX_TOKENS,
        cache_system=POLISH_CACHE_SYSTEM,
    )


def _collect_polish_prompts(
    stale_features: list,
    help_dir: str | Path,
    project_root: str | Path,
    *,
    use_rag: bool = True,
) -> tuple[list[BatchPolishRequest], dict[str, PolishPreparation]]:
    """Render templates and build polish requests for stale features.

    Returns ``(requests, prep_by_feature)``:

    - ``requests`` is the flat list of all polish requests across
      every stale feature, in feature×depth order.
    - ``prep_by_feature`` maps feature name to the
      :class:`PolishPreparation` used at submit time, so the
      resume splicer can re-derive the same out_paths and
      depth ordering.

    Pure of LLM calls. The RAG grounding pass DOES happen here
    (mirroring the synchronous path's ``_maybe_polish``) — we
    bake the augmented_context into the user message so the
    batch result is comparable to a synchronous polish call.
    """
    from attune_author.generator import prepare_polish_phase
    from attune_author.polish import build_source_summary

    requests: list[BatchPolishRequest] = []
    prep_by_feature: dict[str, PolishPreparation] = {}

    for feature in stale_features:
        prep = prepare_polish_phase(
            feature=feature,
            help_dir=help_dir,
            project_root=project_root,
            use_rag=use_rag,
        )
        prep_by_feature[feature.name] = prep
        if not prep.pending:
            continue

        # Mirror _maybe_polish: build source summary + (optional) RAG context
        # once per feature, reuse across depths.
        source_info = prep.source_info
        summary = build_source_summary(
            public_classes=source_info.public_classes,
            public_functions=source_info.public_functions,
            module_docstrings=source_info.module_docstrings,
            file_count=source_info.file_count,
            function_signatures=source_info.function_signatures or None,
            class_signatures=source_info.class_signatures or None,
            module_constants=source_info.module_constants or None,
        )

        for entry in prep.pending:
            augmented: str | None = None
            if use_rag:
                from attune_author.rag_hook import ground_polish_context

                augmented = ground_polish_context(feature.name, entry.depth)
            requests.append(
                _build_polish_request(
                    feature_name=feature.name,
                    depth=entry.depth,
                    rendered_content=entry.rendered_content,
                    source_summary=summary,
                    augmented_context=augmented,
                )
            )

    return requests, prep_by_feature


# --- submit ----------------------------------------------------------------


def submit_maintenance_batch(
    help_dir: str | Path,
    project_root: str | Path,
    features: list[str] | None = None,
    *,
    force: bool = False,
    client: Any | None = None,
) -> BatchState:
    """SUBMIT phase: prepare prompts, post one batch, write state.

    Resolves stale features (or the explicit ``features`` list),
    renders all templates, builds polish requests, posts one
    Anthropic batch, and writes the state file. Returns the
    persisted :class:`BatchState` so the CLI can print a
    confirmation message.

    Raises:
        BatchAlreadyPending: A state file already exists.
            Pass ``force=True`` to overwrite (or run
            ``--cancel`` first to release the existing batch).
        ValueError: No stale features (nothing to do).
    """
    if not force and has_pending_batch(help_dir):
        raise BatchAlreadyPending(
            f"pending batch already submitted; state file at {state_path(help_dir)}. "
            "Run --resume, --cancel, or pass --force to overwrite."
        )

    from attune_author.maintenance import _resolve_stale_features

    stale = _resolve_stale_features(help_dir, project_root, features)
    if not stale:
        raise ValueError("no stale features to regenerate")

    requests, _prep = _collect_polish_prompts(stale, help_dir=help_dir, project_root=project_root)
    if not requests:
        raise ValueError("no polish requests to submit (all features skipped)")

    batch_id = submit_batch(requests, client=client)
    submitted_at = _now_utc()
    eta = submitted_at + _eta_for(len(requests))
    state = BatchState(
        schema_version=STATE_SCHEMA_VERSION,
        batch_id=batch_id,
        submitted_at=submitted_at,
        expected_completion_at=eta,
        model=requests[0].model,
        requests=tuple(
            BatchStateRequest(custom_id=r.custom_id, feature=r.feature, depth=r.depth)
            for r in requests
        ),
    )
    write_batch_state(help_dir, state)
    logger.info(
        "submitted batch %s (%d requests, eta %s)",
        batch_id,
        len(requests),
        eta.isoformat(),
    )
    return state


def _eta_for(num_requests: int) -> timedelta:
    """Estimate completion time for ``num_requests`` based on adaptive timeout."""
    return timedelta(seconds=adaptive_timeout_secs(num_requests))


# --- resume ----------------------------------------------------------------


def resume_maintenance_batch(
    help_dir: str | Path,
    project_root: str | Path,
    *,
    poll_interval_secs: float = 30.0,
    timeout_secs: float | None = None,
    client: Any | None = None,
    on_progress: Any = None,
) -> MaintenanceResultBatch:
    """RESUME phase: poll, splice, write.

    Loads the state file, polls the batch until terminal (or
    timeout), splices polished text per feature, and writes the
    final templates. On terminal completion (success or permanent
    failure for some features) the state file is **deleted**. On
    poll-loop timeout the state file is **kept** so the user's
    next ``--resume`` picks up cleanly.

    Per-feature failure isolation: if any depth of a feature's
    requests errored in the batch, the entire feature is marked
    failed (no templates written). Other features in the same
    batch are written normally.
    """
    state = read_batch_state(help_dir)
    # Re-resolve current stale features so we know what's currently expected.
    # We trust the state file's request list as the authoritative "what we
    # asked for"; current-staleness is only for the report.
    from attune_author.manifest import load_manifest as _load_manifest
    from attune_author.staleness import check_staleness as _check_staleness

    manifest = _load_manifest(help_dir)
    stale_features_in_state = [
        manifest.features[f] for f in {r.feature for r in state.requests} if f in manifest.features
    ]
    _, prep_by_feature = _collect_polish_prompts(
        stale_features_in_state,
        help_dir=help_dir,
        project_root=project_root,
    )

    # Re-build the request list so poll_batch can map results in the
    # same order as the state file (the on-the-wire entries have the
    # actual prompts; we don't need them at resume time, but we need
    # the request list to hold custom_ids and order).
    expected = [
        BatchPolishRequest(
            custom_id=r.custom_id,
            feature=r.feature,
            depth=r.depth,
            system="",
            user_message="",
            model=state.model,
            max_tokens=0,
        )
        for r in state.requests
    ]

    final_status, results = poll_batch(
        state.batch_id,
        expected,
        client=client,
        poll_interval_secs=poll_interval_secs,
        timeout_secs=timeout_secs,
        on_progress=on_progress,
    )

    # Group results by feature so we can apply per-feature isolation.
    per_feature: dict[str, list[BatchPolishResult]] = {}
    for r in results:
        per_feature.setdefault(r.feature, []).append(r)

    report_features = stale_features_in_state
    report = _check_staleness(manifest, help_dir, project_root, [f.name for f in report_features])
    rb = MaintenanceResultBatch(
        staleness=report,
        final_status=final_status,
        batch_id=state.batch_id,
    )

    for feature_name, results_for_feat in per_feature.items():
        prep = prep_by_feature.get(feature_name)
        if prep is None:
            # Manifest changed between submit and resume. We can't write
            # anything sensibly. Mark the feature failed and continue.
            rb.failed.append(feature_name)
            logger.warning(
                "Feature '%s' was in batch but is no longer in manifest; skipping",
                feature_name,
            )
            continue

        if any(r.error for r in results_for_feat):
            rb.failed.append(feature_name)
            for r in results_for_feat:
                if r.error:
                    logger.warning(
                        "Polish failed for %s/%s: %s",
                        r.feature,
                        r.depth,
                        r.error,
                    )
            continue

        polished = {r.depth: r.text or "" for r in results_for_feat}
        from attune_author.generator import apply_polish_results

        gen_result = apply_polish_results(prep, polished)
        rb.regenerated.append(gen_result)

    if final_status == "timed_out":
        # Keep state file. User can run --resume again later.
        logger.info(
            "Batch %s still running (%d/%d done); state file kept for re-resume",
            state.batch_id,
            sum(1 for r in results if r.text is not None),
            len(results),
        )
    else:
        delete_batch_state(help_dir)

    return rb


# --- status & cancel -------------------------------------------------------


def status_maintenance_batch(
    help_dir: str | Path,
    *,
    client: Any | None = None,
) -> dict[str, Any]:
    """STATUS phase: one-shot query, no polling.

    Returns a JSON-friendly dict with both the persisted local
    state and Anthropic's current view of the batch. Does not
    raise on terminal states — the caller (CLI) renders both the
    pending and the terminal cases.
    """
    state = read_batch_state(help_dir)
    if client is None:
        from attune_author.doc_gen._anthropic import get_client

        client = get_client()
    batch = client.messages.batches.retrieve(state.batch_id)
    counts = getattr(batch, "request_counts", None)
    return {
        "batch_id": state.batch_id,
        "submitted_at": state.submitted_at.isoformat(),
        "expected_completion_at": state.expected_completion_at.isoformat(),
        "model": state.model,
        "request_count": len(state.requests),
        "processing_status": getattr(batch, "processing_status", None),
        "request_counts": (
            {
                "succeeded": getattr(counts, "succeeded", 0),
                "errored": getattr(counts, "errored", 0),
                "expired": getattr(counts, "expired", 0),
                "canceled": getattr(counts, "canceled", 0),
                "processing": getattr(counts, "processing", 0),
            }
            if counts is not None
            else None
        ),
        "ended_at": getattr(batch, "ended_at", None),
        "expires_at": getattr(batch, "expires_at", None),
        "cancel_initiated_at": getattr(batch, "cancel_initiated_at", None),
    }


def cancel_maintenance_batch(
    help_dir: str | Path,
    *,
    client: Any | None = None,
) -> str:
    """CANCEL phase: cancel the batch and remove the state file.

    Returns the canceled batch_id for the CLI to confirm.
    """
    state = read_batch_state(help_dir)
    if client is None:
        from attune_author.doc_gen._anthropic import get_client

        client = get_client()
    try:
        client.messages.batches.cancel(state.batch_id)
    except Exception as exc:  # noqa: BLE001 — cancel is best-effort
        logger.warning(
            "cancel call failed for batch %s (state file still removed): %s",
            state.batch_id,
            exc,
        )
    delete_batch_state(help_dir)
    return state.batch_id


# --- result type -----------------------------------------------------------


@dataclass
class MaintenanceResultBatch:
    """Result of a batch maintenance run.

    Mirrors :class:`MaintenanceResult` so downstream consumers
    (status reports, hooks) can treat it interchangeably. Adds
    ``final_status`` and ``batch_id`` so callers can render
    timeouts and partial-completion states correctly.
    """

    staleness: Any  # StalenessReport — typed loosely to avoid import cycle
    final_status: str = "ended"
    batch_id: str = ""
    regenerated: list = None  # type: ignore[assignment]
    failed: list = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.regenerated is None:
            self.regenerated = []
        if self.failed is None:
            self.failed = []

    @property
    def stale_count(self) -> int:
        return self.staleness.stale_count

    @property
    def regenerated_count(self) -> int:
        return len(self.regenerated)
