"""Mock-only tests for polish-summaries (specs/summaries-polish).

No live calls: submit/poll are patched at the CLI import site; the
module itself never constructs an Anthropic client.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from attune_author import summaries_polish as sp
from attune_author.cli import main
from attune_author.doc_gen._anthropic_batch import BatchPolishResult


def _mk_help_dir(tmp_path: Path, entries: dict[str, str]) -> Path:
    help_dir = tmp_path / ".help"
    (help_dir / "templates").mkdir(parents=True)
    sidecar = {}
    for rel, summary in entries.items():
        p = help_dir / "templates" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\ntype: concept\nsource_hash: {'ab' * 16}\n---\n\n# T\n\nBody prose here.\n",
            encoding="utf-8",
        )
        sidecar[rel] = summary
    (help_dir / "summaries.json").write_text(json.dumps(sidecar), encoding="utf-8")
    return help_dir


class TestBuildRequests:
    def test_builds_one_request_per_entry(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed", "cli/faq.md": "seed2"})
        report = sp.build_requests(help_dir, "claude-sonnet-5")
        assert len(report.requests) == 2
        req = report.requests[0]
        assert req.custom_id == sp.custom_id_for("cli/concept.md")
        assert req.feature == "cli/concept.md"  # apply maps results via this
        assert req.model == "claude-sonnet-5"
        assert "Current (mechanical) summary: seed" in req.user_message
        assert "Body prose here." in req.user_message

    def test_missing_sidecar_raises(self, tmp_path):
        (tmp_path / ".help" / "templates").mkdir(parents=True)
        with pytest.raises(sp.SummariesPolishError, match="seed it first"):
            sp.build_requests(tmp_path / ".help", "claude-sonnet-5")

    def test_polished_entry_skipped_unless_force(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "polished line"})
        meta = {"cli/concept.md": {"summary_hash": sp._sha256("polished line")}}
        (help_dir / "summaries.meta.json").write_text(json.dumps(meta), encoding="utf-8")

        report = sp.build_requests(help_dir, "claude-sonnet-5")
        assert report.requests == []
        assert report.skipped_polished == ["cli/concept.md"]

        forced = sp.build_requests(help_dir, "claude-sonnet-5", force=True)
        assert len(forced.requests) == 1

    def test_hand_edited_entry_always_skipped(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "human rewrote this"})
        meta = {"cli/concept.md": {"summary_hash": sp._sha256("what we wrote")}}
        (help_dir / "summaries.meta.json").write_text(json.dumps(meta), encoding="utf-8")

        for force in (False, True):
            report = sp.build_requests(help_dir, "claude-sonnet-5", force=force)
            assert report.requests == []
            assert report.skipped_hand_edited == ["cli/concept.md"]

    def test_orphaned_sidecar_key_ignored(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        sidecar["gone/nope.md"] = "orphan"
        (help_dir / "summaries.json").write_text(json.dumps(sidecar))
        report = sp.build_requests(help_dir, "claude-sonnet-5")
        assert [r.feature for r in report.requests] == ["cli/concept.md"]


class TestModelAndCost:
    def test_default_is_capable_tier(self, monkeypatch):
        monkeypatch.delenv("ATTUNE_MODEL_CAPABLE", raising=False)
        assert sp.polish_model() == "claude-sonnet-5"

    def test_fable_pin_swapped_for_opus_on_batch(self, monkeypatch):
        monkeypatch.setenv("ATTUNE_MODEL_CAPABLE", "claude-fable-5")
        assert sp.polish_model() == "claude-opus-4-8"

    def test_estimate_positive_and_scales(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"a/x.md": "s", "a/y.md": "s"})
        two = sp.estimate_cost_usd(sp.build_requests(help_dir, "m").requests)
        one = sp.estimate_cost_usd(sp.build_requests(help_dir, "m").requests[:1])
        assert 0 < one < two


class TestNormalize:
    def test_single_line_passes_through(self):
        line, truncated = sp._normalize_summary("Explains how the CLI routes input.")
        assert line == "Explains how the CLI routes input."
        assert truncated is False

    def test_multiline_keeps_last_line(self):
        text = "Here is the summary you asked for:\n\nActual one-liner."
        assert sp._normalize_summary(text) == ("Actual one-liner.", False)

    def test_overlong_truncates_at_sentence_boundary(self):
        text = "First sentence stays. " + "x" * 300
        line, truncated = sp._normalize_summary(text)
        assert line == "First sentence stays."
        assert truncated is True

    def test_overlong_single_sentence_hard_clips(self):
        line, truncated = sp._normalize_summary("y" * 300)
        assert len(line) <= sp.MAX_SUMMARY_CHARS
        assert truncated is True
        assert line.endswith("…")

    def test_truncation_breaks_at_clause_boundary_not_mid_word(self):
        """102 of 296 live entries clipped mid-word ('the /agent ski…');
        clip at the last comma/semicolon (or word) before the cap."""
        line = "Consult when integrating attune.agent_factory: " + ", ".join(
            f"Identifier{i}" for i in range(30)
        )
        clipped, truncated = sp._normalize_summary(line)
        assert truncated is True
        assert clipped.endswith("…")
        body = clipped.rstrip("…")
        # ends exactly at a full identifier, no partial token
        assert body.split(", ")[-1].startswith("Identifier")
        assert body == body.rstrip(" ,;")
        assert len(clipped) <= sp.MAX_SUMMARY_CHARS

    def test_truncation_word_boundary_without_clauses(self):
        words = "word " * 60
        clipped, truncated = sp._normalize_summary(words.strip())
        assert truncated is True
        assert clipped.endswith("word…")

    def test_strips_wrapping_quotes(self):
        assert sp._normalize_summary('"Quoted line."')[0] == "Quoted line."


class TestApplyResults:
    def _result(self, rel: str, text: str | None, error: str | None = None) -> BatchPolishResult:
        return BatchPolishResult(
            custom_id=sp.custom_id_for(rel),
            feature=rel,
            depth=Path(rel).stem,
            text=text,
            error=error,
        )

    def test_success_updates_sidecar_and_meta(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        now = lambda: datetime(2026, 7, 9, tzinfo=timezone.utc)  # noqa: E731
        counters = sp.apply_results(
            help_dir,
            [self._result("cli/concept.md", "Polished line.")],
            model="claude-sonnet-5",
            _now=now,
        )
        assert counters == {"applied": 1, "truncated": 0, "errored": 0, "empty": 0}
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        assert sidecar["cli/concept.md"] == "Polished line."
        meta = json.loads((help_dir / "summaries.meta.json").read_text())
        record = meta["cli/concept.md"]
        assert record["model"] == "claude-sonnet-5"
        assert record["summary_hash"] == sp._sha256("Polished line.")
        assert record["source_hash"] == "ab" * 16
        assert record["polished_at"].startswith("2026-07-09")

    def test_errored_item_keeps_seed_entry(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        counters = sp.apply_results(
            help_dir,
            [self._result("cli/concept.md", None, error="anthropic.RateLimitError")],
            model="m",
        )
        assert counters["errored"] == 1
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        assert sidecar["cli/concept.md"] == "seed"
        assert "cli/concept.md" not in json.loads((help_dir / "summaries.meta.json").read_text())

    def test_empty_response_keeps_seed_entry(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        counters = sp.apply_results(help_dir, [self._result("cli/concept.md", "   \n ")], model="m")
        assert counters["empty"] == 1
        assert json.loads((help_dir / "summaries.json").read_text())["cli/concept.md"] == "seed"

    def test_reapply_then_skip_roundtrip(self, tmp_path):
        """What apply writes, build_requests recognizes as polished."""
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        sp.apply_results(help_dir, [self._result("cli/concept.md", "Polished line.")], model="m")
        report = sp.build_requests(help_dir, "m")
        assert report.skipped_polished == ["cli/concept.md"]


class TestCli:
    def test_dry_run_prints_estimate_and_does_not_submit(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        with patch("attune_author.doc_gen._anthropic_batch.submit_batch") as mock_submit:
            code = main(["polish-summaries", "--help-dir", str(help_dir), "--dry-run"])
        assert code == 0
        mock_submit.assert_not_called()
        out = capsys.readouterr().out
        assert "1 to polish" in out
        assert "est. ~$" in out

    def test_cost_gate_aborts_with_exit_2(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        with patch("attune_author.doc_gen._anthropic_batch.submit_batch") as mock_submit:
            code = main(["polish-summaries", "--help-dir", str(help_dir), "--max-usd", "0.0000001"])
        assert code == 2
        mock_submit.assert_not_called()
        assert "exceeds --max-usd" in capsys.readouterr().err

    def test_happy_path_submits_polls_applies(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})

        def fake_poll(batch_id, expected, **kwargs):
            results = [
                BatchPolishResult(
                    custom_id=r.custom_id,
                    feature=r.feature,
                    depth=r.depth,
                    text="Polished line.",
                    error=None,
                )
                for r in expected
            ]
            return "ended", results

        with (
            patch(
                "attune_author.doc_gen._anthropic_batch.submit_batch",
                return_value="batch_123",
            ),
            patch(
                "attune_author.doc_gen._anthropic_batch.poll_batch",
                side_effect=fake_poll,
            ),
        ):
            code = main(["polish-summaries", "--help-dir", str(help_dir)])
        assert code == 0
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        assert sidecar["cli/concept.md"] == "Polished line."
        assert not (help_dir / ".summaries-batch-state.json").exists()
        assert "applied 1" in capsys.readouterr().out

    def test_timeout_keeps_state_and_exits_3(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        with (
            patch(
                "attune_author.doc_gen._anthropic_batch.submit_batch",
                return_value="batch_123",
            ),
            patch(
                "attune_author.doc_gen._anthropic_batch.poll_batch",
                return_value=("timed_out", []),
            ),
        ):
            code = main(["polish-summaries", "--help-dir", str(help_dir)])
        assert code == 3
        state = json.loads((help_dir / ".summaries-batch-state.json").read_text())
        assert state["batch_id"] == "batch_123"
        assert "--resume" in capsys.readouterr().err

    def test_resume_without_state_exits_2(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        code = main(["polish-summaries", "--help-dir", str(help_dir), "--resume"])
        assert code == 2
        assert "no pending batch state" in capsys.readouterr().err

    def test_nothing_to_polish_exits_0_without_submit(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "done line"})
        meta = {"cli/concept.md": {"summary_hash": sp._sha256("done line")}}
        (help_dir / "summaries.meta.json").write_text(json.dumps(meta), encoding="utf-8")
        with patch("attune_author.doc_gen._anthropic_batch.submit_batch") as mock_submit:
            code = main(["polish-summaries", "--help-dir", str(help_dir)])
        assert code == 0
        mock_submit.assert_not_called()
        assert "0 to polish" in capsys.readouterr().out


class TestJsonAndHashEdges:
    def test_unreadable_sidecar_raises(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        (help_dir / "summaries.json").write_text("{not json", encoding="utf-8")
        with pytest.raises(sp.SummariesPolishError, match="unreadable JSON"):
            sp.build_requests(help_dir, "m")

    def test_non_object_sidecar_raises(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        (help_dir / "summaries.json").write_text('["a", "list"]', encoding="utf-8")
        with pytest.raises(sp.SummariesPolishError, match="not a JSON object"):
            sp.build_requests(help_dir, "m")

    def test_source_hash_falls_back_to_body_sha(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        template = help_dir / "templates" / "cli" / "concept.md"
        template.write_text("# No frontmatter here\n\nJust body.\n", encoding="utf-8")
        sp.apply_results(
            help_dir,
            [
                BatchPolishResult(
                    custom_id=sp.custom_id_for("cli/concept.md"),
                    feature="cli/concept.md",
                    depth="concept",
                    text="Polished.",
                    error=None,
                )
            ],
            model="m",
        )
        meta = json.loads((help_dir / "summaries.meta.json").read_text())
        expected = sp._sha256(template.read_text(encoding="utf-8"))
        assert meta["cli/concept.md"]["source_hash"] == expected

    def test_apply_truncates_overlong_result_and_flags_meta(self, tmp_path):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        long_text = "Leading sentence stays. " + "pad " * 100
        counters = sp.apply_results(
            help_dir,
            [
                BatchPolishResult(
                    custom_id=sp.custom_id_for("cli/concept.md"),
                    feature="cli/concept.md",
                    depth="concept",
                    text=long_text,
                    error=None,
                )
            ],
            model="m",
        )
        assert counters["truncated"] == 1
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        assert sidecar["cli/concept.md"] == "Leading sentence stays."
        meta = json.loads((help_dir / "summaries.meta.json").read_text())
        assert meta["cli/concept.md"]["truncated"] is True


class TestCliResume:
    def test_resume_happy_path_polls_and_applies(self, tmp_path, capsys):
        help_dir = _mk_help_dir(tmp_path, {"cli/concept.md": "seed"})
        sp.save_state(
            help_dir,
            "batch_777",
            sp.build_requests(help_dir, "claude-sonnet-5").requests,
        )

        def fake_poll(batch_id, expected, **kwargs):
            assert batch_id == "batch_777"
            return "ended", [
                BatchPolishResult(
                    custom_id=r.custom_id,
                    feature=r.feature,
                    depth=r.depth,
                    text="Resumed polish.",
                    error=None,
                )
                for r in expected
            ]

        with (
            patch("attune_author.doc_gen._anthropic_batch.submit_batch") as mock_submit,
            patch(
                "attune_author.doc_gen._anthropic_batch.poll_batch",
                side_effect=fake_poll,
            ),
        ):
            code = main(["polish-summaries", "--help-dir", str(help_dir), "--resume"])
        assert code == 0
        mock_submit.assert_not_called()  # resume never resubmits
        sidecar = json.loads((help_dir / "summaries.json").read_text())
        assert sidecar["cli/concept.md"] == "Resumed polish."
        assert not (help_dir / ".summaries-batch-state.json").exists()
        assert "applied 1" in capsys.readouterr().out


class TestCustomIdContract:
    def test_matches_batch_api_charset(self):
        """The Batch API enforces ^[a-zA-Z0-9_-]{1,64}$ — a raw template
        path (slashes, dots) 400s the whole submit. Hit live 2026-07-10."""
        import re

        for rel in ("cli/concept.md", "elicitation-forms/troubleshooting.md"):
            cid = sp.custom_id_for(rel)
            assert re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", cid), cid

    def test_distinct_paths_get_distinct_ids(self):
        assert sp.custom_id_for("a/b.md") != sp.custom_id_for("a/c.md")
