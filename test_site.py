"""Link and structure checks for the built site. Run: python test_site.py"""
import re, sys
from pathlib import Path

root = Path(__file__).parent
bad = []
for f in list(root.rglob("*.html")):
    text = f.read_text(encoding="utf-8")
    if not text.lstrip().lower().startswith("<!doctype html>"):
        bad.append(f"{f.name}: no doctype")
    if "63029788502" in text:
        bad.append(f"{f.name}: bank number")
    for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
        if re.match(r"(https?:|mailto:|tel:)", href):
            continue
        if not (f.parent / href).resolve().exists():
            bad.append(f"{f.name}: broken link {href}")
if not (root / "sitemap.xml").exists() or not (root / "robots.txt").exists():
    bad.append("sitemap/robots missing")
print("FAIL:\n- " + "\n- ".join(bad) if bad else "OK")
sys.exit(1 if bad else 0)
