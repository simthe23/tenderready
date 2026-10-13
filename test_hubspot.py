"""Checks that HubSpot injection works and is off by default. Run: python test_hubspot.py"""
import json
from pathlib import Path
import build_site

cfg_path = build_site.CONFIG
assert not cfg_path.exists(), "remove hubspot.json before running this test"

build_site.build()
assert "js.hs-scripts.com" not in Path("index.html").read_text(encoding="utf-8"), "tracking must be off without config"

cfg_path.write_text(json.dumps({"portal_id": "1234567", "form_id": "abcd1234-ab12-cd34-ef56-0123456789ab", "region": "eu1"}))
try:
    build_site.build()
    home = Path("index.html").read_text(encoding="utf-8")
    post = Path("blog/how-to-register-on-csd.html").read_text(encoding="utf-8")
    assert "//js.hs-scripts.com/1234567.js" in home and "//js.hs-scripts.com/1234567.js" in post
    assert 'region:"eu1"' in home and 'region:"eu1"' in post
    assert "HubSpot analytics cookies" in home
    assert "HUBSPOT_FORM" not in home and "HUBSPOT_TRACKING" not in post
finally:
    cfg_path.unlink()
    build_site.build()
print("OK")
