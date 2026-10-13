"""Build blog pages, sitemap and robots.txt. Run: python build_blog.py"""
import html
import json
import re
from pathlib import Path

from posts import POSTS, REVIEWED

ROOT = Path(__file__).parent
BASE = "https://simthe23.github.io/tenderready/"
GUMROAD = {
    "starter": ("Starter", "R200", "https://pikachu29.gumroad.com/l/lakow"),
    "core": ("Core", "R497", "https://pikachu29.gumroad.com/l/amirc"),
}
ISO_DATE = "2026-10-13"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root{--ink:#17233a;--ink-soft:#4b5568;--paper:#ece5d2;--paper-alt:#f7f3e8;--paper-deep:#ddd3b5;--stamp:#a3402c;--stamp-dark:#7c2f21;--line:#c9bfa0;--line-strong:#a89d7c;
--font-display:'Fraunces',Georgia,serif;--font-body:'IBM Plex Sans',-apple-system,Segoe UI,sans-serif;--font-mono:'IBM Plex Mono','Courier New',monospace;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#ece5d2;--ink-soft:#b9b096;--paper:#15130f;--paper-alt:#1c1a15;--paper-deep:#0e0d0a;--stamp:#d3654a;--stamp-dark:#e8836a;--line:#3a362a;--line-strong:#4d4736;}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font-body);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--stamp)}a:hover{color:var(--stamp-dark)}
.wrap{max-width:720px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1.5px solid var(--line-strong);padding:16px 0}
.head-inner{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.wordmark{font-family:var(--font-mono);font-weight:600;font-size:13px;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;color:var(--ink)}
.wordmark span{color:var(--stamp)}
nav a{font-family:var(--font-mono);font-size:12px;margin-left:16px;color:var(--ink-soft)}
.eyebrow{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--stamp);margin:36px 0 8px}
h1{font-family:var(--font-display);font-weight:600;font-size:clamp(1.7rem,4.5vw,2.45rem);line-height:1.15;margin:0 0 12px;text-wrap:balance}
h2{font-family:var(--font-display);font-weight:600;font-size:1.4rem;margin:34px 0 8px;text-wrap:balance}
.meta{font-family:var(--font-mono);font-size:12px;color:var(--ink-soft);margin:0 0 24px}
article p,article li{font-size:1.02rem}
article ul,article ol{padding-left:22px}
article li{margin:6px 0}
table{border-collapse:collapse;width:100%;font-size:.92rem;margin:14px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line-strong);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--paper-alt);font-family:var(--font-mono);font-size:12px}
.cta{border:1.5px solid var(--ink);background:var(--paper-alt);padding:22px 20px;margin:40px 0}
.cta p{margin:0 0 12px}
.cta .btn{display:inline-block;background:var(--stamp);color:#fdf8ec;font-family:var(--font-mono);font-weight:600;font-size:13px;padding:12px 20px;text-decoration:none;border-radius:2px}
.cta .btn:hover{background:var(--stamp-dark);color:#fdf8ec}
.more{padding:0;list-style:none}
.more li{border-bottom:1px dashed var(--line);padding-bottom:10px}
.card{display:block;border:1px solid var(--line-strong);background:var(--paper-alt);padding:16px 18px;margin:12px 0;text-decoration:none;color:var(--ink)}
.card b{font-family:var(--font-display);font-size:1.12rem;display:block;margin-bottom:4px}
.card span{color:var(--ink-soft);font-size:.92rem}
.disclaimer{font-family:var(--font-mono);font-size:11px;color:var(--ink-soft);border-top:1px dashed var(--line-strong);padding-top:16px;margin-top:32px}
footer{background:var(--paper-deep);border-top:1.5px solid var(--ink);padding:26px 0 36px;margin-top:48px;font-family:var(--font-mono);font-size:11.5px;color:var(--ink-soft)}
"""


def page(title, desc, canonical, body, extra_head=""):
    """Pages sit in blog/, so shared assets and the home page are one level up."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="style.css">
{extra_head}</head>
<body>
<header class="site"><div class="wrap head-inner">
<a class="wordmark" href="../index.html">Amanani <span>&middot;</span> TenderReady</a>
<nav><a href="index.html">Guides</a><a href="../index.html#pricing">Pricing</a></nav>
</div></header>
{body}
<footer><div class="wrap">Amanani (Pty) Ltd &middot; Reg 2019/045663/07 &middot; CSD MAAA0761124 &middot; East London, Eastern Cape<br>&copy; 2026 Amanani (Pty) Ltd. <a href="../index.html">TenderReady</a></div></footer>
</body>
</html>
"""


def utm(url, slug):
    return f"{url}?utm_source=blog&utm_medium=article&utm_campaign={slug}"


def render_post(p):
    name, price, link = GUMROAD[p["tier"]]
    url = f"{BASE}blog/{p['slug']}.html"
    others = [q for q in POSTS if q["slug"] != p["slug"]][:3]
    more = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["short"])}</a></li>' for q in others)
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": p["title"],
        "description": p["description"], "datePublished": ISO_DATE, "dateModified": ISO_DATE,
        "author": {"@type": "Organization", "name": "Amanani (Pty) Ltd"},
        "mainEntityOfPage": url,
    })
    body = f"""<main class="wrap"><article>
<p class="eyebrow">Guide</p>
<h1>{html.escape(p["title"])}</h1>
<p class="meta">By Amanani (Pty) Ltd &middot; Last reviewed {REVIEWED}</p>
{p["body"]}
<div class="cta">
<p><b>Stop losing quotes before price is compared.</b> TenderReady is a set of AI prompts and compliance checklists built from real UFH, WSU and BCMM quotes. {name} tier is {price}, once-off.</p>
<a class="btn" href="{utm(link, p['slug'])}">Get {name} &mdash; {price}</a>
</div>
<!-- HUBSPOT_FORM: embed the free checklist sign-up form here once it exists -->
<h2>More guides</h2>
<ul class="more">{more}</ul>
<p class="disclaimer">Not legal, tax or investment advice. Procurement rules and thresholds change: always verify against www.csd.gov.za, National Treasury and the issuing entity's own RFQ conditions before you submit a quote.</p>
</article></main>"""
    return page(p["title"], p["description"], url, body,
                extra_head=f'<script type="application/ld+json">{ld}</script>\n')


def render_index():
    cards = "".join(
        f'<a class="card" href="{p["slug"]}.html"><b>{html.escape(p["short"])}</b><span>{html.escape(p["description"])}</span></a>'
        for p in POSTS)
    body = f"""<main class="wrap">
<p class="eyebrow">Guides</p>
<h1>Government RFQ guides for South African SMMEs</h1>
<p class="meta">Plain-language guides from a CSD-registered supplier who bids UFH, WSU and BCMM RFQs.</p>
{cards}
<p class="disclaimer">Not legal, tax or investment advice. Verify requirements at www.csd.gov.za and with the issuing entity.</p>
</main>"""
    return page("Government RFQ Guides for South African SMMEs | TenderReady",
                "Guides on CSD registration, proof of address, RFQs, pricing government quotes, RFQ vs tender and B-BBEE affidavits.",
                f"{BASE}blog/", body)


def build():
    blog = ROOT / "blog"
    blog.mkdir(exist_ok=True)
    (blog / "style.css").write_text(CSS, encoding="utf-8")
    for p in POSTS:
        (blog / f"{p['slug']}.html").write_text(render_post(p), encoding="utf-8")
    (blog / "index.html").write_text(render_index(), encoding="utf-8")
    urls = [BASE, f"{BASE}blog/"] + [f"{BASE}blog/{p['slug']}.html" for p in POSTS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{u}</loc><lastmod>{ISO_DATE}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")


def words(fragment):
    return len(re.sub(r"<[^>]+>", " ", fragment).split())


if __name__ == "__main__":
    build()
    for p in POSTS:
        print(f"{words(p['body']):5d} words  {p['slug']}")
