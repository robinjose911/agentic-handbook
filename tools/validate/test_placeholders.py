"""Validator: every manifest visual slot resolves to a PNG at the declared dimensions (Stage 0.4)."""
import json
import os
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "stubs"))
from png_writer import read_png_size as _png_size  # noqa: E402

MANIFEST = os.path.join(REPO, "assets", "manifest.json")


def _slots():
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)["slots"]


def test_manifest_parses_and_has_slots():
    slots = _slots()
    assert len(slots) >= 17  # banner + social + 15 diagrams


def test_slot_ids_are_unique():
    ids = [s["id"] for s in _slots()]
    assert len(ids) == len(set(ids)), "duplicate slot id in manifest"


def test_all_diagram_slots_present():
    ids = {s["id"] for s in _slots() if s["kind"] == "diagram"}
    expected = {f"{i:02d}-" for i in range(15)}
    for prefix in expected:
        assert any(i.startswith(prefix) for i in ids), f"no diagram slot for {prefix}"


@pytest.mark.parametrize("slot", _slots(), ids=lambda s: s["id"])
def test_slot_resolves_at_declared_dimensions(slot):
    path = os.path.join(REPO, slot["path"])
    assert os.path.exists(path), f"slot {slot['id']} has no file at {slot['path']}"
    w, h = _png_size(path)
    assert (w, h) != (0, 0), f"slot {slot['id']} has zero dimensions"
    assert (w, h) == (slot["width"], slot["height"]), (
        f"slot {slot['id']}: file is {w}x{h}, manifest says {slot['width']}x{slot['height']}"
    )
