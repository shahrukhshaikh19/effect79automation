"""Pixel-class checks. YAML cannot attest beauty. This is not a critic."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Any

from runtime.host.artifact_contract import PIXEL_SUFFIXES, is_flagship, pixel_evidence

LOOKDEV_DIR = "evidence/lookdev"
REF_DIRS = ("references", "reference")


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def png_stats(path: Path) -> dict[str, float] | None:
    """Mean luma / contrast / crushed-black ratio for 8-bit PNG. None if unreadable."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos = 8
    width = height = 0
    bit_depth = color_type = 0
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif ctype == b"IDAT":
            idat.extend(chunk)
        elif ctype == b"IEND":
            break
    if width < 1 or height < 1 or bit_depth != 8 or color_type not in {2, 6}:
        return None
    bpp = 3 if color_type == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = width * bpp
    rows: list[bytes] = []
    i = 0
    prev = bytes(stride)
    for _ in range(height):
        filt = raw[i]
        scan = bytearray(raw[i + 1 : i + 1 + stride])
        i += 1 + stride
        if filt == 1:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + left) & 255
        elif filt == 2:
            for x in range(stride):
                scan[x] = (scan[x] + prev[x]) & 255
        elif filt == 3:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + ((left + prev[x]) // 2)) & 255
        elif filt == 4:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                up_left = prev[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + _paeth(left, prev[x], up_left)) & 255
        elif filt != 0:
            return None
        prev = bytes(scan)
        rows.append(prev)
    step = max(1, height // 48)
    lumas: list[float] = []
    crushed = 0
    for y in range(0, height, step):
        row = rows[y]
        for x in range(0, width, max(1, width // 64)):
            o = x * bpp
            r, g, b = row[o], row[o + 1], row[o + 2]
            yv = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            lumas.append(yv)
            if yv < 0.04:
                crushed += 1
    if not lumas:
        return None
    mean = sum(lumas) / len(lumas)
    var = sum((v - mean) ** 2 for v in lumas) / len(lumas)
    return {
        "mean_luma": mean,
        "contrast": var**0.5,
        "crushed_black": crushed / len(lumas),
        "samples": float(len(lumas)),
    }


def write_solid_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    """Test helper: uncompressed-style 8-bit RGB PNG."""
    raw = bytearray()
    pixel = bytes(rgb)
    for _ in range(height):
        raw.append(0)
        raw.extend(pixel * width)
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    )


def reference_images(project_dir: Path) -> list[Path]:
    found: list[Path] = []
    for name in REF_DIRS:
        root = project_dir / name
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in PIXEL_SUFFIXES and path.stat().st_size > 32:
                found.append(path)
    return sorted(found)


def lookdev_images(project_dir: Path) -> list[Path]:
    root = project_dir / LOOKDEV_DIR
    if not root.is_dir():
        return []
    found: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".png", ".webp"} and path.stat().st_size > 4_000:
            found.append(path)
    return sorted(found)


def _hero_shots(project_dir: Path) -> list[Path]:
    shots: list[Path] = []
    for rel in pixel_evidence(project_dir):
        path = project_dir / rel
        if path.suffix.lower() == ".png":
            shots.append(path)
    return shots


def _class_issues(hero: dict[str, float], ref: dict[str, float] | None) -> list[str]:
    issues: list[str] = []
    if hero["mean_luma"] < 0.05 and hero["contrast"] < 0.04:
        issues.append("hero render is crushed/dead (near-black, no contrast) — not a finished lookdev")
    if ref is None:
        return issues
    if ref["mean_luma"] >= 0.20 and hero["mean_luma"] < 0.11:
        issues.append(
            f"hero mean luma {hero['mean_luma']:.2f} is a night-silhouette; "
            f"reference mean luma {ref['mean_luma']:.2f} is lit — class miss, not a mood shift"
        )
    if ref["mean_luma"] >= 0.20 and hero["mean_luma"] / max(ref["mean_luma"], 0.01) < 0.40:
        issues.append("hero is far darker than the mood reference — crushed default, not lookdev")
    if ref["contrast"] >= 0.08 and hero["contrast"] < 0.035:
        issues.append("hero has no readable contrast versus a detailed reference")
    return issues


def validate_lookdev_evidence(project_dir: Path, signals: dict[str, Any] | None) -> dict[str, Any]:
    if not is_flagship(signals):
        return {"ok": True, "issues": []}
    shots = lookdev_images(project_dir)
    if len(shots) < 2:
        return {
            "ok": False,
            "issues": [
                f"{LOOKDEV_DIR}/ needs at least two Blender/browser lookdev PNGs (>4KB). "
                "GLB + YAML is not lookdev. Screenshot the authored scene before export."
            ],
        }
    refs = [png_stats(p) for p in reference_images(project_dir)]
    refs = [s for s in refs if s]
    ref = max(refs, key=lambda s: s["mean_luma"]) if refs else None
    issues: list[str] = []
    for shot in shots[:4]:
        stats = png_stats(shot)
        if not stats:
            continue
        issues.extend(_class_issues(stats, ref))
    return {"ok": not issues, "issues": issues}


def validate_visual_class(project_dir: Path, signals: dict[str, Any] | None) -> dict[str, Any]:
    if not is_flagship(signals):
        return {"ok": True, "issues": []}
    shots = _hero_shots(project_dir)
    if not shots:
        return {"ok": False, "issues": ["no PNG hero captures to judge visual class"]}
    refs = [png_stats(p) for p in reference_images(project_dir)]
    refs = [s for s in refs if s]
    ref = max(refs, key=lambda s: s["mean_luma"]) if refs else None
    issues: list[str] = []
    checked = 0
    for shot in shots[:6]:
        stats = png_stats(shot)
        if not stats:
            continue
        checked += 1
        issues.extend(_class_issues(stats, ref))
    if checked == 0:
        return {"ok": False, "issues": ["hero captures are not readable 8-bit PNGs"]}
    # Unique issues only
    seen: list[str] = []
    for item in issues:
        if item not in seen:
            seen.append(item)
    return {"ok": not seen, "issues": seen}
