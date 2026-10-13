"""Rebuild the whole site: copy the landing page, build the blog, inject HubSpot.

Run: python build_site.py

HubSpot is switched on by creating hubspot.json next to this file:
    {"portal_id": "12345678", "form_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "region": "na1"}
(region is "na1" for most accounts, "eu1" for EU data centres; the embed code in HubSpot shows it.)
Without that file the site builds with no tracking and no form.
"""
import json
import re
import shutil
from pathlib import Path

import build_blog

ROOT = Path(__file__).parent
LANDING_SRC = ROOT.parent / "amanani docs" / "eskom folder" / "procurement-starter-kit" / "landing.html"
CONFIG = ROOT / "hubspot.json"

PRIVACY_TRACKING = (
    '<p class="disclaimer" id="privacy"><b>Privacy:</b> We collect only the name and email address you give us '
    "when you buy, join the QuoteForge waitlist or request the free checklist. Purchases are processed through "
    "Gumroad; checklist and waitlist sign-ups are stored in HubSpot. We use your details to deliver what you asked "
    "for and to send tender tips and product updates, never sell or share them, and you can unsubscribe in any "
    "email or ask us to access or delete your data by emailing Simthembiledotwana2@gmail.com (POPIA). "
    "This site also uses HubSpot analytics cookies to count visits and see which pages help; you can decline them "
    "in the cookie notice or your browser settings.</p>"
)


def load_config():
    if not CONFIG.exists():
        return None
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    for key in ("portal_id", "form_id"):
        if not re.fullmatch(r"[0-9a-fA-F-]+", str(cfg.get(key, ""))):
            raise SystemExit(f"hubspot.json: bad {key}")
    cfg.setdefault("region", "na1")
    if cfg["region"] not in ("na1", "eu1"):
        raise SystemExit("hubspot.json: region must be na1 or eu1")
    return cfg


def host(cfg, base):
    """EU accounts load scripts from js-eu1.* hosts; na1 uses js.*"""
    return f"js-{cfg['region']}.{base}" if cfg["region"] == "eu1" else f"js.{base}"


def tracking(cfg):
    return f'<script type="text/javascript" id="hs-script-loader" async defer src="//{host(cfg, "hs-scripts.com")}/{cfg["portal_id"]}.js"></script>'


def form_block(cfg, blog=False):
    embed = (
        f'<script charset="utf-8" type="text/javascript" src="//{host(cfg, "hsforms.net")}/forms/embed/v2.js"></script>\n'
        f'<script>hbspt.forms.create({{region:"{cfg["region"]}",portalId:"{cfg["portal_id"]}",formId:"{cfg["form_id"]}"}});</script>'
    )
    head = (
        '<h2>Free 7-point pre-submission RFQ check</h2>\n'
        '<p>Run it before every quote goes out. Enter your details and we will email you the one-page PDF.</p>'
    )
    if blog:
        return f'<div class="cta">{head}\n{embed}</div>'
    return (
        '<section id="free-checklist"><div class="wrap">'
        '<div class="section-head"><p class="eyebrow">Free download</p>' + head.replace("<h2>", "<h2>", 1) + "</div>"
        f"{embed}</div></section>"
    )


def inject(cfg):
    for f in ROOT.rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        text = text.replace("<!-- HUBSPOT_TRACKING -->", tracking(cfg))
        text = text.replace("<!-- HUBSPOT_FORM -->", form_block(cfg, blog=f.parent.name == "blog"))
        text = re.sub(r'<p class="disclaimer" id="privacy">.*?</p>', PRIVACY_TRACKING, text, flags=re.S)
        f.write_text(text, encoding="utf-8")


def build():
    shutil.copyfile(LANDING_SRC, ROOT / "index.html")
    build_blog.build()
    cfg = load_config()
    if cfg:
        inject(cfg)
    return cfg


if __name__ == "__main__":
    print("HubSpot:", "ON" if build() else "off (no hubspot.json)")
