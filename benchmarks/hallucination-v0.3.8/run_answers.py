"""Run the answer pass: each question x each model x each condition.

Baseline condition:  README + file tree only.
Treated condition:   baseline + the attune-help `lookup(depth=reference)`
                     result for the question's feature.

Temperature = 0, max_tokens = 1024. Resumable — re-running skips
items already in answers.json.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

REPO = pathlib.Path("/Users/patrickroebuck/attune-author")
BENCH = REPO / "benchmarks/hallucination-v0.3.8"
OUT = BENCH / "answers.json"
CTX = BENCH / "contexts.json"

MODELS = [("sonnet", "claude-sonnet-4-6"), ("opus", "claude-opus-4-6")]

SYSTEM = (
    "You are a developer assistant answering questions about the "
    "attune-author Python package. Use only the repository context "
    "provided. Be concise and specific. If a claim requires a detail "
    "you can verify from the context, give the exact detail; if you "
    "cannot verify it, say so rather than guessing."
)


def load_questions() -> list[dict]:
    data = yaml.safe_load((BENCH / "questions.yaml").read_text())
    return data["questions"]


def build_baseline_context() -> str:
    readme = (REPO / "README.md").read_text()
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    files = "\n".join(sorted(r.stdout.splitlines()))
    return (
        "# Repository: attune-author\n\n"
        "## File tree (tracked files)\n\n"
        f"```\n{files}\n```\n\n"
        "## README.md\n\n"
        f"{readme}"
    )


def build_treated_context(baseline: str, feature: str) -> str:
    ref = REPO / f".help/templates/{feature}/reference.md"
    if not ref.exists():
        raise FileNotFoundError(f"Missing reference template: {ref}")
    body = ref.read_text()
    return (
        baseline
        + "\n\n---\n\n"
        + f"## attune-help lookup result: feature={feature!r}, depth='reference'\n\n"
        + body
    )


def save_contexts(baseline: str, treated_by_feature: dict[str, str]) -> None:
    CTX.write_text(
        json.dumps(
            {
                "baseline": baseline,
                "treated_by_feature": treated_by_feature,
            },
            indent=2,
        )
    )


def ask(client: Anthropic, model_id: str, context: str, question: str) -> str:
    user = f"{context}\n\n---\n\n# Question\n\n{question}"
    r = client.messages.create(
        model=model_id,
        max_tokens=1024,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text


def main() -> int:
    client = Anthropic()
    questions = load_questions()

    baseline = build_baseline_context()
    features = sorted({q["feature"] for q in questions})
    treated_by_feature = {f: build_treated_context(baseline, f) for f in features}
    save_contexts(baseline, treated_by_feature)

    results: dict[str, dict] = {}
    if OUT.exists():
        results = json.loads(OUT.read_text())

    total = len(questions) * len(MODELS) * 2
    done = 0
    for q in questions:
        qid = str(q["id"])
        for model_short, model_id in MODELS:
            for cond in ("baseline", "treated"):
                key = f"q{qid}|{model_short}|{cond}"
                if key in results:
                    done += 1
                    continue
                ctx = baseline if cond == "baseline" else treated_by_feature[q["feature"]]
                try:
                    text = ask(client, model_id, ctx, q["question"])
                except Exception as e:  # noqa: BLE001
                    print(f"[FAIL] {key}: {e}", file=sys.stderr)
                    return 1
                results[key] = {
                    "qid": q["id"],
                    "category": q["category"],
                    "feature": q["feature"],
                    "model": model_short,
                    "condition": cond,
                    "question": q["question"],
                    "answer": text,
                }
                OUT.write_text(json.dumps(results, indent=2))
                done += 1
                print(f"[{done}/{total}] {key}")

    print(f"\nDone: {done} answers written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
