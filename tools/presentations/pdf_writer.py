"""Minimal, dependency-free PDF writer (Helvetica text, Letter pages, multi-page). Pure stdlib — same
ethos as the PNG writer. Produces a valid PDF that any reader opens. Deterministic."""
from __future__ import annotations

from typing import List

PAGE_W, PAGE_H = 612, 792  # US Letter, points
MARGIN = 72
LEADING = 14
FONT_SIZE = 11
TOP = PAGE_H - MARGIN
LINES_PER_PAGE = int((TOP - MARGIN) / LEADING)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _content_stream(lines: List[str]) -> bytes:
    parts = ["BT", f"/F1 {FONT_SIZE} Tf", f"{LEADING} TL", f"{MARGIN} {TOP} Td"]
    for ln in lines:
        safe = _escape(ln.encode("latin-1", "replace").decode("latin-1"))
        parts.append(f"({safe}) Tj T*")
    parts.append("ET")
    return ("\n".join(parts)).encode("latin-1")


def write_pdf(path: str, lines: List[str]) -> None:
    # max(1, …) guarantees at least one (possibly empty) page even for empty input.
    pages = [lines[i:i + LINES_PER_PAGE] for i in range(0, max(1, len(lines)), LINES_PER_PAGE)]

    objects: List[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)  # 1-based object number

    # 1 catalog, 2 pages (filled later), 3 font — reserve numbers by adding placeholders in order.
    catalog_num = add(b"")  # 1
    pages_num = add(b"")    # 2
    font_num = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")  # 3

    page_nums: List[int] = []
    for pl in pages:
        stream = _content_stream(pl)
        content_num = add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        page_obj = (
            "<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] "
            "/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
            % (pages_num, PAGE_W, PAGE_H, font_num, content_num)
        ).encode("latin-1")
        page_nums.append(add(page_obj))

    kids = " ".join(f"{n} 0 R" for n in page_nums)
    objects[pages_num - 1] = (
        "<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, len(page_nums))
    ).encode("latin-1")
    objects[catalog_num - 1] = ("<< /Type /Catalog /Pages %d 0 R >>" % pages_num).encode("latin-1")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0] * (len(objects) + 1)
    for i, obj in enumerate(objects, start=1):
        offsets[i] = len(out)
        out += f"{i} 0 obj\n".encode("latin-1") + obj + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for i in range(1, len(objects) + 1):
        out += f"{offsets[i]:010d} 00000 n \n".encode("latin-1")
    out += (
        "trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF"
        % (len(objects) + 1, catalog_num, xref_pos)
    ).encode("latin-1")

    with open(path, "wb") as fh:
        fh.write(out)
