"""Smoke eval — lightweight RAG gate check for CI.

Runs 5 maximally discriminating questions (from the v0.3.9 hallucination
benchmark) against sonnet in both baseline and treated conditions, judges
with Opus, and checks the results against the thresholds in eval_config.yaml.

Cost: ~10 answer calls + ~10 judge calls (~$0.10–0.30).

Exit codes:
  0  All enforced thresholds passed.
  1  One or more thresholds failed (deploy should be blocked).
  2  Configuration or I/O error (treat as gate failure).

Usage:
    python benchmarks/smoke_eval.py
    python benchmarks/smoke_eval.py --out /tmp/smoke_results.json
    python benchmarks/smoke_eval.py --no-color
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "benchmarks" / "hallucination-v0.3.9"

SMOKE_QUESTION_IDS = {2, 9, 12, 27, 39}
ANSWER_MODEL_ID = "claude-sonnet-4-6"
JUDGE_MODEL_ID = "claude-opus-4-6"

FAITHFULNESS_GATE = 0.95  # end_user persona — HARD gate (drives exit code)
ACCURACY_GATE = 0.85  # developer persona — ADVISORY on smoke; full-25 enforces

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def green(s: str) -> str:
    return _c("32", s)


def red(s: str) -> str:
    return _c("31", s)


def yellow(s: str) -> str:
    return _c("33", s)


def bold(s: str) -> str:
    return _c("1", s)


def dim(s: str) -> str:
    return _c("2", s)


# ---------------------------------------------------------------------------
# Context builders (mirrors run_answers.py logic)
# ---------------------------------------------------------------------------


def build_baseline_context() -> str:
    readme = (REPO / "README.md").read_text()
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    files = "\n".join(sorted(result.stdout.splitlines()))
    return (
        "# Repository: attune-author\n\n"
        "## File tree (tracked files)\n\n"
        f"```\n{files}\n```\n\n"
        "## README.md\n\n"
        f"{readme}"
    )


def build_treated_context(baseline: str, feature: str) -> str:
    ref = REPO / ".help" / "templates" / feature / "reference.md"
    if not ref.exists():
        raise FileNotFoundError(f"Missing reference template: {ref}")
    body = ref.read_text()
    return (
        baseline
        + "\n\n---\n\n"
        + f"## attune-help lookup result: feature={feature!r}, depth='reference'\n\n"
        + body
    )


# ---------------------------------------------------------------------------
# Answer + judge prompts (mirrors run_answers.py / run_judge.py)
# ---------------------------------------------------------------------------

ANSWER_SYSTEM = (
    "You are a developer assistant answering questions about the "
    "attune-author Python package. Use only the repository context "
    "provided. Be concise and specific. If a claim requires a detail "
    "you can verify from the context, give the exact detail; if you "
    "cannot verify it, say so rather than guessing."
)

JUDGE_SYSTEM = (
    "You are an impartial judge scoring a developer assistant's answer "
    "about a Python package. You receive: the question, the ground-truth "
    "answer verified from source, and the assistant's response. You return "
    "a single JSON object with keys `verdict` and `reasoning`.\n\n"
    "Verdicts:\n"
    "- `correct`: argument names right, return type right, no invented "
    "arguments or APIs. Type annotations are optional; extra correct detail "
    "is fine.\n"
    "- `partial`: one argument name wrong, one extra argument invented, "
    "or return type wrong — but the core call / claim is still recognizable "
    "and not fabricated.\n"
    "- `hallucinated`: the function / class / module doesn't exist as "
    "described, argument list is fabricated, wrong module, invented API, "
    "or answer contradicts ground truth on the main point.\n\n"
    "A response that correctly says 'I cannot verify this from the context' "
    "without inventing a specific wrong answer counts as `partial`, not "
    "`hallucinated`.\n\n"
    "Return ONLY the JSON object, no preamble or code fence."
)

_JSON_RE = re.compile(r"\{[\s\S]*\}")


def get_answer(client: Anthropic, context: str, question: str) -> str:
    user = f"{context}\n\n---\n\n# Question\n\n{question}"
    r = client.messages.create(
        model=ANSWER_MODEL_ID,
        max_tokens=1024,
        temperature=0,
        system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text


def judge_answer(client: Anthropic, question: str, truth: str, answer: str) -> dict:
    user = (
        f"## Question\n{question}\n\n"
        f"## Ground truth\n{truth}\n\n"
        f"## Assistant's answer\n{answer}\n"
    )
    r = client.messages.create(
        model=JUDGE_MODEL_ID,
        max_tokens=512,
        temperature=0,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = r.content[0].text
    m = _JSON_RE.search(raw)
    if not m:
        return {"verdict": "error", "reasoning": f"No JSON in judge response: {raw[:200]}"}
    try:
        parsed = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"verdict": "error", "reasoning": f"Invalid JSON: {e}; raw={raw[:200]}"}
    verdict = parsed.get("verdict", "").lower().strip()
    if verdict not in ("correct", "partial", "hallucinated"):
        return {"verdict": "error", "reasoning": f"Unknown verdict: {verdict!r}"}
    return {"verdict": verdict, "reasoning": parsed.get("reasoning", "")}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def compute_metrics(judgments: list[dict]) -> dict[str, float]:
    treated = [j for j in judgments if j["condition"] == "treated" and j["verdict"] != "error"]
    total = len(treated)
    if total == 0:
        return {"faithfulness": 0.0, "strict_accuracy": 0.0, "total_valid": 0}
    correct = sum(1 for j in treated if j["verdict"] == "correct")
    hallucinated = sum(1 for j in treated if j["verdict"] == "hallucinated")
    faithfulness = (total - hallucinated) / total
    strict_accuracy = correct / total
    return {
        "faithfulness": faithfulness,
        "strict_accuracy": strict_accuracy,
        "total_valid": total,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="Write JSON results to this path.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI output.")
    args = parser.parse_args(argv)

    if args.no_color:
        global _USE_COLOR
        _USE_COLOR = False

    client = Anthropic()

    # -- Load question subset ------------------------------------------------
    try:
        raw = yaml.safe_load((BENCH / "questions.yaml").read_text())
    except FileNotFoundError:
        print(red("ERROR: questions.yaml not found. Run from the repo root."), file=sys.stderr)
        return 2

    questions = [q for q in raw["questions"] if q["id"] in SMOKE_QUESTION_IDS]
    if len(questions) != len(SMOKE_QUESTION_IDS):
        found = {q["id"] for q in questions}
        missing = SMOKE_QUESTION_IDS - found
        print(red(f"ERROR: Missing question IDs in corpus: {missing}"), file=sys.stderr)
        return 2

    # -- Build contexts ------------------------------------------------------
    print(bold("\n=== attune-author RAG smoke eval ===\n"))
    print(dim(f"Questions : {sorted(SMOKE_QUESTION_IDS)}"))
    print(dim(f"Model     : {ANSWER_MODEL_ID}"))
    print(dim(f"Judge     : {JUDGE_MODEL_ID}"))
    print()

    try:
        baseline_ctx = build_baseline_context()
    except subprocess.CalledProcessError as e:
        print(red(f"ERROR building baseline context: {e}"), file=sys.stderr)
        return 2

    features = sorted({q["feature"] for q in questions})
    try:
        treated_ctx = {f: build_treated_context(baseline_ctx, f) for f in features}
    except FileNotFoundError as e:
        print(red(f"ERROR building treated context: {e}"), file=sys.stderr)
        return 2

    # -- Run answer + judge --------------------------------------------------
    judgments: list[dict] = []
    total_calls = len(questions) * 2  # baseline + treated
    done = 0

    for q in questions:
        for cond in ("baseline", "treated"):
            done += 1
            ctx = baseline_ctx if cond == "baseline" else treated_ctx[q["feature"]]
            label = f"q{q['id']}|sonnet|{cond}"
            print(f"[{done:2d}/{total_calls}] answer  {dim(label)} ...", end=" ", flush=True)
            try:
                answer = get_answer(client, ctx, q["question"])
            except Exception as e:  # noqa: BLE001
                print(red(f"FAIL ({e})"))
                return 2
            print(dim("→ judging ..."), end=" ", flush=True)
            try:
                result = judge_answer(client, q["question"], q["answer"], answer)
            except Exception as e:  # noqa: BLE001
                print(red(f"FAIL ({e})"))
                return 2
            v = result["verdict"]
            color = green if v == "correct" else (yellow if v == "partial" else red)
            print(color(v))
            judgments.append(
                {
                    "qid": q["id"],
                    "category": q["category"],
                    "feature": q["feature"],
                    "model": "sonnet",
                    "condition": cond,
                    "question": q["question"],
                    "answer": answer,
                    **result,
                }
            )

    # -- Compute metrics -----------------------------------------------------
    metrics = compute_metrics(judgments)
    print()
    print(bold("Results (treated condition):"))
    print(
        f"  Faithfulness   : {metrics['faithfulness']*100:.1f}%  "
        f"(gate ≥ {FAITHFULNESS_GATE*100:.0f}%)"
    )
    print(
        f"  Strict Accuracy: {metrics['strict_accuracy']*100:.1f}%  "
        f"(advisory ≥ {ACCURACY_GATE*100:.0f}%; full-25 eval is the hard gate)"
    )
    print(f"  Valid judgments: {metrics['total_valid']}/{len(SMOKE_QUESTION_IDS)}")

    # -- Per-question table --------------------------------------------------
    print()
    print(bold("Per-question breakdown:"))
    print(f"  {'Q':<4} {'Category':<12} {'Baseline':<14} {'Treated'}")
    print(f"  {'-'*4} {'-'*12} {'-'*14} {'-'*14}")
    treated_by_qid = {j["qid"]: j["verdict"] for j in judgments if j["condition"] == "treated"}
    baseline_by_qid = {j["qid"]: j["verdict"] for j in judgments if j["condition"] == "baseline"}
    for q in sorted(questions, key=lambda x: x["id"]):
        bv = baseline_by_qid.get(q["id"], "?")
        tv = treated_by_qid.get(q["id"], "?")
        bc = green if bv == "correct" else (yellow if bv == "partial" else red)
        tc = green if tv == "correct" else (yellow if tv == "partial" else red)
        print(f"  {q['id']:<4} {q['category']:<12} {bc(bv):<23} {tc(tv)}")

    # -- Threshold checks ----------------------------------------------------
    # Hard gate (drives exit code): faithfulness + valid-judgment count.
    # Strict accuracy is ADVISORY on the smoke set — with only 5 questions it
    # can only score in 20-point steps, so an 85% bar is reachable solely at a
    # perfect 5/5 and would red on single-question judge noise. The full
    # 25-question eval owns the strict-accuracy hard gate. See
    # specs/rag-gate-accuracy-baseline/design.md.
    failures: list[str] = []
    if metrics["total_valid"] < len(SMOKE_QUESTION_IDS):
        failures.append(
            f"Only {metrics['total_valid']}/{len(SMOKE_QUESTION_IDS)} valid judgments "
            f"(judge errors on {len(SMOKE_QUESTION_IDS) - metrics['total_valid']} items)"
        )
    if metrics["faithfulness"] < FAITHFULNESS_GATE:
        failures.append(
            f"Faithfulness {metrics['faithfulness']*100:.1f}% < gate {FAITHFULNESS_GATE*100:.0f}%"
        )

    advisories: list[str] = []
    if metrics["strict_accuracy"] < ACCURACY_GATE:
        advisories.append(
            f"Strict accuracy {metrics['strict_accuracy']*100:.1f}% < advisory "
            f"{ACCURACY_GATE*100:.0f}% (full-25 eval is the hard gate)"
        )

    print()
    for a in advisories:
        # ::warning:: so it surfaces in the GitHub Actions log without failing.
        print(f"::warning::{a}")
        print(f"  {yellow('!')} {a}")
    if failures:
        print(bold(red("GATE FAILED — deploy blocked:")))
        for f in failures:
            print(f"  {red('✗')} {f}")
        exit_code = 1
    else:
        print(bold(green("GATE PASSED")))
        exit_code = 0

    # -- Optional JSON output ------------------------------------------------
    output = {
        "exit_code": exit_code,
        "metrics": metrics,
        "gates": {
            "faithfulness": {
                "value": metrics["faithfulness"],
                "threshold": FAITHFULNESS_GATE,
                "passed": metrics["faithfulness"] >= FAITHFULNESS_GATE,
                "enforced": True,
            },
            "strict_accuracy": {
                "value": metrics["strict_accuracy"],
                "threshold": ACCURACY_GATE,
                "passed": metrics["strict_accuracy"] >= ACCURACY_GATE,
                "enforced": False,  # advisory on the smoke set; full-25 enforces
            },
        },
        "judgments": judgments,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(output, indent=2))
        print(dim(f"\nResults written to {args.out}"))
    print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
