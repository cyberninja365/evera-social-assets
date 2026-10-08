#!/usr/bin/env python3
"""Generate CAM Oct 17–31 tip cards (1080x1080) matching week1-v2 style."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cam-oct17-31"
LOGO_PATH = ROOT / "brand" / "evera-logo-full-transparent.png"

SIZE = 1080
BG = (232, 242, 251)
ORANGE = (219, 112, 56)
NAVY = (54, 73, 103)
WHITE = (255, 255, 255)

CARD_MARGIN = 56
CARD_TOP = 56
CARD_RADIUS = 28
CARD_HEIGHT = 380
LOGO_TARGET_W = 420
LOGO_MARGIN = 48

FONT_DIR = Path("/usr/share/fonts/truetype/macos")
INTER_BOLD = FONT_DIR / "Inter-Bold.ttf"
INTER_SEMI = FONT_DIR / "Inter-SemiBold.ttf"
INTER_REG = FONT_DIR / "Inter-Regular.ttf"


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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
    return lines


def rounded_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def render_card(headline: str, tip: str, outfile: Path) -> None:
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    card_box = (CARD_MARGIN, CARD_TOP, SIZE - CARD_MARGIN, CARD_TOP + CARD_HEIGHT)
    rounded_rect(draw, card_box, CARD_RADIUS, WHITE)

    pad_x = CARD_MARGIN + 44
    max_w = SIZE - 2 * CARD_MARGIN - 88

    font_label = load_font(INTER_SEMI, 26)
    font_head = load_font(INTER_BOLD, 52)
    font_body = load_font(INTER_REG, 34)
    font_cta = load_font(INTER_SEMI, 30)

    y = CARD_TOP + 36
    draw.text((pad_x, y), "CYBERSECURITY AWARENESS MONTH", font=font_label, fill=ORANGE)
    y += 44

    for line in wrap(draw, headline, font_head, max_w):
        draw.text((pad_x, y), line, font=font_head, fill=NAVY)
        y += 58

    y += 8
    for line in wrap(draw, tip, font_body, max_w):
        draw.text((pad_x, y), line, font=font_body, fill=NAVY)
        y += 42

    y = CARD_TOP + CARD_HEIGHT - 52
    draw.text((pad_x, y), "Free 2-minute Cyber Checkup", font=font_cta, fill=ORANGE)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    scale = LOGO_TARGET_W / logo.width
    logo_h = int(logo.height * scale)
    logo = logo.resize((LOGO_TARGET_W, logo_h), Image.Resampling.LANCZOS)
    lx = LOGO_MARGIN
    ly = SIZE - LOGO_MARGIN - logo_h
    img.paste(logo, (lx, ly), logo)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    img.save(outfile, "JPEG", quality=92, optimize=True)


POSTS = [
    {
        "date": "2026-10-17",
        "file": "17_fake-package-texts.jpg",
        "headline": "Pause on package texts.",
        "tip": "Delivery scams spike before the holidays. Open the carrier app or site you already use—don't tap random tracking links.",
        "slug": "fake-package-texts",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-18",
        "file": "18_tech-support-popups.jpg",
        "headline": "Close the pop-up. Don't call.",
        "tip": "Fake virus warnings want you to panic-dial a \"support\" number. Force-quit the browser; real security software won't demand an immediate phone call.",
        "slug": "tech-support-popups",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-19",
        "file": "19_grandparent-scams.jpg",
        "headline": "Verify urgent family calls.",
        "tip": "Scammers impersonate grandkids in crisis. Hang up and call your family member on the number you already have—or use your family code word.",
        "slug": "grandparent-scams",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-20",
        "file": "20_wifi-router-passwords.jpg",
        "headline": "Change your Wi‑Fi password.",
        "tip": "If it's still on the sticker from your Kern County internet provider, update it today. Use a long passphrase guests can't guess.",
        "slug": "wifi-router-passwords",
        "link_path": "/checkup-start",
        "local": "kern",
    },
    {
        "date": "2026-10-21",
        "file": "21_kids-gaming-scams.jpg",
        "headline": "Talk before they trade skins.",
        "tip": "Free Robux and \"account upgrade\" links steal logins. Teach kids: never share passwords or move chats to Discord with strangers.",
        "slug": "kids-gaming-scams",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-22",
        "file": "22_fake-online-stores.jpg",
        "headline": "Shop sites you trust.",
        "tip": "Too-good deals on unknown stores often mean stolen cards or nothing shipped. Pay with a credit card and double-check the real brand URL.",
        "slug": "fake-online-stores",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-23",
        "file": "23_qr-code-scams.jpg",
        "headline": "Think before you scan.",
        "tip": "QR codes on parking meters, flyers, and mail can open phishing pages. Preview the link—or type the official site yourself.",
        "slug": "qr-code-scams",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-24",
        "file": "24_facebook-marketplace.jpg",
        "headline": "Marketplace meets in public.",
        "tip": "Memphis neighbors: skip wire transfers and odd payment apps for local pickups. Meet in a safe, public place and bring someone with you.",
        "slug": "facebook-marketplace",
        "link_path": "/memphis1",
        "local": "memphis",
    },
    {
        "date": "2026-10-25",
        "file": "25_backups-photos.jpg",
        "headline": "Back up the photos you can't replace.",
        "tip": "Ransomware and lost phones hurt most when memories aren't saved. Turn on automatic cloud or external-drive backups for your family's devices.",
        "slug": "backups-photos",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-26",
        "file": "26_old-devices-accounts.jpg",
        "headline": "Retire old devices safely.",
        "tip": "Bakersfield households: wipe phones and laptops before donating, and close accounts you no longer use so they can't be reopened by a stranger.",
        "slug": "old-devices-accounts",
        "link_path": "/checkup-start",
        "local": "kern",
    },
    {
        "date": "2026-10-27",
        "file": "27_smart-tvs-cameras.jpg",
        "headline": "Secure smart TVs and cameras.",
        "tip": "Change default passwords, turn off remote access you don't need, and keep firmware updated so strangers can't peek into your home.",
        "slug": "smart-tvs-cameras",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-28",
        "file": "28_social-media-oversharing.jpg",
        "headline": "Share less location detail.",
        "tip": "Vacation posts, school jerseys, and birthday dates help scammers impersonate you. Save the big announcements until you're back home.",
        "slug": "social-media-oversharing",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-29",
        "file": "29_medicare-benefits-scams.jpg",
        "headline": "Benefits callers can be fakes.",
        "tip": "Medicare and Social Security won't threaten you over the phone or ask for gift cards. Hang up and call the number on your official card.",
        "slug": "medicare-benefits-scams",
        "link_path": "/checkup-start",
        "local": None,
    },
    {
        "date": "2026-10-30",
        "file": "30_memphis-household-check.jpg",
        "headline": "Memphis families: quick home check.",
        "tip": "Before the holidays, make sure every computer in the house has updates, backups, and someone you can call when something feels off.",
        "slug": "memphis-household-check",
        "link_path": "/memphis1",
        "local": "memphis",
    },
    {
        "date": "2026-10-31",
        "file": "31_halloween-scam-tip.jpg",
        "headline": "Scary but true: fake charities.",
        "tip": "Heart-tugging Halloween fundraisers can be scams. Give through the charity's real website—not a link from a stranger's text.",
        "slug": "halloween-charity-scams",
        "link_path": "/checkup-start",
        "local": None,
    },
]


def build_link(path: str, slug: str) -> str:
    return (
        f"https://everacyber.com{path}"
        f"?utm_source=facebook&utm_medium=social"
        f"&utm_campaign=cybersecurity-awareness-month&utm_content={slug}"
    )


def build_caption(headline: str, tip: str, link: str, local: str | None) -> str:
    lines = [headline, "", tip, ""]
    if local == "memphis":
        lines.append("Greater Memphis & Mid-South families—we're here when home tech gets stressful.")
        lines.append("")
    elif local == "kern":
        lines.append("Bakersfield & Kern County families—we help households stay ahead of everyday scams.")
        lines.append("")
    lines.append(f"Free 2-minute Cyber Checkup → {link}")
    return "\n".join(lines)


HASHTAGS = "#CybersecurityAwarenessMonth #EveraCyber #HomeCybersecurity #FamilySafety #ScamAlert"


def main() -> None:
    import csv

    rows = []
    for p in POSTS:
        out = OUT / p["file"]
        render_card(p["headline"], p["tip"], out)
        link = build_link(p["link_path"], p["slug"])
        caption = build_caption(p["headline"], p["tip"], link, p["local"])
        rows.append(
            {
                "date": p["date"],
                "image_file": p["file"],
                "caption": caption,
                "link": link,
                "hashtags": HASHTAGS,
            }
        )

    csv_path = OUT / "posts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "image_file", "caption", "link", "hashtags"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} images and {csv_path}")


if __name__ == "__main__":
    main()
