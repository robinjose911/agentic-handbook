#!/usr/bin/env python3
"""Fill every `assets/manifest.json` slot marked `placeholder` with a labeled PNG.

Deterministic: no RNG, no timestamps. A slot whose `status` is `real` is NEVER overwritten, even
with `--force` (real assets must never be clobbered by the stub generator). `--force` only re-emits
placeholders that already exist on disk.

Usage:
    python tools/stubs/make_placeholders.py [--force]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from png_writer import write_png  # noqa: E402

MANIFEST = os.path.join(REPO, "assets", "manifest.json")

# Per-kind colour scheme so placeholders are visually distinguishable at a glance.
PALETTE = {
    "banner": ((36, 52, 92), (60, 84, 140)),       # deep blue stripes
    "social": ((36, 52, 92), (60, 84, 140)),
    "diagram": ((70, 74, 82), (104, 110, 122)),    # slate-grey stripes
}
DEFAULT_PALETTE = ((80, 80, 80), (120, 120, 120))
BORDER = (245, 245, 245)
BAND = (20, 20, 24)
STRIPE_W = 28
BORDER_W = 6
BAND_H_FRAC = 0.14


def _pixel_fn(width: int, height: int, kind: str):
    dark, light = PALETTE.get(kind, DEFAULT_PALETTE)
    band_h = int(height * BAND_H_FRAC)

    def pixel(x: int, y: int):
        if x < BORDER_W or x >= width - BORDER_W or y < BORDER_W or y >= height - BORDER_W:
            return BORDER
        if y < band_h:
            return BAND
        return light if ((x + y) // STRIPE_W) % 2 == 0 else dark

    return pixel


def generate(force: bool = False) -> list[str]:
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)

    written: list[str] = []
    for slot in manifest["slots"]:
        path = os.path.join(REPO, slot["path"])
        if slot.get("status") == "real":
            # Real assets are never clobbered, even with --force.
            continue
        if os.path.exists(path) and not force:
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        w, h = int(slot["width"]), int(slot["height"])
        label = f'{slot["label"]} [{w}x{h}] PLACEHOLDER'
        write_png(
            path,
            w,
            h,
            _pixel_fn(w, h, slot.get("kind", "")),
            text_chunks=[("Title", label), ("Software", "agentic-handbook placeholder generator")],
        )
        written.append(slot["path"])
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-emit existing placeholders")
    args = parser.parse_args()
    written = generate(force=args.force)
    print(f"placeholders written: {len(written)}")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
