#!/usr/bin/env python3
"""Reconcile independent visual-a / visual-b scorecards. Read-only on inputs."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

REVIEW = Path(__file__).resolve().parents[3] / "docs" / "research" / "anime-pipeline-total-review"


def main() -> int:
    a = json.loads((REVIEW / "evidence" / "visual-a" / "scorecard.json").read_text(encoding="utf-8"))
    b = json.loads((REVIEW / "evidence" / "visual-b" / "scorecard.json").read_text(encoding="utf-8"))
    rubric = json.loads((REVIEW / "common-rubric.json").read_text(encoding="utf-8"))
    pipes = rubric["pipelines_in_scope"]
    cats = rubric["categories"]
    weights = rubric["weights"]
    disagreements = []
    category_means = []
    weighted = []
    for pipe in pipes:
        cat_a, cat_b = {}, {}
        for cat, spec in cats.items():
            sa, sb = [], []
            for dim in spec["dimensions"]:
                da = a["pipelines"][pipe][cat][dim]
                db = b["pipelines"][pipe][cat][dim]
                sa.append(float(da["score"]))
                sb.append(float(db["score"]))
                delta = abs(da["score"] - db["score"])
                if delta >= 2:
                    disagreements.append(
                        {
                            "pipeline": pipe,
                            "category": cat,
                            "dimension": dim,
                            "a": da["score"],
                            "b": db["score"],
                            "delta": delta,
                            "a_confidence": da.get("confidence"),
                            "b_confidence": db.get("confidence"),
                            "a_justification": da.get("justification", "")[:240],
                            "b_justification": db.get("justification", "")[:240],
                        }
                    )
            cat_a[cat] = round(mean(sa), 2)
            cat_b[cat] = round(mean(sb), 2)
        category_means.append({"pipeline": pipe, "visual_a": cat_a, "visual_b": cat_b})
        wa = round(sum(cat_a[c] * weights[c] for c in cats), 2)
        wb = round(sum(cat_b[c] * weights[c] for c in cats), 2)
        weighted.append(
            {
                "pipeline": pipe,
                "visual_a_weighted": wa,
                "visual_b_weighted": wb,
                "midpoint": round((wa + wb) / 2, 2),
            }
        )
    out = {
        "rubric_id": rubric["id"],
        "reviewers": ["visual-a", "visual-b"],
        "disagreement_threshold": 2,
        "disagreements_ge_2": disagreements,
        "disagreement_count": len(disagreements),
        "category_means": category_means,
        "weighted_totals_after_all_categories_visible": weighted,
        "note": "Weighted totals support, not replace, diagnosis. Disagreements of 2+ points are preserved, not averaged away.",
    }
    dest = REVIEW / "evidence" / "scorecard-reconciliation.json"
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"disagreement_count": len(disagreements), "weighted": weighted}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
