"""Build the offline research artifact from the sole canonical report-source.md.

Requires Python-Markdown (tested 3.10.3). Uses this worktree's optional isolated
.scratch/python installation, then the normal Python import path. No network,
font download, source rewriting or external rendering dependency.
"""
from pathlib import Path
import hashlib
import html
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL_DEPENDENCIES = HERE / ".scratch" / "python"
if LOCAL_DEPENDENCIES.is_dir():
    sys.path.insert(0, str(LOCAL_DEPENDENCIES))
try:
    import markdown
except ImportError as exc:
    raise SystemExit("Install Python-Markdown in the environment or research/sequence-pilot/.scratch/python; tested version 3.10.3.") from exc


def main():
    source = HERE / "report-source.md"
    raw = source.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2-3"}})
    body = md.convert(raw)
    heading = re.search(r'<h1(?:\s[^>]*)?>(.*?)</h1>', body, re.S)
    if not heading:
        raise SystemExit("Canonical source needs one H1 title")
    title_markup = heading.group(1)
    title_text = re.sub(r"<[^>]+>", "", title_markup)
    content = body[heading.end():].lstrip()
    first_section = re.search(r"<h2\b", content)
    if not first_section:
        raise SystemExit("Canonical source needs section headings")
    introduction = content[:first_section.start()]
    sections = content[first_section.start():]
    sections = sections.replace("<table>", '<div class="table-scroll" role="region" aria-label="Research comparison table; scroll horizontally on a narrow screen" tabindex="0"><table>').replace("</table>", "</table></div>")
    toc = md.toc
    digest = hashlib.sha256(raw.encode()).hexdigest()
    document = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Evidence-backed production choices, renderer alternatives and bounded experiments for a premium action webtoon pipeline.">
<meta name="color-scheme" content="light">
<meta name="report-source-sha256" content="{digest}">
<title>{html.escape(title_text)} — Anime Pipeline Research</title>
<link rel="stylesheet" href="report.css">
</head>
<body>
<a class="skip-link" href="#report-content">Skip to report</a>
<header class="site-header"><div class="header-inner">
<a class="identity" href="#top"><span class="identity-mark" aria-hidden="true">AP</span><span>Anime Pipeline<span class="identity-detail">Production research</span></span></a>
<nav class="top-links" aria-label="Project"><a href="reader/index.html">Pilot reader <span aria-hidden="true">↗</span></a><a href="../../../research/sequence-pilot/START_HERE.md">Handoff <span aria-hidden="true">↗</span></a></nav>
</div></header>
<main id="top">
<section class="hero" aria-labelledby="report-title"><div class="hero-inner">
<p class="eyebrow">Research / Direction / Next experiment</p>
<h1 id="report-title">{title_markup}</h1>
<div class="introduction">{introduction}</div>
<div class="hero-links"><a class="primary-link" href="#the-choices-worth-testing">Compare production routes <span aria-hidden="true">↓</span></a><a href="reader/index.html">Open the implementation reader <span aria-hidden="true">↗</span></a></div>
</div></section>
<div class="report-layout">
<aside class="contents" aria-label="Report navigation"><details open><summary>In this report</summary><nav aria-label="Sections">{toc}</nav><div class="contents-footer"><a href="../../../research/sequence-pilot/report-source.md">Canonical Markdown source</a><span>Offline artifact · No external runtime</span></div></details></aside>
<article id="report-content" class="report-content">{sections}</article>
</div>
</main>
<footer class="site-footer"><div><span>Anime Pipeline · Sequence pilot research</span><a href="#top">Back to top ↑</a></div><p>Source citations appear beside the claims they support. Documented capabilities, proposed experiments and observed implementation results remain distinct.</p></footer>
</body>
</html>
'''
    out = ROOT / "docs" / "research" / "sequence-pilot"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(document, encoding="utf-8")
    print(f"Built {out / 'index.html'} from source SHA256 {digest} using Python-Markdown {markdown.__version__}")


if __name__ == "__main__":
    main()
