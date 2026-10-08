#!/usr/bin/env python3
"""Rebuild Evera social collateral JPGs from collateral_content (designed layouts, no mailer art)."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collateral_content import CARDS, CardContent, get_card  # noqa: F401
from scripts.collateral_drops import DROP_OUTPUT_BASENAMES, is_dropped_slug

SOURCE_ROOT = ROOT / "source" / "4x6"
OUT_DIR = ROOT / "collateral-social"
BRAND_LOGO = ROOT / "brand" / "evera-logo-full-transparent.png"
REVIEW_SHEETS = ROOT / "evera-marketing" / "review" / "pr2-collateral" / "v2" / "sheets"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (26, 58, 92)
ORANGE = (232, 108, 36)
LIGHT_BLUE = (232, 244, 252)
WHITE = (255, 255, 255)
PHONE_BG = (245, 247, 250)
SMS_BUBBLE = (220, 228, 235)
SMS_BUBBLE_SCAM = (255, 235, 230)

SQUARE_SIZE = (1080, 1080)
PORTRAIT_SIZE = (1080, 1350)
LOGO_TARGET_WIDTH = 500
BODY_MIN_PX = 40
CTA_MIN_PX = 40
CTA_BAR_H = 76
FOUNDING_ON_IMAGE = "Founding Member pricing for 12 months"

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

# Former photo-strip cards rebuilt with designed heroes (contact sheet source list).
REBUILT_SLUGS: frozenset[str] = frozenset(
    {
        "free-checkup-18-new",
        "free-checkup-4",
        "free-checkup-9",
        "plans-pricing-10-new",
        "plans-pricing-11-new",
        "plans-pricing-11",
        "plans-pricing-12",
        "plans-pricing-15-new",
        "plans-pricing-15",
        "plans-pricing-16-new",
        "plans-pricing-16",
        "plans-pricing-17-new",
        "plans-pricing-17",
        "plans-pricing-18",
        "plans-pricing-40",
        "plans-pricing-6",
        "plans-pricing-7-new",
        "plans-pricing-7",
        "plans-pricing-9-new",
        "protect-mom-dad-14-2",
        "protect-mom-dad-14",
        "protect-mom-dad-19-new",
        "protect-mom-dad-19",
        "protect-mom-dad-20-new",
        "protect-mom-dad-26",
        "protect-mom-dad-37",
        "protect-mom-dad-38",
        "protect-mom-dad-39",
        "protect-mom-dad-8-new",
        "scam-help-33",
        "scam-help-35",
        "talk-to-a-real-person-8",
        "launch-special-l1",
        "launch-special-l10",
        "launch-special-l2-bak",
        "launch-special-l2-mem1",
        "launch-special-l4",
        "launch-special-l5",
        "launch-special-l6",
        "scam-quiz-5",
    }
)


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


def cta_display_text(cta_bar: str) -> str:
    text = cta_bar.strip()
    if text.endswith(":"):
        text = text[:-1].strip()
    return text


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


def draw_sms_hero(size: tuple[int, int], sender_line: str, message_line: str) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)
    margin = int(w * 0.12)
    phone_w = w - 2 * margin
    phone_h = int(h * 0.88)
    px = margin
    py = (h - phone_h) // 2
    draw.rounded_rectangle((px, py, px + phone_w, py + phone_h), radius=36, fill=PHONE_BG, outline=(180, 190, 200), width=3)
    inner = (px + 24, py + 56, px + phone_w - 24, py + phone_h - 24)
    draw.rounded_rectangle(inner, radius=20, fill=WHITE)
    label_font = ImageFont.truetype(FONT_BOLD, max(26, int(w * 0.04)))
    msg_font = ImageFont.truetype(FONT_REG, max(BODY_MIN_PX, int(w * 0.036)))
    tx = inner[0] + 20
    ty = inner[1] + 24
    draw.text((tx, ty), "Messages", fill=NAVY, font=label_font)
    ty += int(label_font.size * 1.5)
    draw.text((tx, ty), sender_line[:48], fill=(100, 110, 120), font=msg_font)
    ty += int(msg_font.size * 1.4)
    bubble_x1 = tx
    bubble_x2 = inner[2] - 60
    bubble_y1 = ty
    lines = wrap_text(draw, message_line[:160], msg_font, bubble_x2 - bubble_x1 - 24)
    line_h = int(msg_font.size * 1.25)
    bubble_y2 = bubble_y1 + len(lines) * line_h + 28
    draw.rounded_rectangle(
        (bubble_x1, bubble_y1, bubble_x2, bubble_y2),
        radius=18,
        fill=SMS_BUBBLE_SCAM,
    )
    by = bubble_y1 + 14
    for line in lines:
        draw.text((bubble_x1 + 16, by), line, fill=NAVY, font=msg_font)
        by += line_h
    return canvas


def draw_popup_hero(size: tuple[int, int], title: str, body: str) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, (210, 218, 228))
    draw = ImageDraw.Draw(canvas)
    margin = int(w * 0.1)
    desk = (margin, margin, w - margin, h - margin)
    draw.rounded_rectangle(desk, radius=12, fill=(180, 190, 200))
    pop_w = int((desk[2] - desk[0]) * 0.72)
    pop_h = int((desk[3] - desk[1]) * 0.55)
    pop_x = desk[0] + (desk[2] - desk[0] - pop_w) // 2
    pop_y = desk[1] + (desk[3] - desk[1] - pop_h) // 2
    draw.rounded_rectangle((pop_x, pop_y, pop_x + pop_w, pop_y + pop_h), radius=8, fill=WHITE, outline=ORANGE, width=4)
    title_font = ImageFont.truetype(FONT_BOLD, max(28, int(w * 0.042)))
    body_font = ImageFont.truetype(FONT_REG, max(BODY_MIN_PX - 2, int(w * 0.034)))
    tx = pop_x + 24
    ty = pop_y + 20
    for line in wrap_text(draw, title[:60], title_font, pop_w - 48):
        draw.text((tx, ty), line, fill=NAVY, font=title_font)
        ty += int(title_font.size * 1.15)
    ty += 10
    for line in wrap_text(draw, body[:140], body_font, pop_w - 48):
        draw.text((tx, ty), line, fill=(50, 60, 70), font=body_font)
        ty += int(body_font.size * 1.2)
    btn_w, btn_h = 120, 40
    draw.rounded_rectangle(
        (pop_x + pop_w - btn_w - 24, pop_y + pop_h - btn_h - 20, pop_x + pop_w - 24, pop_y + pop_h - 20),
        radius=6,
        fill=ORANGE,
    )
    return canvas


def _draw_icon_tile(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, label: str) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=NAVY, width=3)
    draw.ellipse((cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2), fill=LIGHT_BLUE)
    font = ImageFont.truetype(FONT_BOLD, max(22, r // 2))
    tw = draw.textlength(label, font=font)
    draw.text((cx - tw / 2, cy - font.size // 2 - 2), label, fill=NAVY, font=font)


def draw_icons_hero(size: tuple[int, int], labels: tuple[str, str, str] = ("PC", "Shield", "Call")) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)
    r = min(w, h) // 10
    gap = w // 4
    cy = h // 2
    positions = [gap, w // 2, w - gap]
    cap_font = ImageFont.truetype(FONT_REG, max(24, int(w * 0.028)))
    for i, (x, lab) in enumerate(zip(positions, labels)):
        _draw_icon_tile(draw, x, cy - 20, r, lab[:1] if len(lab) <= 6 else lab[:3])
        tw = draw.textlength(labels[i], font=cap_font)
        draw.text((x - tw / 2, cy + r + 8), labels[i], fill=NAVY, font=cap_font)
    return canvas


def draw_plan_tiles_hero(size: tuple[int, int]) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)
    plans = [
        ("Personal", "$24/mo"),
        ("Home+", "$49/mo"),
        ("Family", "$74/mo"),
    ]
    tile_w = int((w - 80) / 3) - 12
    tile_h = int(h * 0.55)
    y0 = (h - tile_h) // 2
    name_font = ImageFont.truetype(FONT_BOLD, max(28, int(w * 0.032)))
    price_font = ImageFont.truetype(FONT_BOLD, max(BODY_MIN_PX, int(w * 0.038)))
    for i, (name, price) in enumerate(plans):
        x0 = 40 + i * (tile_w + 18)
        draw.rounded_rectangle((x0, y0, x0 + tile_w, y0 + tile_h), radius=16, fill=WHITE, outline=NAVY, width=3)
        draw.text((x0 + 16, y0 + 20), name, fill=NAVY, font=name_font)
        draw.text((x0 + 16, y0 + tile_h - price_font.size - 24), price, fill=ORANGE, font=price_font)
    return canvas


def draw_copy_panel_hero(size: tuple[int, int], lines: list[str]) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)
    pad = 24
    box = (pad, pad, w - pad, h - pad)
    draw.rounded_rectangle(box, radius=16, fill=WHITE, outline=NAVY, width=2)
    font = ImageFont.truetype(FONT_REG, max(BODY_MIN_PX, int(w * 0.034)))
    ty = box[1] + 20
    for line in lines[:4]:
        for wrapped in wrap_text(draw, line, font, box[2] - box[0] - 40):
            draw.text((box[0] + 20, ty), wrapped, fill=NAVY, font=font)
            ty += int(font.size * 1.25)
        ty += 8
    return canvas


def draw_pricing_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    pricing: str,
    max_width: int,
    font: ImageFont.FreeTypeFont,
) -> int:
    """Render pricing with wrap; split on middle dots if needed."""
    pricing = pricing.replace("(regular $29)", "").replace("(regular $59)", "").replace("(regular $89)", "")
    pricing = re.sub(r"\s+", " ", pricing).strip()
    segments = [s.strip() for s in re.split(r"[·]", pricing) if s.strip()]
    if not segments:
        segments = [pricing]
    line_h = int(font.size * 1.25)
    cy = y
    row: list[str] = []
    row_w = 0
    gap = draw.textlength(" · ", font=font)

    def flush_row() -> None:
        nonlocal cy, row, row_w
        if not row:
            return
        text = " · ".join(row)
        draw.text((x, cy), text, fill=ORANGE, font=font)
        cy += line_h
        row = []
        row_w = 0

    for seg in segments:
        seg_w = draw.textlength(seg, font=font)
        extra = gap if row else 0
        if row and row_w + extra + seg_w > max_width:
            flush_row()
        if row:
            row_w += gap + seg_w
        else:
            row_w = seg_w
        row.append(seg)
    flush_row()
    return cy


def paste_logo(canvas: Image.Image, logo: Image.Image, header_h: int) -> None:
    w = canvas.width
    scale = LOGO_TARGET_WIDTH / logo.width
    lw = int(logo.width * scale)
    lh = int(logo.height * scale)
    if lh > header_h - 24:
        scale = (header_h - 24) / logo.height
        lw = int(logo.width * scale)
        lh = int(logo.height * scale)
    logo_r = logo.resize((lw, lh), Image.Resampling.LANCZOS)
    canvas.paste(logo_r, ((w - lw) // 2, (header_h - lh) // 2), logo_r)


def render_card(
    content: CardContent,
    logo: Image.Image,
    size: tuple[int, int],
) -> Image.Image:
    w, h = size
    is_portrait = h > w
    canvas = Image.new("RGB", size, LIGHT_BLUE)
    draw = ImageDraw.Draw(canvas)

    header_h = 200 if is_portrait else 190
    draw.rectangle((0, 0, w, header_h), fill=LIGHT_BLUE)
    paste_logo(canvas, logo, header_h)

    cta_h = CTA_BAR_H
    text_top = header_h + 16
    text_bottom_limit = h - cta_h - 16

    headline_px = 52 if is_portrait else 46
    body_px = 42 if is_portrait else 40
    head_font, body_font = load_fonts(headline_px, body_px)
    margin_x = 56
    max_text_w = w - 2 * margin_x

    hero_mode = content.get("hero_mode", "icons")
    y = text_top

    headline = content["headline"].replace("|", "\n")
    for line in headline.split("\n"):
        for wrapped in wrap_text(draw, line, head_font, max_text_w):
            draw.text((margin_x, y), wrapped, fill=NAVY, font=head_font)
            y += int(head_font.size * 1.12)
    y += 8

    if hero_mode not in ("phone", "sms", "popup"):
        for line in content.get("image_lines", [])[:2]:
            for wrapped in wrap_text(draw, line, body_font, max_text_w):
                draw.text((margin_x, y), wrapped, fill=(40, 50, 60), font=body_font)
                y += int(body_font.size * 1.2)
            y += 4

    if content.get("pricing_line"):
        y += 10
        price_font = ImageFont.truetype(FONT_BOLD, body_px)
        y = draw_pricing_lines(draw, margin_x, y, content["pricing_line"], max_text_w, price_font)
        y += 6

    if content.get("founding_on_image"):
        y += 6
        founding_font = ImageFont.truetype(FONT_REG, BODY_MIN_PX)
        for line in wrap_text(draw, FOUNDING_ON_IMAGE, founding_font, max_text_w):
            draw.text((margin_x, y), line, fill=NAVY, font=founding_font)
            y += int(founding_font.size * 1.15)

    hero_top = y + 12
    hero_bottom = text_bottom_limit
    hero_w = w - 2 * margin_x
    hero_h = max(120, hero_bottom - hero_top)
    hero_size = (hero_w, hero_h)

    if hero_mode == "none":
        pass
    elif hero_mode == "plan_tiles":
        canvas.paste(draw_plan_tiles_hero(hero_size), (margin_x, hero_top))
    elif hero_mode == "copy_panel":
        panel_lines = content.get("panel_lines") or content.get("bullets", [])[:3]
        canvas.paste(draw_copy_panel_hero(hero_size, list(panel_lines)), (margin_x, hero_top))
    elif hero_mode == "icons":
        labels = content.get("icon_labels", ("Computers", "Monitoring", "Real help"))
        if isinstance(labels, list):
            labels = tuple(labels[:3])  # type: ignore[assignment]
        canvas.paste(draw_icons_hero(hero_size, labels), (margin_x, hero_top))
    elif hero_mode == "sms":
        sender = content.get("phone_caller", "Unknown")
        msg = content.get("phone_hint", "")
        canvas.paste(draw_sms_hero(hero_size, sender, msg), (margin_x, hero_top))
    elif hero_mode == "popup":
        title = content.get("phone_caller", "Security warning")
        body = content.get("phone_hint", "Call the number on screen now.")
        canvas.paste(draw_popup_hero(hero_size, title, body), (margin_x, hero_top))
    elif hero_mode == "phone":
        caller = content.get("phone_caller", "Unknown caller")
        hint = content.get("phone_hint", "If you're not sure, hang up and call back on a number you trust.")
        phone_img = draw_phone_hero(hero_size, caller, hint)
        canvas.paste(phone_img, (margin_x, hero_top))
    else:
        canvas.paste(draw_icons_hero(hero_size), (margin_x, hero_top))

    cta_text = cta_display_text(content["cta_bar"])
    draw.rectangle((0, h - cta_h, w, h), fill=ORANGE)
    cta_font = ImageFont.truetype(FONT_BOLD, max(CTA_MIN_PX, 40 if not is_portrait else 40))
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


def build_contact_sheet(manifest: list[dict]) -> Path:
    REVIEW_SHEETS.mkdir(parents=True, exist_ok=True)
    thumbs: list[Image.Image] = []
    labels: list[str] = []
    for m in manifest:
        slug = m["slug"]
        if slug not in REBUILT_SLUGS:
            continue
        sq = OUT_DIR / m["output_square"]
        if not sq.is_file():
            continue
        im = Image.open(sq).convert("RGB")
        im = im.resize((270, 270), Image.Resampling.LANCZOS)
        thumbs.append(im)
        labels.append(slug)
    if not thumbs:
        out = REVIEW_SHEETS / "rebuilt-cards-empty.jpg"
        Image.new("RGB", (100, 100), LIGHT_BLUE).save(out, quality=90)
        return out

    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    label_h = 28
    sheet_w = cols * 270
    sheet_h = rows * (270 + label_h)
    sheet = Image.new("RGB", (sheet_w, sheet_h), WHITE)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_REG, 14)
    for i, (thumb, lab) in enumerate(zip(thumbs, labels)):
        c, r = i % cols, i // cols
        x, y = c * 270, r * (270 + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 4, y + 272), lab[:36], fill=NAVY, font=font)
    out = REVIEW_SHEETS / "rebuilt-cards-v2.jpg"
    sheet.save(out, "JPEG", quality=90, optimize=True)
    return out


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
            square = render_card(content, logo, SQUARE_SIZE)
            portrait = render_card(content, logo, PORTRAIT_SIZE)
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
    sheet_path = build_contact_sheet(manifest)

    jpg_count = sum(2 for m in manifest if m["output_square"] and m["output_portrait"])
    print(f"Removed {removed} dropped JPG(s)")
    print(f"Built {len(manifest)} kept cards")
    print(f"Wrote {jpg_count} JPGs to {OUT_DIR}")
    print(f"Contact sheet: {sheet_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
