"""LLM polish for a workspace's path-keyed ``.help/summaries.json``.

Upgrades mechanically seeded one-line summaries (attune-ai
``scripts/seed_help_summaries.py``) into purpose-written catalog lines
via the Anthropic Batch API on the **capable** tier. Design:
``specs/summaries-polish/`` in the attune workspace repo.

Provenance lives in a sibling ``.help/summaries.meta.json`` (the
consumed sidecar stays schema-pure per ADR-004)::

    { "cli/error.md": {
        "polished_at": "...", "model": "...",
        "source_hash": "...", "summary_hash": "...",
        "truncated": false } }

Skip rules: a meta entry whose ``summary_hash`` matches the current
sidecar value is already polished (skip unless ``force``); a mismatch
means a human edited it since — hand edits always win.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    BatchPolishResult,
)
from attune_author.model_tiers import fable_extras, resolve_model

#: Ceiling for one summary line; the prompt asks for <=180 so honest
#: outputs never hit the truncation path.
MAX_SUMMARY_CHARS = 200

#: Response budget: a one-line summary is ~60 tokens; 200 leaves slack
#: for models that narrate before complying (we keep the last line).
SUMMARY_MAX_TOKENS = 200

#: Template body cap sent to the model (chars). Enough to characterize
#: any template; keeps per-request input cost bounded.
_BODY_CAP_CHARS = 8_000

#: Cost heuristics for the gate (USD per MTok, capable tier, Batch API
#: 50% discount applied). Deliberately coarse — the gate exists to stop
#: runaway invocations, not to do accounting.
_BATCH_USD_PER_MTOK_IN = 3.0 / 2
_BATCH_USD_PER_MTOK_OUT = 15.0 / 2
_CHARS_PER_TOKEN = 4

_STATE_FILENAME = ".summaries-batch-state.json"
_META_FILENAME = "summaries.meta.json"
_SIDECAR_FILENAME = "summaries.json"

_SENTENCE_END = re.compile(r"(?<=[.!?])\s")

_SYSTEM = """\
You write one-line catalog summaries for developer help templates.

Rules:
- Output EXACTLY one line, no markdown, no quotes, no preamble.
- At most 180 characters.
- Lead with what the template answers and when a developer should read it.
- Keep feature names, API identifiers, CLI commands, and error strings
  VERBATIM — they are retrieval keywords.
- Do not invent capabilities that are not in the template body."""


class SummariesPolishError(RuntimeError):
    """Raised for unrecoverable polish-summaries failures (bad inputs,
    cost gate exceeded, missing state on --resume)."""


@dataclass(frozen=True)
class BuildReport:
    """What ``build_requests`` decided, for CLI reporting."""

    requests: list[BatchPolishRequest]
    skipped_polished: list[str]
    skipped_hand_edited: list[str]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SummariesPolishError(f"unreadable JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SummariesPolishError(f"{path} is not a JSON object")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_hash(template_text: str) -> str:
    """Frontmatter ``source_hash`` when present, else body sha256."""
    match = re.search(r"^source_hash:\s*([0-9a-f]{16,64})\s*$", template_text, re.MULTILINE)
    if match:
        return match.group(1)
    return _sha256(template_text)


def polish_model() -> str:
    """Capable tier, with the batch fable guard.

    The Batch API rejects the ``fallbacks`` param, so a fable model
    (possible via an ``ATTUNE_MODEL_CAPABLE`` pin) is swapped for the
    fallback target directly — same rationale as
    ``maintenance_batch._batch_polish_model()``.
    """
    model = resolve_model("capable")
    if fable_extras(model):
        return "claude-opus-4-8"
    return model


def custom_id_for(rel_path: str) -> str:
    """Stable Anthropic ``custom_id`` for one template path."""
    return f"sum__{rel_path}"


def build_requests(help_dir: Path, model: str, *, force: bool = False) -> BuildReport:
    """Assemble one batch request per polishable sidecar entry."""
    sidecar = _read_json(help_dir / _SIDECAR_FILENAME)
    if not sidecar:
        raise SummariesPolishError(
            f"no {_SIDECAR_FILENAME} at {help_dir} — seed it first "
            "(scripts/seed_help_summaries.py in the workspace repo)"
        )
    meta = _read_json(help_dir / _META_FILENAME)
    templates_root = help_dir / "templates"

    requests: list[BatchPolishRequest] = []
    skipped_polished: list[str] = []
    skipped_hand: list[str] = []
    for rel_path, summary in sorted(sidecar.items()):
        record = meta.get(rel_path)
        if isinstance(record, dict) and record.get("summary_hash"):
            if record["summary_hash"] == _sha256(str(summary)):
                if not force:
                    skipped_polished.append(rel_path)
                    continue
            else:
                # Sidecar changed after we wrote it: a human refined the
                # line (GUI Summaries page). Hand edits always win.
                skipped_hand.append(rel_path)
                continue
        template_path = templates_root / rel_path
        if not template_path.is_file():
            continue  # orphaned sidecar key; reseeding cleans these up
        body = template_path.read_text(encoding="utf-8")
        user_message = (
            f"Template path: {rel_path}\n"
            f"Current (mechanical) summary: {summary}\n\n"
            f"Template body (may be truncated):\n\n{body[:_BODY_CAP_CHARS]}"
        )
        requests.append(
            BatchPolishRequest(
                custom_id=custom_id_for(rel_path),
                feature=str(Path(rel_path).parent),
                depth=Path(rel_path).stem,
                system=_SYSTEM,
                user_message=user_message,
                model=model,
                max_tokens=SUMMARY_MAX_TOKENS,
                cache_system=False,  # system prompt is far below cache minimums
            )
        )
    return BuildReport(requests, skipped_polished, skipped_hand)


def estimate_cost_usd(requests: list[BatchPolishRequest]) -> float:
    """Coarse spend estimate for the cost gate (chars/4 tokenizer)."""
    in_tokens = sum((len(r.system) + len(r.user_message)) / _CHARS_PER_TOKEN for r in requests)
    out_tokens = len(requests) * SUMMARY_MAX_TOKENS
    return in_tokens / 1e6 * _BATCH_USD_PER_MTOK_IN + out_tokens / 1e6 * _BATCH_USD_PER_MTOK_OUT


def _normalize_summary(text: str) -> tuple[str, bool]:
    """Collapse a model response to one clean line.

    Multi-line responses keep the LAST non-empty line (narration comes
    before the answer). Returns ``(line, truncated)``.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    line = lines[-1] if lines else ""
    line = line.strip("\"'` ")
    if len(line) <= MAX_SUMMARY_CHARS:
        return line, False
    parts = _SENTENCE_END.split(line)
    clipped = parts[0].strip()
    if len(clipped) > MAX_SUMMARY_CHARS:
        clipped = clipped[: MAX_SUMMARY_CHARS - 1].rstrip() + "…"
    return clipped, True


def apply_results(
    help_dir: Path,
    results: list[BatchPolishResult],
    *,
    model: str,
    _now: Any = None,
) -> dict[str, int]:
    """Splice successful results into the sidecar + meta.

    Errored/expired/canceled items keep their existing (seed) entry and
    are only counted — never silently dropped. Returns counters for the
    CLI report.
    """
    sidecar_path = help_dir / _SIDECAR_FILENAME
    sidecar = _read_json(sidecar_path)
    meta_path = help_dir / _META_FILENAME
    meta = _read_json(meta_path)
    templates_root = help_dir / "templates"

    stamp = (_now or (lambda: datetime.now(timezone.utc)))().isoformat()
    counters = {"applied": 0, "truncated": 0, "errored": 0, "empty": 0}
    for result in results:
        rel_path = result.custom_id.removeprefix("sum__")
        if result.error is not None or result.text is None:
            counters["errored"] += 1
            continue
        line, truncated = _normalize_summary(result.text)
        if not line:
            counters["empty"] += 1
            continue
        sidecar[rel_path] = line
        record: dict[str, Any] = {
            "polished_at": stamp,
            "model": model,
            "summary_hash": _sha256(line),
        }
        template_path = templates_root / rel_path
        if template_path.is_file():
            record["source_hash"] = _source_hash(template_path.read_text(encoding="utf-8"))
        if truncated:
            record["truncated"] = True
            counters["truncated"] += 1
        meta[rel_path] = record
        counters["applied"] += 1

    _write_json(sidecar_path, sidecar)
    _write_json(meta_path, meta)
    return counters


# --- state file (submit / resume split, mirrors maintain --batch) ---


def save_state(help_dir: Path, batch_id: str, requests: list[BatchPolishRequest]) -> None:
    _write_json(
        help_dir / _STATE_FILENAME,
        {
            "batch_id": batch_id,
            "model": requests[0].model if requests else "",
            "custom_ids": [r.custom_id for r in requests],
        },
    )


def load_state(help_dir: Path) -> dict[str, Any]:
    state = _read_json(help_dir / _STATE_FILENAME)
    if not state.get("batch_id"):
        raise SummariesPolishError(
            f"no pending batch state at {help_dir / _STATE_FILENAME}; " "run without --resume first"
        )
    return state


def clear_state(help_dir: Path) -> None:
    (help_dir / _STATE_FILENAME).unlink(missing_ok=True)
