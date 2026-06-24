"""Minimal, dependency-free PNG encoder (RGB, 8-bit).

Pure stdlib (zlib + struct + binascii) so it works on any Python with no wheels to install.
Deterministic: no timestamps, no RNG. Reused by the placeholder generator (Stage 0) and the
brand-asset generator (Stage 6).
"""
from __future__ import annotations

import binascii
import struct
import zlib
from typing import Callable, Iterable, Tuple

RGB = Tuple[int, int, int]


def read_png_size(path: str) -> Tuple[int, int]:
    """Read (width, height) from a PNG's IHDR. Shared by the placeholder/manifest tooling and the
    validators so the IHDR parser lives in exactly one place."""
    with open(path, "rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{path} is not a PNG")
        fh.read(4)  # IHDR length
        if fh.read(4) != b"IHDR":
            raise ValueError(f"{path} missing IHDR")
        return struct.unpack(">II", fh.read(8))


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(
    path: str,
    width: int,
    height: int,
    pixel: Callable[[int, int], RGB],
    text_chunks: Iterable[Tuple[str, str]] = (),
) -> None:
    """Write an RGB PNG of exactly ``width`` x ``height`` to ``path``.

    ``pixel(x, y)`` returns an ``(r, g, b)`` tuple. ``text_chunks`` are ``(keyword, value)`` pairs
    written as Latin-1 ``tEXt`` chunks (used to embed the placeholder label in the file itself).
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"width/height must be positive, got {width}x{height}")

    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None) for this scanline
        row = bytearray(width * 3)
        i = 0
        for x in range(width):
            r, g, b = pixel(x, y)
            row[i] = r & 0xFF
            row[i + 1] = g & 0xFF
            row[i + 2] = b & 0xFF
            i += 3
        raw.extend(row)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (RGB)
    idat = zlib.compress(bytes(raw), 9)

    out = bytearray(sig)
    out += _chunk(b"IHDR", ihdr)
    for keyword, value in text_chunks:
        payload = keyword.encode("latin-1", "replace") + b"\x00" + value.encode("latin-1", "replace")
        out += _chunk(b"tEXt", payload)
    out += _chunk(b"IDAT", idat)
    out += _chunk(b"IEND", b"")

    with open(path, "wb") as fh:
        fh.write(out)
