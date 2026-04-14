"""Tabulate results and run McNemar's test on paired baseline/treated.

Reads judgments.json. Prints:
- Per-model accuracy% and hallucination% in each condition
- Paired delta (treated - baseline)
- McNemar exact test on correct/incorrect outcomes
- Per-category breakdown
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from math import comb

BENCH = pathlib.Path(__file__).parent
JUDGMENTS = BENCH / "judgments.json"


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar on discordant pairs b vs c.

    b = improved (baseline incorrect, treated correct)
    c = regressed (baseline correct, treated incorrect)
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p_tail = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2 * p_tail)


def fmt_pct(x: float, n: int) -> str:
    return f"{100*x/n:5.1f}% ({x}/{n})" if n else "  n/a"


def main() -> None:
    data = json.loads(JUDGMENTS.read_text())

    by_model_cond: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    paired: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    by_cat: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for key, j in data.items():
        model = j["model"]
        cond = j["condition"]
        v = j["verdict"]
        by_model_cond[(model, cond)][v] += 1
        by_model_cond[(model, cond)]["total"] += 1
        paired[(model, j["qid"])][cond] = v
        by_cat[(model, j["category"], cond)][v] += 1
        by_cat[(model, j["category"], cond)]["total"] += 1

    print("=" * 72)
    print("  attune-help hallucination benchmark — v0.3.6 / attune-author")
    print("=" * 72)

    for model in ("sonnet", "opus"):
        print(f"\n## Model: {model}")
        print(f"{'Metric':<20}{'Baseline':<28}{'Treated':<28}{'Δ':<10}")
        print("-" * 86)
        for verdict in ("correct", "partial", "hallucinated"):
            b = by_model_cond[(model, "baseline")]
            t = by_model_cond[(model, "treated")]
            bn, tn = b["total"], t["total"]
            bval, tval = b[verdict], t[verdict]
            delta_pp = (100 * tval / tn) - (100 * bval / bn) if bn and tn else 0
            print(f"{verdict:<20}{fmt_pct(bval, bn):<28}{fmt_pct(tval, tn):<28}{delta_pp:+6.1f}pp")

        # McNemar on correct-vs-not-correct
        improved = 0  # baseline not-correct, treated correct
        regressed = 0  # baseline correct, treated not-correct
        concordant_correct = 0
        concordant_wrong = 0
        for (m, qid), outcomes in paired.items():
            if m != model:
                continue
            b_ok = outcomes.get("baseline") == "correct"
            t_ok = outcomes.get("treated") == "correct"
            if b_ok and t_ok:
                concordant_correct += 1
            elif not b_ok and not t_ok:
                concordant_wrong += 1
            elif not b_ok and t_ok:
                improved += 1
            else:
                regressed += 1
        p = mcnemar_exact(improved, regressed)
        print(
            f"\n  Paired outcomes (correct vs not): "
            f"both correct={concordant_correct}, both wrong={concordant_wrong}, "
            f"improved={improved}, regressed={regressed}"
        )
        print(f"  McNemar exact two-sided p = {p:.4f}")

    # Per-category roll-up
    print("\n\n## Per-category accuracy (correct only)")
    cats = sorted({c for (_, c, _) in by_cat})
    print(f"{'Category':<14}{'Model':<10}{'Baseline':<28}{'Treated':<28}")
    print("-" * 80)
    for model in ("sonnet", "opus"):
        for cat in cats:
            b = by_cat[(model, cat, "baseline")]
            t = by_cat[(model, cat, "treated")]
            bs = fmt_pct(b.get("correct", 0), b.get("total", 0))
            ts = fmt_pct(t.get("correct", 0), t.get("total", 0))
            print(f"{cat:<14}{model:<10}{bs:<28}{ts:<28}")

    print()


if __name__ == "__main__":
    main()
