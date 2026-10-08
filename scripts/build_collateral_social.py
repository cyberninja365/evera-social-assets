#!/usr/bin/env python3
"""Rebuild Evera social collateral JPGs from 4x6 sources + collateral_content."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collateral_content import CARDS, CardContent, get_card  # noqa: F401
from scripts.collateral_drops import DROP_OUTPUT_BASENAMES, is_dropped_slug

SOURCE_ROOT = ROOT / "source" / "4x6"
OUT_DIR = ROOT / "collateral-social"
BRAND_LOGO = ROOT / "brand" / "evera-logo-full-transparent.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (26, 58, 92)
ORANGE = (232, 108, 36)
LIGHT_BLUE = (232, 244, 252)
WHITE = (255, 255, 255)
PHONE_BG = (245, 247, 250)

SQUARE_SIZE = (1080, 1080)
PORTRAIT_SIZE = (1080, 1350)
LOGO_MIN_WIDTH = 480
BODY_MIN_PX = 40
CTA_BAR_H = 72

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
class BuildResult:
    set: str
    source_file: str
    slug: str
    campaign: str
    output_square: str
    output_portrait: str
    issues: list[str] = field(default_factory=list)


def normalize_stem(filename: str) -> str:
    stem = Path(filename).stem.replace("_", "-")
    stem = re.sub(r"[^a-zA-Z0-9\-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-").lower()
    return stem or "card"


def slug_for_file(folder_name: str, filename: str) -> str:
    _, _, slug_prefix = FOLDER_BY_NAME[folder_name]
    return f"{slug_prefix}-{normalize_stem(filename)}"


def extract_front_panel(img: Image.Image) -> Image.Image:
    w, h = img.size
    if w > h:
        return img.crop((0, 0, w // 2, h))
    if h > w:
        return img.crop((0, 0, w, h // 2))
    return img


def extract_hero_photo(front: Image.Image) -> Image.Image:
    """Photo-only strip from mailer art (avoid headline/CTA/QR bands)."""
    w, h = front.size
    x0, x1 = int(w * 0.08), int(w * 0.98)
    y0, y1 = int(h * 0.40), int(h * 0.74)
    crop = front.crop((x0, y0, x1, y1))
    arr = np.array(crop.convert("RGB"))
    # Down-weight high-contrast text rows (mailer typography)
    gray = arr.mean(axis=2)
    row_edge = np.abs(np.diff(gray, axis=1)).mean(axis=1)
    quiet = row_edge < 18
    if quiet.sum() > 10:
        idx = np.where(quiet)[0]
        y0r, y1r = idx[0], idx[-1] + 1
        if y1r - y0r > crop.height * 0.25:
            crop = crop.crop((0, y0r, crop.width, y1r))
    return crop.convert("RGB")


def soften_hero(photo: Image.Image) -> Image.Image:
    """Blur mailer typography in photo strips so only color/people remain."""
    w, h = photo.size
    small = photo.resize((max(1, w // 5), max(1, h // 5)), Image.Resampling.LANCZOS)
    blurred = small.resize((w, h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=6))
    return blurred


def load_fonts(headline_px: int, body_px: int) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    body_px = max(body_px, BODY_MIN_PX)
    return (
        ImageFont.truetype(FONT_BOLD, headline_px),
        ImageFont.truetype(FONT_REG, body_px),
    )


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def draw_phone_hero(size: tuple[int, int], caller_line: str, subtitle: str) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)
    margin = int(w * 0.12)
    phone_w = w - 2 * margin
    phone_h = int(h * 0.88)
    px = margin
    py = (h - phone_h) // 2
    radius = 36
    draw.rounded_rectangle((px, py, px + phone_w, py + phone_h), radius=radius, fill=PHONE_BG, outline=(180, 190, 200), width=3)
    notch_w = int(phone_w * 0.35)
    draw.rounded_rectangle(
        (px + (phone_w - notch_w) // 2, py + 12, px + (phone_w + notch_w) // 2, py + 36),
        radius=12,
        fill=(210, 215, 222),
    )
    inner = (px + 24, py + 56, px + phone_w - 24, py + phone_h - 24)
    draw.rounded_rectangle(inner, radius=20, fill=WHITE)
    title_font = ImageFont.truetype(FONT_BOLD, max(28, int(w * 0.045)))
    body_font = ImageFont.truetype(FONT_REG, max(BODY_MIN_PX, int(w * 0.038)))
    tx = inner[0] + 20
    ty = inner[1] + 28
    draw.text((tx, ty), "Incoming call", fill=(120, 130, 140), font=body_font)
    ty += int(body_font.size * 1.6)
    for line in wrap_text(draw, caller_line[:80], title_font, inner[2] - inner[0] - 40):
        draw.text((tx, ty), line, fill=NAVY, font=title_font)
        ty += int(title_font.size * 1.15)
    ty += 12
    for line in wrap_text(draw, subtitle[:120], body_font, inner[2] - inner[0] - 40):
        draw.text((tx, ty), line, fill=(60, 70, 80), font=body_font)
        ty += int(body_font.size * 1.25)
    draw.ellipse((inner[2] - 100, inner[3] - 100, inner[2] - 40, inner[3] - 40), fill=(220, 70, 60))
    draw.ellipse((inner[0] + 40, inner[3] - 100, inner[0] + 100, inner[3] - 40), fill=(70, 170, 90))
    return canvas


def paste_cover(canvas: Image.Image, photo: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    tw, th = x1 - x0, y1 - y0
    if tw <= 0 or th <= 0:
        return
    scale = max(tw / photo.width, th / photo.height)
    nw, nh = int(photo.width * scale), int(photo.height * scale)
    resized = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    cx = (nw - tw) // 2
    cy = (nh - th) // 2
    cropped = resized.crop((cx, cy, cx + tw, cy + th))
    canvas.paste(cropped, (x0, y0))


def render_card(
    content: CardContent,
    logo: Image.Image,
    hero_photo: Image.Image | None,
    size: tuple[int, int],
) -> Image.Image:
    w, h = size
    is_portrait = h > w
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)

    header_h = 150 if is_portrait else 130
    draw.rectangle((0, 0, w, header_h), fill=LIGHT_BLUE)

    logo_scale = max(LOGO_MIN_WIDTH / logo.width, (header_h * 0.75) / logo.height)
    lw = int(logo.width * logo_scale)
    lh = int(logo.height * logo_scale)
    if lh > header_h - 20:
        logo_scale = (header_h - 20) / logo.height
        lw = int(logo.width * logo_scale)
        lh = int(logo.height * logo_scale)
    lw = max(lw, LOGO_MIN_WIDTH)
    logo_r = logo.resize((lw, lh), Image.Resampling.LANCZOS)
    canvas.paste(logo_r, ((w - lw) // 2, (header_h - lh) // 2), logo_r)

    cta_h = CTA_BAR_H
    text_top = header_h + 16
    text_bottom_limit = h - cta_h - 16

    headline_px = 52 if is_portrait else 46
    body_px = 42 if is_portrait else 40
    head_font, body_font = load_fonts(headline_px, body_px)
    margin_x = 56
    max_text_w = w - 2 * margin_x

    hero_mode = content.get("hero_mode", "photo")
    hero_top = text_top
    y = text_top

    headline = content["headline"].replace("|", "\n")
    for line in headline.split("\n"):
        for wrapped in wrap_text(draw, line, head_font, max_text_w):
            draw.text((margin_x, y), wrapped, fill=NAVY, font=head_font)
            y += int(head_font.size * 1.12)
    y += 8

    # On-image copy stays short (captions live in posts.csv only).
    if hero_mode != "phone":
        for line in content.get("image_lines", [])[:2]:
            for wrapped in wrap_text(draw, line, body_font, max_text_w):
                draw.text((margin_x, y), wrapped, fill=(40, 50, 60), font=body_font)
                y += int(body_font.size * 1.2)
            y += 4

    if content.get("pricing_line"):
        y += 10
        price_font = ImageFont.truetype(FONT_BOLD, body_px)
        draw.text((margin_x, y), content["pricing_line"], fill=ORANGE, font=price_font)
        y += int(price_font.size * 1.3)

    if content.get("founding_on_image"):
        y += 6
        founding_font = ImageFont.truetype(FONT_REG, max(34, body_px - 4))
        founding = "Founding Member pricing locked for the first 12 months"
        for line in wrap_text(draw, founding, founding_font, max_text_w):
            draw.text((margin_x, y), line, fill=NAVY, font=founding_font)
            y += int(founding_font.size * 1.15)

    hero_top = y + 12
    hero_bottom = text_bottom_limit
    hero_box = (margin_x, hero_top, w - margin_x, hero_bottom)

    if hero_mode == "none":
        pass
    elif hero_mode == "phone":
        phone_h = hero_bottom - hero_top
        caller = content.get("phone_caller", "Unknown caller")
        hint = content.get("phone_hint", "If you're not sure, hang up and call back on a number you trust.")
        phone_img = draw_phone_hero((w - 2 * margin_x, phone_h), caller, hint)
        canvas.paste(phone_img, (margin_x, hero_top))
    else:
        if hero_photo is not None:
            paste_cover(canvas, soften_hero(hero_photo), hero_box)

    cta_text = content["cta_bar"]
    draw.rectangle((0, h - cta_h, w, h), fill=ORANGE)
    cta_font = ImageFont.truetype(FONT_BOLD, 36 if is_portrait else 34)
    tw = draw.textlength(cta_text, font=cta_font)
    draw.text(((w - tw) / 2, h - cta_h + (cta_h - cta_font.size) // 2 - 2), cta_text, fill=WHITE, font=cta_font)
    return canvas


def collect_sources() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for folder_name in FOLDER_BY_NAME:
        folder = SOURCE_ROOT / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.png")):
            if path.name.startswith("."):
                continue
            slug = slug_for_file(folder_name, path.name)
            if is_dropped_slug(slug):
                continue
            items.append((folder_name, path))
    return items


def delete_dropped_outputs() -> int:
    removed = 0
    for base in DROP_OUTPUT_BASENAMES:
        for name in (f"{base}.jpg", f"{base}-ig.jpg"):
            path = OUT_DIR / name
            if path.is_file():
                path.unlink()
                removed += 1
    return removed


def write_card_map_yaml(entries: list[dict]) -> None:
    lines = ["# Auto-generated card index for kept 4x6 → social collateral", "cards:"]
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

    removed = delete_dropped_outputs()
    logo = Image.open(BRAND_LOGO).convert("RGBA")
    manifest: list[dict] = []
    card_map_entries: list[dict] = []

    for folder_name, path in collect_sources():
        set_id, campaign, _ = FOLDER_BY_NAME[folder_name]
        slug = slug_for_file(folder_name, path.name)
        if slug not in CARDS:
            print(f"Warning: no collateral_content for kept slug {slug}", file=sys.stderr)
            continue

        content = get_card(slug)
        rel_source = str(path.relative_to(ROOT))
        square_name = f"{set_id}-{slug}.jpg"
        portrait_name = f"{set_id}-{slug}-ig.jpg"
        issues: list[str] = []

        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                front = extract_front_panel(img)
                hero_photo = extract_hero_photo(front) if content.get("hero_mode", "photo") == "photo" else None

                square = render_card(content, logo, hero_photo, SQUARE_SIZE)
                portrait = render_card(content, logo, hero_photo, PORTRAIT_SIZE)

                square.save(OUT_DIR / square_name, "JPEG", quality=92, optimize=True)
                portrait.save(OUT_DIR / portrait_name, "JPEG", quality=92, optimize=True)
        except Exception as exc:  # noqa: BLE001
            issues.append(f"processing_error:{exc}")

        failed = any(i.startswith("processing_error") for i in issues)
        manifest.append(
            {
                "set": set_id,
                "source_file": rel_source,
                "slug": slug,
                "campaign": campaign,
                "output_square": square_name if not failed else "",
                "output_portrait": portrait_name if not failed else "",
                "issues": issues,
            }
        )
        card_map_entries.append(
            {
                "set": set_id,
                "source_path": rel_source,
                "slug": slug,
                "campaign": campaign,
            }
        )

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_card_map_yaml(card_map_entries)

    jpg_count = sum(2 for m in manifest if m["output_square"] and m["output_portrait"])
    print(f"Removed {removed} dropped JPG(s)")
    print(f"Built {len(manifest)} kept cards")
    print(f"Wrote {jpg_count} JPGs to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
