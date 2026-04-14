"""Run the judge pass with Opus 4.6.

For each answer in answers.json, prompt Opus with the question,
ground-truth answer, and the model's response. Opus returns a
JSON verdict {verdict, reasoning} where verdict is one of
correct | partial | hallucinated.

Resumable: re-running skips items already in judgments.json.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

REPO = pathlib.Path("/Users/patrickroebuck/attune-author")
BENCH = REPO / "benchmarks/hallucination-v0.3.6"
ANSWERS = BENCH / "answers.json"
OUT = BENCH / "judgments.json"

JUDGE_MODEL = "claude-opus-4-6"

SYSTEM = (
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

JSON_RE = re.compile(r"\{[\s\S]*\}")


def load_questions_by_id() -> dict[int, dict]:
    data = yaml.safe_load((BENCH / "questions.yaml").read_text())
    return {q["id"]: q for q in data["questions"]}


def judge(client: Anthropic, question: str, truth: str, answer: str) -> dict:
    user = (
        f"## Question\n{question}\n\n"
        f"## Ground truth\n{truth}\n\n"
        f"## Assistant's answer\n{answer}\n"
    )
    r = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=512,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = r.content[0].text
    m = JSON_RE.search(raw)
    if not m:
        return {"verdict": "error", "reasoning": f"No JSON in response: {raw[:200]}"}
    try:
        parsed = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"verdict": "error", "reasoning": f"Invalid JSON: {e}; raw={raw[:200]}"}
    verdict = parsed.get("verdict", "").lower().strip()
    if verdict not in ("correct", "partial", "hallucinated"):
        return {"verdict": "error", "reasoning": f"Unknown verdict: {verdict!r}"}
    return {
        "verdict": verdict,
        "reasoning": parsed.get("reasoning", ""),
    }


def main() -> int:
    client = Anthropic()
    if not ANSWERS.exists():
        print(f"Missing {ANSWERS}. Run run_answers.py first.", file=sys.stderr)
        return 1
    answers = json.loads(ANSWERS.read_text())
    questions = load_questions_by_id()

    judgments: dict[str, dict] = {}
    if OUT.exists():
        judgments = json.loads(OUT.read_text())

    total = len(answers)
    done = 0
    for key, entry in answers.items():
        if key in judgments:
            done += 1
            continue
        q = questions[entry["qid"]]
        try:
            verdict = judge(client, q["question"], q["answer"], entry["answer"])
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {key}: {e}", file=sys.stderr)
            return 1
        judgments[key] = {
            "qid": entry["qid"],
            "category": entry["category"],
            "feature": entry["feature"],
            "model": entry["model"],
            "condition": entry["condition"],
            **verdict,
        }
        OUT.write_text(json.dumps(judgments, indent=2))
        done += 1
        print(f"[{done}/{total}] {key} -> {verdict['verdict']}")

    print(f"\nDone: {done} judgments written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
