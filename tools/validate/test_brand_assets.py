"""Validator: the banner + social-preview brand assets exist at OG-grade dimensions, carry the brand
text, and the manifest marks them real (Stage 6.1)."""
import json
import os
import struct
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "stubs"))
from png_writer import read_png_size  # noqa: E402
import make_brand  # noqa: E402 — reuse the exact same punctuation normalization the generator applies

MANIFEST = os.path.join(REPO, "assets", "manifest.json")


def _embeddable(s: str) -> str:
    # What actually lands in a PNG tEXt chunk: normalized punctuation, then latin-1 with replacement.
    return make_brand._norm(s).encode("latin-1", "replace").decode("latin-1")


def _slot(slot_id):
    with open(MANIFEST, encoding="utf-8") as fh:
        for s in json.load(fh)["slots"]:
            if s["id"] == slot_id:
                return s
    raise AssertionError(f"no manifest slot {slot_id}")


def _png_text_chunks(path):
    """Return the {keyword: value} tEXt chunks from a PNG."""
    out = {}
    with open(path, "rb") as fh:
        assert fh.read(8) == b"\x89PNG\r\n\x1a\n"
        while True:
            head = fh.read(8)
            if len(head) < 8:
                break
            length, tag = struct.unpack(">I", head[:4])[0], head[4:8]
            data = fh.read(length)
            fh.read(4)  # crc
            if tag == b"tEXt":
                kw, _, val = data.partition(b"\x00")
                out[kw.decode("latin-1")] = val.decode("latin-1")
            if tag == b"IEND":
                break
    return out


def test_banner_and_social_exist_at_manifest_dims():
    for slot_id in ("banner", "social-preview"):
        slot = _slot(slot_id)
        path = os.path.join(REPO, slot["path"])
        assert os.path.exists(path), f"{slot_id}: missing {slot['path']}"
        w, h = read_png_size(path)
        assert (w, h) == (slot["width"], slot["height"]), (
            f"{slot_id}: {w}x{h} != manifest {slot['width']}x{slot['height']}"
        )


def test_social_preview_meets_og_minimum():
    slot = _slot("social-preview")
    w, h = read_png_size(os.path.join(REPO, slot["path"]))
    assert w >= 1200 and h >= 630, f"social-preview {w}x{h} below GitHub OG minimum 1200x630"


def test_brand_slots_are_real():
    for slot_id in ("banner", "social-preview"):
        assert _slot(slot_id)["status"] == "real", f"{slot_id} still placeholder"


def test_banner_carries_tagline_and_mnemonic():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    chunks = _png_text_chunks(os.path.join(REPO, "assets", "banner.png"))
    assert chunks.get("Description") == _embeddable(cfg["tagline"]), "banner must embed the tagline"
    mnemonic = chunks.get("Mnemonic", "")
    assert "AGENTIC" in mnemonic
    for s in cfg["mnemonic"]["surfaces"]:
        assert s["name"] in mnemonic, f"banner mnemonic chunk missing surface {s['name']}"


def test_social_preview_carries_social_text_and_differs_from_banner():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    chunks = _png_text_chunks(os.path.join(REPO, "assets", "social-preview.png"))
    assert chunks.get("Description") == _embeddable(cfg["socialPreviewText"]), (
        "social-preview must embed the configured socialPreviewText (not the banner tagline)"
    )
    # The social card must not be a byte-identical clone of the banner.
    banner = open(os.path.join(REPO, "assets", "banner.png"), "rb").read()
    social = open(os.path.join(REPO, "assets", "social-preview.png"), "rb").read()
    assert banner != social, "social-preview.png is a byte-identical clone of banner.png"
