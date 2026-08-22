"""Validate and package Breathable AI for the Chrome Web Store / AMO.

    python tools/build.py               # validate, then write dist/breathable-ai-<version>.zip
    python tools/build.py --check-copy  # also check store listing character limits
"""
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# Only these ship. Everything else in the repo is source, docs, or store art.
PAYLOAD = [
    "manifest.json",
    "content.js",
    "popup.html",
    "popup.js",
    "breath.mp3",
    "icons/icon16.png",
    "icons/icon32.png",
    "icons/icon48.png",
    "icons/icon128.png",
]

errors, warnings = [], []


def png_size(path):
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def validate():
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for rel in PAYLOAD:
        if not (ROOT / rel).exists():
            errors.append(f"missing payload file: {rel}")

    # every icon the manifest names must exist at exactly the size it claims
    for block, label in ((manifest.get("icons", {}), "icons"),
                         (manifest.get("action", {}).get("default_icon", {}), "action.default_icon")):
        for size, rel in block.items():
            path = ROOT / rel
            if not path.exists():
                errors.append(f"{label}: {rel} does not exist")
                continue
            actual = png_size(path)
            if actual is None:
                errors.append(f"{label}: {rel} is not a valid PNG")
            elif actual != (int(size), int(size)):
                errors.append(f"{label}: {rel} is {actual[0]}x{actual[1]}, manifest declares {size}")

    # content script and web-accessible resource scopes must line up, or the
    # mp3 fails to load on a site the script actually runs on
    cs_hosts = {m.split("/")[2] for m in manifest["content_scripts"][0]["matches"]}
    war_hosts = {m.split("/")[2] for m in manifest["web_accessible_resources"][0]["matches"]}
    for host in sorted(cs_hosts - war_hosts):
        errors.append(f"{host} runs the content script but cannot load breath.mp3 "
                      f"(missing from web_accessible_resources)")
    for host in sorted(war_hosts - cs_hosts):
        warnings.append(f"{host} is web-accessible but runs no content script")

    for res in manifest["web_accessible_resources"][0]["resources"]:
        if not (ROOT / res).exists():
            errors.append(f"web_accessible_resources names a missing file: {res}")

    if not re.fullmatch(r"\d+(\.\d+){0,3}", manifest["version"]):
        errors.append(f"invalid version string: {manifest['version']}")
    if len(manifest["description"]) > 132:
        errors.append(f"manifest description is {len(manifest['description'])} chars (max 132)")
    if "<all_urls>" in json.dumps(manifest):
        warnings.append("manifest still contains <all_urls>; expect a slower store review")

    return manifest


def check_copy():
    listing = (ROOT / "store" / "STORE-LISTING.md").read_text(encoding="utf-8")
    for label, pattern, limit in (
        ("summary", r"\*\(max 132 characters\)\*\n```\n(.*?)\n```", 132),
        ("description", r"\*\(max 16,000 characters\)\*\n\n```\n(.*?)\n```", 16000),
    ):
        match = re.search(pattern, listing, re.S)
        if not match:
            errors.append(f"could not find {label} block in STORE-LISTING.md")
            continue
        n = len(match.group(1))
        print(f"  {label}: {n} / {limit} chars")
        if n > limit:
            errors.append(f"{label} is {n} chars, over the {limit} limit")


def package(manifest):
    DIST.mkdir(exist_ok=True)
    out = DIST / f"breathable-ai-{manifest['version']}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in PAYLOAD:
            z.write(ROOT / rel, rel)
    return out


if __name__ == "__main__":
    manifest = validate()
    if "--check-copy" in sys.argv:
        print("listing copy:")
        check_copy()

    for w in warnings:
        print(f"  warning: {w}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)

    out = package(manifest)
    kb = out.stat().st_size / 1024
    print(f"\nvalidated {len(PAYLOAD)} files, {len(manifest['content_scripts'][0]['matches'])} host matches")
    print(f"wrote {out.relative_to(ROOT)}  ({kb:.1f} KB)")
