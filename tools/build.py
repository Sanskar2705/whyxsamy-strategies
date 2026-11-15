"""Build the whyxsamy strategy site: content/*.html -> <slug>/index.html, plus index.html and pdf/<slug>.pdf.

    python tools/build.py            # pages only
    python tools/build.py --pdf      # pages + PDFs (headless Chrome print, uses the @media print styles)
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["rupee", "yield", "trend", "2x", "factor", "agents"]
COLORS = {"rupee": "c-saffron", "yield": "c-green", "trend": "c-gold", "2x": "c-violet", "factor": "c-blue", "agents": "c-violet"}
KEYWORD = {"rupee": "RUPEE", "yield": "YIELD", "trend": "TREND", "2x": "2X", "factor": "FACTOR", "agents": "REPORT"}
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]

DISCLAIMER = ("<b>Educational only. Not investment advice.</b> whyxsamy is not registered with SEBI as an investment adviser or "
              "research analyst. Nothing here is a recommendation to buy, sell or hold any security. Past returns do not predict future "
              "returns. Figures are from the sources listed on each page; calculated figures are labelled as such. Talk to a "
              "SEBI-registered adviser before acting.")

AI_DISCLAIMER = ("<b>Explainer, not a primary source.</b> This note summarises the public reports linked above (OpenAI, METR / Redwood "
                 "Research and press coverage of Hugging Face's post-mortem). Where sources differ, we follow the companies' own reports. "
                 "Read the originals before quoting a number.")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · whyxsamy</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Unbounded:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body><div class="wrap">
"""
FOOT = """<div class="disclaimer">{disc}</div>
<footer>@whyxsamy · a Why, answered</footer>
</div></body></html>
"""


def parse(path):
    raw = path.read_text(encoding="utf-8")
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", re.search(r"<!--meta(.*?)-->", raw, re.S).group(1), re.M))
    body = re.sub(r"<!--meta.*?-->", "", raw, flags=re.S).strip()
    return meta, body


def page(meta, body):
    slug = meta["slug"]
    top = (f'<header class="top"><a class="brand" href="../">why<span>x</span>samy</a><a class="back" href="../">All notes</a></header>\n'
           f'<div class="kicker">{html.escape(meta["kicker"])}</div>\n<h1>{html.escape(meta["title"])}</h1>\n'
           f'<div class="actions"><a class="btn" href="../pdf/{slug}.pdf" download>Download PDF</a>'
           f'<a class="btn ghost" href="../">More notes</a></div>\n')
    return (HEAD.format(title=html.escape(meta["title"]), desc=html.escape(meta["desc"]), up="../") + top + body + "\n"
            + FOOT.format(disc=AI_DISCLAIMER if meta.get("track") == "ai" else DISCLAIMER))


def index(metas):
    tiles = "".join(
        f'<a class="tile" href="{m["slug"]}/"><div class="k {COLORS[m["slug"]]}">{html.escape(m["kicker"])}</div>'
        f'<h3>{html.escape(m["title"])}</h3><p>{html.escape(m["desc"])}</p></a>' for m in metas)
    body = ('<header class="top"><a class="brand" href="./">why<span>x</span>samy</a></header>\n'
            '<div class="kicker">Strategy notes</div>\n<h1>The full breakdown behind every reel</h1>\n'
            '<p class="lede">Each note expands one video: the numbers, how the strategy works, what can go wrong, and a checklist. '
            'Every figure is sourced or marked as calculated.</p>\n'
            f'<div class="tiles">{tiles}</div>\n')
    return HEAD.format(title="Strategy notes", desc="The full breakdown behind every whyxsamy reel.", up="") + body + FOOT.format(disc=DISCLAIMER)


def main():
    metas = []
    for slug in ORDER:
        meta, body = parse(ROOT / "content" / f"{slug}.html")
        assert meta["slug"] == slug
        out = ROOT / slug / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(meta, body), encoding="utf-8")
        metas.append(meta)
    (ROOT / "index.html").write_text(index(metas), encoding="utf-8")
    print("pages:", ", ".join(ORDER))
    if "--pdf" in sys.argv:
        chrome = next(c for c in CHROME if Path(c).exists())
        (ROOT / "pdf").mkdir(exist_ok=True)
        for slug in ORDER:
            src = (ROOT / slug / "index.html").as_uri()
            dst = ROOT / "pdf" / f"{slug}.pdf"
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                            f"--print-to-pdf={dst}", src], check=True, capture_output=True)
            print("pdf:", dst.name, dst.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
