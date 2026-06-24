#!/usr/bin/env python3
"""Generate the brand assets — assets/banner.png (wide hero card) and assets/social-preview.png (the
OG/social card, which carries the configured socialPreviewText) — from repo.config.json, using the
pure-Python PNG writer + 5x7 font (no image deps). Deterministic. After generating, flip the manifest
slots to `real`.

These are functional brand cards; the final polished art is Robin's to design (proposal §10). Run:

    python tools/stubs/make_brand.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from png_writer import write_png  # noqa: E402
import font5x7  # noqa: E402

WIDTH, HEIGHT = 1280, 640
BG_TOP = (26, 22, 51)
BG_BOTTOM = (14, 30, 58)
WHITE = (245, 245, 248)
SUBTLE = (170, 178, 200)
ACCENTS = [
    (139, 111, 214), (63, 167, 214), (225, 171, 47), (46, 196, 182),
    (225, 90, 79), (91, 141, 239), (95, 184, 122),
]

# Helvetica/font has no em-dash or curly quotes; normalize to the supported ASCII glyphs.
_PUNCT = {"—": "-", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"', "·": "-", "…": "...", "→": "->"}


def _norm(s: str) -> str:
    for u, a in _PUNCT.items():
        s = s.replace(u, a)
    return s


def _config():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _set(buf, x, y, rgb):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = rgb


def _draw_text(buf, text, x, y, scale, color, spacing=1):
    for px, py in font5x7.text_pixels(_norm(text), scale, spacing):
        _set(buf, x + px, y + py, color)


def _draw_centered(buf, text, y, scale, color, spacing=1):
    tw = font5x7.text_width(_norm(text), scale, spacing)
    _draw_text(buf, text, (WIDTH - tw) // 2, y, scale, color, spacing)


def _wrap(text: str, scale: int, max_w: int, spacing=1) -> list[str]:
    words, out, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font5x7.text_width(trial, scale, spacing) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def _background(buf):
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        bg = tuple(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        row = (y * WIDTH) * 3
        for x in range(WIDTH):
            i = row + x * 3
            buf[i], buf[i + 1], buf[i + 2] = bg


def _render(cfg: dict, kind: str) -> bytearray:
    buf = bytearray(WIDTH * HEIGHT * 3)
    _background(buf)
    surfaces = cfg["mnemonic"]["surfaces"]
    surface_names = [s["name"].upper() for s in surfaces]

    _draw_centered(buf, cfg["repoName"].upper(), 64, 9, WHITE)

    if kind == "social":
        # The OG card carries the configured social copy (distinct from the banner's tagline).
        for i, line in enumerate(_wrap(cfg["socialPreviewText"].upper(), 3, WIDTH - 160)):
            _draw_centered(buf, line, 200 + i * 40, 3, SUBTLE)
    else:
        _draw_centered(buf, "THE CPTO'S PLAYBOOK FOR AGENTIC AI", 210, 3, SUBTLE)

    col_w = WIDTH // 7
    for idx, s in enumerate(surfaces):
        color = ACCENTS[idx % len(ACCENTS)]
        cx = idx * col_w + col_w // 2
        lw = font5x7.text_width(s["letter"], 8)
        _draw_text(buf, s["letter"], cx - lw // 2, 330, 8, color)
        name = s["name"].upper()
        nw = font5x7.text_width(name, 2)
        _draw_text(buf, name, cx - nw // 2, 420, 2, SUBTLE)

    # Footer derived from config (not hand-typed), so it can't drift from the canonical mnemonic.
    _draw_centered(buf, " ".join(surface_names), 510, 2, SUBTLE)
    _draw_centered(buf, f"BY {cfg['owner'].upper()}", 575, 2, SUBTLE)
    return buf


def _write(path: str, buf: bytearray, cfg: dict, description: str):
    def pixel(x, y):
        i = (y * WIDTH + x) * 3
        return buf[i], buf[i + 1], buf[i + 2]

    write_png(
        path, WIDTH, HEIGHT, pixel,
        text_chunks=[
            ("Title", cfg["repoName"]),
            ("Description", _norm(description)),
            ("Mnemonic", "AGENTIC: " + " ".join(s["name"] for s in cfg["mnemonic"]["surfaces"])),
        ],
    )


def main() -> int:
    cfg = _config()
    for rel, kind, desc in (
        ("assets/banner.png", "banner", cfg["tagline"]),
        ("assets/social-preview.png", "social", cfg["socialPreviewText"]),
    ):
        path = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _write(path, _render(cfg, kind), cfg, desc)
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
