#!/usr/bin/env python3
"""Rebuild data.json from an export of the Mardi Gras 2027 Board.

Usage: python3 scripts/sync_board.py <items_dir>

<items_dir> holds one <id>.json file per board item (as saved by
ArtifactData list with out_dir). Only the fields the glasses view uses
are kept; "next" falls back to the item's "notes". data.json is left
untouched when nothing but the timestamp would change.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data.json"


def convert(item_id, d):
    out = {
        "id": item_id,
        "title": d.get("title", ""),
        "category": d.get("category", "Other"),
        "status": d.get("status", "todo"),
        "due": d.get("due"),
    }
    nxt = d.get("next") or d.get("notes")
    if nxt:
        out["next"] = nxt
    return out


def main():
    src = Path(sys.argv[1])
    files = sorted(src.glob("*.json"))
    if not files:
        sys.exit(f"no item files in {src}")
    items = [convert(f.stem, json.loads(f.read_text())) for f in files]
    items.sort(key=lambda i: (i["due"] or "9999", i["title"]))

    if OUT.exists() and json.loads(OUT.read_text()).get("items") == items:
        print("data.json already up to date")
        return
    now = datetime.now(ZoneInfo("America/Chicago")).isoformat(timespec="seconds")
    OUT.write_text(json.dumps({"updated": now, "items": items}, indent=1, ensure_ascii=False) + "\n")
    print(f"data.json updated with {len(items)} items")


if __name__ == "__main__":
    main()
