"""Validator: every Mermaid source rendered to a real PNG and the manifest reflects it (Stage 1.2)."""
import json
import os
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "stubs"))
from png_writer import read_png_size as _png_size  # noqa: E402

SRC = os.path.join(REPO, "assets", "diagrams", "src")
MANIFEST = os.path.join(REPO, "assets", "manifest.json")


def _diagram_slots():
    with open(MANIFEST, encoding="utf-8") as fh:
        return [s for s in json.load(fh)["slots"] if s["kind"] == "diagram"]


def test_every_source_has_a_rendered_png():
    sources = {f[:-4] for f in os.listdir(SRC) if f.endswith(".mmd")}
    for name in sources:
        png = os.path.join(REPO, "assets", "diagrams", f"{name}.png")
        assert os.path.exists(png), f"{name}.mmd has no rendered {name}.png"


def test_all_fifteen_diagram_slots_are_real():
    slots = _diagram_slots()
    assert len(slots) == 15
    placeholders = [s["id"] for s in slots if s["status"] != "real"]
    assert placeholders == [], f"diagram slots still placeholder: {placeholders}"


@pytest.mark.parametrize("slot", _diagram_slots(), ids=lambda s: s["id"])
def test_rendered_png_matches_manifest_dimensions(slot):
    path = os.path.join(REPO, slot["path"])
    assert os.path.exists(path), f"{slot['id']}: missing {slot['path']}"
    w, h = _png_size(path)
    assert (w, h) == (slot["width"], slot["height"]), (
        f"{slot['id']}: PNG is {w}x{h}, manifest says {slot['width']}x{slot['height']}"
    )


def test_hero_is_og_source_grade():
    # The hero feeds the Stage 6 social/OG asset, so it must have OG-grade resolution: long edge
    # >= 1200 and short edge >= 600 (enough to compose a 1200x630+ preview without upscaling).
    hero = next(s for s in _diagram_slots() if s["id"] == "00-hero-decision-tree")
    w, h = _png_size(os.path.join(REPO, hero["path"]))
    assert max(w, h) >= 1200, f"hero long edge {max(w, h)} < 1200"
    assert min(w, h) >= 600, f"hero short edge {min(w, h)} < 600"
