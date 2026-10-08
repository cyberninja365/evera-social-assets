#!/usr/bin/env python3
"""Build Evera social collateral JPGs from 4x6 mailer source PNGs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source" / "4x6"
OUT_DIR = ROOT / "collateral-social"
BRAND_LOGO = ROOT / "brand" / "evera-logo-full-transparent.png"

NAVY = (26, 58, 92)  # ~#1a3a5c
ORANGE = (232, 108, 36)  # ~#e86c24
LIGHT_BLUE = (232, 244, 252)  # ~#e8f4fc

SQUARE_SIZE = (1080, 1080)
PORTRAIT_SIZE = (1080, 1350)

SET_FOLDERS: list[tuple[str, str, str, str]] = [
    ("01 Free Cyber Checkup", "01", "free-cyber-checkup", "free-checkup"),
    ("02 See Plans & Pricing", "02", "plans-pricing", "plans-pricing"),
    ("03 Protect Mom & Dad", "03", "protect-mom-dad", "protect-mom-dad"),
    ("04 Ask Evera_Scam Help", "04", "scam-help", "scam-help"),
    ("05 Free Scam Guide", "05", "free-scam-guide", "free-scam-guide"),
    ("06 Talk to a Real Person", "06", "talk-to-a-real-person", "talk-to-a-real-person"),
    ("07 Launch Special", "07", "launch-special", "launch-special"),
    ("08 Scam Quiz", "08", "scam-quiz", "scam-quiz"),
]

FOLDER_BY_NAME = {name: (set_id, campaign, slug_prefix) for name, set_id, campaign, slug_prefix in SET_FOLDERS}


@dataclass
class CardResult:
    set: str
    source_file: str
    slug: str
    campaign: str
    output_square: str
    output_portrait: str
    issues: list[str] = field(default_factory=list)


def normalize_stem(filename: str) -> str:
    stem = Path(filename).stem
    stem = stem.replace("_", "-")
    stem = re.sub(r"[^a-zA-Z0-9\-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-").lower()
    return stem or "card"


def slug_for_file(folder_name: str, filename: str) -> str:
    _, _, slug_prefix = FOLDER_BY_NAME[folder_name]
    return f"{slug_prefix}-{normalize_stem(filename)}"


def extract_front_panel(img: Image.Image) -> tuple[Image.Image, str | None]:
    w, h = img.size
    if w > h:
        return img.crop((0, 0, w // 2, h)), None
    if h > w:
        return img.crop((0, 0, w, h // 2)), None
    issue = f"unexpected square source dimensions {w}x{h}"
    return img, issue


def dominant_edge_color(arr: np.ndarray, side: str) -> tuple[int, int, int]:
    h, w = arr.shape[:2]
    strip = 8
    if side == "top":
        sample = arr[:strip, :, :3]
    elif side == "bottom":
        sample = arr[h - strip :, :, :3]
    elif side == "left":
        sample = arr[:, :strip, :3]
    else:
        sample = arr[:, w - strip :, :3]
    flat = sample.reshape(-1, 3)
    return tuple(int(x) for x in np.median(flat, axis=0))


def detect_bottom_trim(arr: np.ndarray) -> tuple[int, list[str]]:
    """Return y coordinate (exclusive) for main content; trim rep/QR footer."""
    issues: list[str] = []
    h, w = arr.shape[:2]
    default_y = int(h * 0.82)

    row_means = arr.mean(axis=(1, 2))
    row_stds = arr.std(axis=(1, 2))

    # Navy rep strip at very bottom (~3–6% height)
    bottom_search_start = int(h * 0.88)
    navy_rows = []
    for y in range(h - 1, bottom_search_start, -1):
        row = arr[y, :, :3]
        if row.mean() < 95 and (row[:, 0] > row[:, 2] + 15).mean() > 0.5:
            navy_rows.append(y)
        elif navy_rows:
            break
    if navy_rows:
        default_y = min(default_y, navy_rows[-1])

    # Orange CTA band above navy
    orange_rows = []
    for y in range(int(h * 0.65), int(h * 0.92)):
        row = arr[y, :, :3]
        r, g, b = row.mean(axis=0)
        if r > 150 and g < 140 and b < 100 and r > g + 30:
            orange_rows.append(y)
    if orange_rows:
        default_y = min(default_y, orange_rows[0])

    # QR / phone-scan box: high-contrast block bottom-right
    y0, y1 = int(h * 0.58), int(h * 0.88)
    x0, x1 = int(w * 0.42), w
    region = arr[y0:y1, x0:x1]
    if region.size:
        gray = region.mean(axis=2)
        edges = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
        if edges > 12:
            # extend trim upward slightly when QR clutter detected
            default_y = min(default_y, y0 + int((y1 - y0) * 0.35))
            pass  # trim handles scan/QR footer band

    # Sudden jump to low-variance rows (solid bars)
    for y in range(int(h * 0.72), h - 5):
        if row_stds[y] < 22 and row_means[y] < 120:
            default_y = min(default_y, y)
            break

    default_y = max(int(h * 0.68), min(default_y, int(h * 0.9)))
    if default_y >= h - 5:
        issues.append("bottom_trim_fallback")
        default_y = int(h * 0.8)
    return default_y, issues


def inpaint_qr_patch(panel: Image.Image, issues: list[str]) -> Image.Image:
    arr = np.array(panel.convert("RGB"))
    h, w = arr.shape[:2]
    y0, y1 = int(h * 0.62), int(h * 0.86)
    x0, x1 = int(w * 0.48), int(w * 0.96)
    sub = arr[y0:y1, x0:x1]
    if sub.size == 0:
        return panel
    gray = sub.mean(axis=2)
    # White/light rounded rectangle for QR
    mask = (gray > 200) & (sub.std(axis=2) < 45)
    if mask.mean() > 0.08:
        fill = dominant_edge_color(arr, "left")
        arr[y0:y1, x0:x1][mask] = fill
        pass
    return Image.fromarray(arr)


def replace_logo_band(panel: Image.Image, logo: Image.Image, issues: list[str]) -> Image.Image:
    arr = np.array(panel.convert("RGBA"))
    h, w = arr.shape[:2]
    band_h = max(int(h * 0.13), 90)
    band_h = min(band_h, int(h * 0.18))

    bg_rgb = dominant_edge_color(arr, "top")
    # Prefer light header background when top is bright
    if sum(bg_rgb) / 3 > 160:
        bg_rgb = LIGHT_BLUE
    elif bg_rgb[0] < 80:
        bg_rgb = NAVY

    header = Image.new("RGBA", (w, band_h), bg_rgb + (255,))
    # Slight gradient blend into content
    blend = Image.new("RGBA", (w, band_h), (0, 0, 0, 0))
    for y in range(band_h):
        alpha = int(255 * (1 - y / max(band_h - 1, 1)) * 0.15)
        for x in range(w):
            blend.putpixel((x, y), bg_rgb + (alpha,))
    header = Image.alpha_composite(header, blend)

    target_w = int(w * 0.62)
    scale = target_w / logo.width
    target_h = int(logo.height * scale)
    max_logo_h = int(band_h * 0.72)
    if target_h > max_logo_h:
        scale = max_logo_h / logo.height
        target_w = int(logo.width * scale)
        target_h = int(logo.height * scale)
    logo_r = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
    lx = (w - target_w) // 2
    ly = (band_h - target_h) // 2
    header.paste(logo_r, (lx, ly), logo_r)

    body = Image.fromarray(arr).convert("RGBA")
    body_crop = body.crop((0, band_h, w, h))
    out = Image.new("RGBA", (w, h - band_h + band_h), (255, 255, 255, 255))
    out.paste(header, (0, 0))
    out.paste(body_crop, (0, band_h))
    return out.convert("RGB")


def build_clean_panel(front: Image.Image, logo: Image.Image) -> tuple[Image.Image, list[str]]:
    issues: list[str] = []
    panel = front.convert("RGB")
    panel = inpaint_qr_patch(panel, issues)

    arr = np.array(panel)
    content_bottom, trim_issues = detect_bottom_trim(arr)
    issues.extend(trim_issues)
    panel = panel.crop((0, 0, panel.width, content_bottom))

    panel = replace_logo_band(panel, logo, issues)
    return panel, issues


def fit_on_canvas(
    panel: Image.Image, size: tuple[int, int], bias: str = "center"
) -> Image.Image:
    tw, th = size
    bg = LIGHT_BLUE
    # Sample background from panel corners
    arr = np.array(panel)
    corners = [
        arr[:20, :20],
        arr[:20, -20:],
        arr[-20:, :20],
        arr[-20:, -20:],
    ]
    med = np.median(np.concatenate([c.reshape(-1, 3) for c in corners]), axis=0)
    if med.mean() > 100:
        bg = tuple(int(x) for x in med)

    scale = min(tw / panel.width, th / panel.height)
    nw, nh = int(panel.width * scale), int(panel.height * scale)
    resized = panel.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", size, bg)
    x = (tw - nw) // 2
    if bias == "top":
        y = int((th - nh) * 0.12)
    else:
        y = (th - nh) // 2
    canvas.paste(resized, (x, y))
    return canvas


def render_square(panel: Image.Image) -> Image.Image:
    # Slight top bias keeps headlines visible in square crop
    tw, th = SQUARE_SIZE
    scale = max(tw / panel.width, th / panel.height)
    nw, nh = int(panel.width * scale), int(panel.height * scale)
    resized = panel.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - tw) // 2
    y = int((nh - th) * 0.08)
    y = max(0, min(y, nh - th))
    return resized.crop((x, y, x + tw, y + th))


def render_portrait(panel: Image.Image) -> Image.Image:
    return fit_on_canvas(panel, PORTRAIT_SIZE, bias="top")


def collect_sources() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for folder_name in FOLDER_BY_NAME:
        folder = SOURCE_ROOT / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.png")):
            if path.name.startswith("."):
                continue
            items.append((folder_name, path))
    return items


def write_card_map_yaml(entries: list[dict]) -> None:
    lines = ["# Auto-generated card index for 4x6 → social collateral", "cards:"]
    for e in entries:
        lines.append(f"  - set: \"{e['set']}\"")
        lines.append(f"    source_path: \"{e['source_path']}\"")
        lines.append(f"    slug: \"{e['slug']}\"")
        lines.append(f"    campaign: \"{e['campaign']}\"")
    (OUT_DIR / "card_map.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not BRAND_LOGO.is_file():
        raise SystemExit(f"Missing brand logo: {BRAND_LOGO}")

    logo = Image.open(BRAND_LOGO).convert("RGBA")
    manifest: list[dict] = []
    card_map_entries: list[dict] = []
    seen_slugs: set[str] = set()

    for folder_name, path in collect_sources():
        set_id, campaign, _ = FOLDER_BY_NAME[folder_name]
        rel_source = str(path.relative_to(ROOT))
        slug = slug_for_file(folder_name, path.name)
        if slug in seen_slugs:
            slug = f"{slug}-dup"
        seen_slugs.add(slug)

        square_name = f"{set_id}-{slug}.jpg"
        portrait_name = f"{set_id}-{slug}-ig.jpg"
        issues: list[str] = []

        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                if img.size == (1024, 1536):
                    issues.append("source_layout_vertical")
                elif img.size != (1536, 1024):
                    issues.append(f"unusual_dimensions_{img.size[0]}x{img.size[1]}")
                front, orient_issue = extract_front_panel(img)
                if orient_issue:
                    issues.append(orient_issue)
                clean, proc_issues = build_clean_panel(front, logo)
                issues.extend(proc_issues)

                square = render_square(clean)
                portrait = render_portrait(clean)

                square_path = OUT_DIR / square_name
                portrait_path = OUT_DIR / portrait_name
                square.save(square_path, "JPEG", quality=92, optimize=True)
                portrait.save(portrait_path, "JPEG", quality=92, optimize=True)
        except Exception as exc:  # noqa: BLE001 — collect per-card failures in manifest
            issues.append(f"processing_error:{exc}")

        failed = any(i.startswith("processing_error") for i in issues)
        entry = {
            "set": set_id,
            "source_file": rel_source,
            "slug": slug,
            "output_square": square_name if not failed else "",
            "output_portrait": portrait_name if not failed else "",
            "issues": issues,
        }
        manifest.append(entry)
        card_map_entries.append(
            {
                "set": set_id,
                "source_path": rel_source,
                "slug": slug,
                "campaign": campaign,
            }
        )

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_card_map_yaml(card_map_entries)

    problems = [
        m
        for m in manifest
        if any(i.startswith(("processing_error", "unusual_dimensions", "unexpected")) for i in m["issues"])
        or m["issues"]
    ]
    jpg_count = sum(
        2
        for m in manifest
        if m["output_square"] and m["output_portrait"]
    )
    print(f"Processed {len(manifest)} cards")
    print(f"Wrote {jpg_count} JPGs to {OUT_DIR}")
    print(f"Cards with manifest notes/issues: {len(problems)}")
    for m in problems:
        print(f"  {m['source_file']}: {', '.join(m['issues'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
