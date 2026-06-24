#!/usr/bin/env python3
"""Mark manifest slots `real` and sync their declared dimensions to the actual rendered PNG on disk.

Kroki/mermaid output scales to content, so the placeholder dimensions in the manifest will not match a
freshly rendered diagram. After rendering, run this to make the manifest reflect reality — the manifest
stays the single source of truth that the render-checks assert against.

Usage:
    python tools/stubs/sync_manifest.py --mark-real <slot-id> [<slot-id> ...]
    python tools/stubs/sync_manifest.py --mark-real-all-diagrams
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from png_writer import read_png_size  # noqa: E402

MANIFEST = os.path.join(REPO, "assets", "manifest.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mark-real", nargs="*", default=[], help="slot ids to mark real")
    parser.add_argument("--mark-real-all-diagrams", action="store_true",
                        help="mark every diagram-kind slot real")
    args = parser.parse_args()

    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)

    targets = set(args.mark_real)
    if args.mark_real_all_diagrams:
        targets |= {s["id"] for s in manifest["slots"] if s.get("kind") == "diagram"}
    if not targets:
        parser.error("nothing to do: pass --mark-real or --mark-real-all-diagrams")

    # A requested id that does not exist in the manifest is almost certainly a typo — fail loudly
    # rather than silently report "updated 0 slot(s)" and leave the real slot stuck as a placeholder.
    present = {s["id"] for s in manifest["slots"]}
    unknown = sorted(targets - present)
    if unknown:
        for sid in unknown:
            print(f"  ERROR: no manifest slot with id '{sid}'", file=sys.stderr)
        return 2

    updated = []
    for slot in manifest["slots"]:
        if slot["id"] not in targets:
            continue
        path = os.path.join(REPO, slot["path"])
        if not os.path.exists(path):
            print(f"  SKIP {slot['id']}: no file at {slot['path']}", file=sys.stderr)
            continue
        w, h = read_png_size(path)
        slot["width"], slot["height"], slot["status"] = w, h, "real"
        updated.append((slot["id"], w, h))

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    for sid, w, h in updated:
        print(f"  real {sid}  {w}x{h}")
    print(f"updated {len(updated)} slot(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
