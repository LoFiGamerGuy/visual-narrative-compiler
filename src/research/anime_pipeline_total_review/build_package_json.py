#!/usr/bin/env python3
"""Build machine-readable package JSON from specialist evidence. Deterministic."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

REVIEW = Path(__file__).resolve().parents[3] / "docs" / "research" / "anime-pipeline-total-review"
EV = REVIEW / "evidence"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    a = load(EV / "visual-a" / "scorecard.json")
    b = load(EV / "visual-b" / "scorecard.json")
    rec = load(EV / "scorecard-reconciliation.json")
    rubric = load(REVIEW / "common-rubric.json")
    scorecards = {
        "schema": "PipelineScorecards/1.0",
        "rubric_id": rubric["id"],
        "frozen_at": rubric["frozen_at"],
        "reviewers": ["visual-a", "visual-b"],
        "independent": True,
        "visual_a": a,
        "visual_b": b,
        "reconciliation": rec,
        "lead_note": (
            "Weighted totals computed only after all categories were scored. "
            "25 dimensions differ by 2+ points; they are preserved. "
            "Visual B scored North Garden lettering/system dimensions 2–3 despite no balloons on inspected pages; "
            "Visual A scored those 0. Lead treats A's zeros as the better-supported observation for absent lettering. "
            "Visual B is more generous on Ember volume vertical pacing/value (4 vs 2). Minority preserved."
        ),
    }
    (REVIEW / "pipeline-scorecards.json").write_text(json.dumps(scorecards, indent=2) + "\n", encoding="utf-8")

    citations = []
    for src in (
        EV / "industry-citations.json",
        EV / "economics-sources.json",
    ):
        if not src.exists():
            continue
        data = load(src)
        if isinstance(data, list):
            citations.extend(data)
        elif isinstance(data, dict):
            if "citations" in data:
                citations.extend(data["citations"])
            elif "claims" in data:
                citations.extend(data["claims"])
            else:
                citations.append({"id": src.name, "payload": data, "source_type": "bundle"})
    citations.append(
        {
            "id": "usco-ai-part2-2025",
            "title": "Copyright and Artificial Intelligence, Part 2: Copyrightability",
            "publisher_author": "U.S. Copyright Office",
            "url": "https://www.copyright.gov/ai/",
            "publication_date": "2025-01-29",
            "access_date": "2026-09-06",
            "source_type": "official",
            "claim_supported": "Outputs of generative AI are copyrightable only where a human author determined sufficient expressive elements; prompts alone are insufficient; AI-assisted human works remain protectable.",
            "authority_rating": "primary/official",
        }
    )
    citations.append(
        {
            "id": "webtoon-canvas-file-size-2026",
            "title": "File Size Overview / Designing Series & Episode Thumbnails",
            "publisher_author": "WEBTOON CANVAS Zendesk",
            "url": "https://webtooncanvas.zendesk.com/hc/en-us/articles/32913712749588",
            "publication_date": "2026-07-22",
            "access_date": "2026-09-06",
            "source_type": "official",
            "claim_supported": "Canvas episode images auto-slice/optimize above 800x1280; max 2MB per sliced image; 20MB/100 images; JPG/PNG; series thumbs 1080x1080 and 1080x1920.",
            "authority_rating": "primary/official",
        }
    )
    citations.append(
        {
            "id": "tapas-episode-publish",
            "title": "Series Basics: How to publish a comic episode on Tapas",
            "publisher_author": "Tapas Help Center",
            "url": "https://help.tapas.io/hc/en-us/articles/1260802028970-Series-Basics-How-to-publish-a-comic-episode-on-Tapas",
            "publication_date": None,
            "access_date": "2026-09-06",
            "source_type": "official",
            "claim_supported": "Page size 940px wide, no height limit, PNG/JPG/GIF, 10MB; episode thumbnail 300x300 under 2MB; desktop and mobile preview required before publish.",
            "authority_rating": "primary/official",
        }
    )
    citations.append(
        {
            "id": "tog-webtoon-official",
            "title": "Tower of God",
            "publisher_author": "SIU / WEBTOON",
            "url": "https://www.webtoons.com/en/fantasy/tower-of-god/list?title_no=95",
            "publication_date": None,
            "access_date": "2026-09-06",
            "source_type": "official licensed listing",
            "claim_supported": "Official English vertical-scroll listing; hook copy 'What do you desire?'; 1.3B views / 4.2M subscribers observed on access date; Season 3 finale listed Feb 23, 2025.",
            "authority_rating": "primary/official",
        }
    )
    citations.append(
        {
            "id": "solo-leveling-yen-press",
            "title": "Solo Leveling (comic) series",
            "publisher_author": "Chugong / DUBU(REDICE) / DISCIPLES / Ize Press / Yen Press",
            "url": "https://yenpress.com/series/solo-leveling-comic",
            "publication_date": "2021-03-02",
            "access_date": "2026-09-06",
            "source_type": "official licensed listing",
            "claim_supported": "Licensed English print comic; named letterer Abigail Blackman; artist credit DUBU then DISCIPLES(REDICE STUDIO).",
            "authority_rating": "primary/official",
        }
    )
    citations.append(
        {
            "id": "ann-korea-ai-law-2026",
            "title": "South Korea's New AI Law Raises Questions for Webtoon Creators, Platforms",
            "publisher_author": "Anime News Network / Wonhee Cho",
            "url": "https://www.animenewsnetwork.com/news/2026-01-24/south-korea-new-ai-law-raises-questions-for-webtoon-creators-platforms/.233383",
            "publication_date": "2026-01-24",
            "access_date": "2026-09-06",
            "source_type": "reputable trade",
            "claim_supported": "Korean AI law requires companies that develop or provide AI models/services to disclose AI-generated content; watermarking; platforms serving Korean users may need workflow/UI notices.",
            "authority_rating": "reputable trade",
        }
    )
    ledger = {
        "schema": "CitationLedger/1.0",
        "access_date": "2026-09-06",
        "count": len(citations),
        "citations": citations,
    }
    (REVIEW / "citation-ledger.json").write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print("wrote pipeline-scorecards.json and citation-ledger.json", len(citations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
