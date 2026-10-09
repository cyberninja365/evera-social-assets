#!/usr/bin/env python3
"""Generate CAM Oct 17–31 tip cards (1080x1080) matching week1-v2 style."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cam-oct17-31"
LOGO_PATH = ROOT / "brand" / "evera-logo-full-transparent.png"
FONT_DIR = ROOT / "brand" / "fonts"
INTER_BOLD = FONT_DIR / "Inter-Bold.ttf"
INTER_SEMI = FONT_DIR / "Inter-SemiBold.ttf"
INTER_REG = FONT_DIR / "Inter-Regular.ttf"
FALLBACK_FONT_DIRS = [
    FONT_DIR,
    Path("/usr/share/fonts/truetype/macos"),
    Path("/usr/share/fonts/truetype/dejavu"),
]

SIZE = 1080
BG = (232, 242, 251)
ORANGE = (219, 112, 56)
NAVY = (54, 73, 103)
WHITE = (255, 255, 255)

CARD_MARGIN = 56
CARD_TOP = 56
CARD_RADIUS = 28
CARD_PAD_X = 44
LOGO_TARGET_W = 600
LOGO_MARGIN = 48
BODY_FONT_SIZE = 40
CHECKUP_GAP_MIN = 32

PLATFORMS = ("facebook", "instagram", "tiktok")


def resolve_font(name: str) -> Path:
    for directory in FALLBACK_FONT_DIRS:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Missing font {name} in {FALLBACK_FONT_DIRS}")


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


def line_height(font: ImageFont.FreeTypeFont, spacing: float = 1.2) -> int:
    bbox = font.getbbox("Ay")
    return int((bbox[3] - bbox[1]) * spacing)


def render_card(headline: str, tip: str, outfile: Path) -> None:
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    pad_x = CARD_MARGIN + CARD_PAD_X
    max_w = SIZE - 2 * CARD_MARGIN - 2 * CARD_PAD_X

    font_label = load_font(resolve_font("Inter-SemiBold.ttf"), 26)
    font_head = load_font(resolve_font("Inter-Bold.ttf"), 52)
    font_body = load_font(resolve_font("Inter-Regular.ttf"), BODY_FONT_SIZE)
    font_cta = load_font(resolve_font("Inter-SemiBold.ttf"), 30)

    head_lh = line_height(font_head, 1.15)
    body_lh = line_height(font_body, 1.25)
    label_lh = line_height(font_label, 1.1)
    cta_lh = line_height(font_cta, 1.1)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    scale = LOGO_TARGET_W / logo.width
    logo_h = int(logo.height * scale)
    logo = logo.resize((LOGO_TARGET_W, logo_h), Image.Resampling.LANCZOS)
    logo_top = SIZE - LOGO_MARGIN - logo_h
    max_card_bottom = logo_top - 24

    y = CARD_TOP + 36
    y += label_lh + 12
    headline_lines = wrap(draw, headline, font_head, max_w)
    y += len(headline_lines) * head_lh + 8
    body_lines = wrap(draw, tip, font_body, max_w)
    content_bottom = y + len(body_lines) * body_lh
    checkup_y = content_bottom + CHECKUP_GAP_MIN
    card_bottom = checkup_y + cta_lh + 36
    card_bottom = min(card_bottom, max_card_bottom)
    if checkup_y + cta_lh + 24 > card_bottom:
        checkup_y = card_bottom - cta_lh - 24

    rounded_rect = ImageDraw.Draw(img)
    rounded_rect.rounded_rectangle(
        (CARD_MARGIN, CARD_TOP, SIZE - CARD_MARGIN, card_bottom),
        radius=CARD_RADIUS,
        fill=WHITE,
    )
    draw = ImageDraw.Draw(img)

    y = CARD_TOP + 36
    draw.text((pad_x, y), "CYBERSECURITY AWARENESS MONTH", font=font_label, fill=ORANGE)
    y += label_lh + 12

    for line in headline_lines:
        draw.text((pad_x, y), line, font=font_head, fill=NAVY)
        y += head_lh

    y += 8
    for line in body_lines:
        draw.text((pad_x, y), line, font=font_body, fill=NAVY)
        y += body_lh

    draw.text((pad_x, checkup_y), "Free 2-minute Cyber Checkup", font=font_cta, fill=ORANGE)

    lx = LOGO_MARGIN
    img.paste(logo, (lx, logo_top), logo)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    img.save(outfile, "JPEG", quality=92, optimize=True)


POSTS = [
    {
        "date": "2026-10-17",
        "file": "17_bank-card-alerts.jpg",
        "headline": "Turn on bank and card alerts.",
        "tip": "Get a text or email for every charge, so you spot one you didn't make right away.",
        "slug": "bank-card-alerts",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Would you know if someone used your card at 2 a.m.?

Log in to your bank and card accounts and turn on alerts for every purchase, by text or email. If a charge shows up that you didn't make, you'll know in minutes instead of at the end of the month.

Want to see what else is worth turning on at home? Take the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-18",
        "file": "18_tech-support-popups.jpg",
        "headline": "Don't call the number on a pop-up.",
        "tip": 'Fake virus warnings try to scare you into calling "support." Close the browser, or restart the computer, and don\'t call.',
        "slug": "tech-support-popups",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Has a screen ever popped up saying your computer is infected and you need to call a number right now?

That's a scam. Whoever answers will ask to get into your computer or ask you to pay. Close the browser, or restart the computer if it won't close, and don't call the number.

Not sure your computer is clean? Take the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-19",
        "file": "19_grandparent-scams.jpg",
        "headline": "Verify urgent family calls.",
        "tip": "Scammers pretend to be a grandchild in trouble and beg you to keep it secret. Hang up and call back on the number you already have.",
        "slug": "grandparent-scams",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Did you get a call from someone who sounded like your grandson, saying he's in trouble and begging you not to tell his parents?

Hang up and call him back on the number you already have, or call his mom or dad. Scammers count on you acting fast and keeping it quiet.

Take the free 2-minute Cyber Checkup to see where your family stands.""",
    },
    {
        "date": "2026-10-20",
        "file": "20_wifi-router-passwords.jpg",
        "headline": "Change your Wi-Fi password.",
        "tip": "Still using the password printed on the router sticker? Change it to a long passphrase only your household knows.",
        "slug": "wifi-router-passwords",
        "link_path": "/bakersfield1",
        "local": "bakersfield",
        "caption": """Is your Wi-Fi password still the one printed on the sticker on your router?

Anyone who's been in your house could have snapped a photo of it. Change it to a long passphrase only your household knows, and change the router's admin password too.

Bakersfield and Kern County, our team can look at the rest of your home setup with you. Start with the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-21",
        "file": "21_kids-gaming-scams.jpg",
        "headline": "Free Robux is always a trap.",
        "tip": '"Free Robux" and game upgrade links steal kids\' logins. Teach them never to share a password, even with a friend in the game.',
        "slug": "kids-gaming-scams",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Has your kid asked about a site that gives away free Robux or V-Bucks?

Those links are built to steal game logins, and sometimes the payment info saved on the account. Tell your kids never to share a password, even with a friend in the game, and to come get you before they click anything that promises free stuff.

Want a quick look at how protected your family's devices are? Take the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-22",
        "file": "22_fake-online-stores.jpg",
        "headline": "Shop sites you trust.",
        "tip": "Too-good deals on unknown stores often mean stolen cards or nothing shipped. Pay with a credit card and double-check the real brand URL.",
        "slug": "fake-online-stores",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Found a deal that looks too good on a store you've never heard of?

Fake shops are a common holiday trick. Some take your money and ship nothing, others just collect your card number. Type the store's web address yourself, and pay with a credit card so you can dispute the charge if something goes wrong.

Before you start holiday shopping, take the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-23",
        "file": "23_qr-code-scams.jpg",
        "headline": "Think before you scan.",
        "tip": "QR codes on parking meters, flyers and mail can lead to fake pages. Check the web address before you enter anything.",
        "slug": "qr-code-scams",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Ever scanned a QR code on a parking meter or a flyer without a second thought?

Scammers stick their own codes over real ones to send you to fake payment pages. Before you enter anything, check that the web address matches the real company, or type the official site yourself.

Take the free 2-minute Cyber Checkup to see what else might be catching your family off guard.""",
    },
    {
        "date": "2026-10-24",
        "file": "24_facebook-marketplace.jpg",
        "headline": "Marketplace meets in public.",
        "tip": "Memphis neighbors: skip wire transfers and odd payment apps for local pickups. Meet in a safe, public place and bring someone with you.",
        "slug": "facebook-marketplace",
        "link_path": "/memphis1",
        "local": "memphis",
        "caption": """Selling the old couch on Facebook Marketplace this weekend, Memphis?

If a buyer wants you to read them a code sent to your phone, overpays and asks for the difference back, or pushes a payment app you don't know, walk away. Meet somewhere public and take cash or a payment method you already use.

Want a second set of eyes on your home tech? Start with the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-25",
        "file": "25_backups-photos.jpg",
        "headline": "Back up the photos you can't replace.",
        "tip": "Ransomware and lost phones hurt most when memories aren't saved. Turn on automatic cloud or external drive backups for your family's devices.",
        "slug": "backups-photos",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """If your phone fell in the lake tomorrow, would the kids' photos go with it?

Turn on automatic backups on every phone and computer in the house, to the cloud, an external drive, or both. Then check once that the photos actually show up there.

Not sure what's backed up at your house? Take the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-26",
        "file": "26_old-devices-accounts.jpg",
        "headline": "Retire old devices safely.",
        "tip": "Bakersfield households: wipe phones and laptops before you sell or donate them, and close old accounts so nobody can take them over.",
        "slug": "old-devices-accounts",
        "link_path": "/bakersfield1",
        "local": "bakersfield",
        "caption": """Got an old phone or laptop sitting in a drawer, Bakersfield?

Before you sell, donate or recycle it, back up what you want, sign out of your accounts, and do a full factory reset. While you're at it, close old accounts you don't use anymore so nobody can take them over.

Kern County families, start with the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-27",
        "file": "27_smart-tvs-cameras.jpg",
        "headline": "Secure smart TVs and cameras.",
        "tip": "Change default passwords, turn off remote access you don't need, and keep firmware updated so strangers can't peek into your home.",
        "slug": "smart-tvs-cameras",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """When did you last change the password on your doorbell camera or smart TV?

Change any default passwords, turn off remote viewing you don't use, and let the updates install. That keeps strangers out of the cameras inside your home.

Take the free 2-minute Cyber Checkup to see what else in your house needs a look.""",
    },
    {
        "date": "2026-10-28",
        "file": "28_social-media-oversharing.jpg",
        "headline": "Post the trip after you're home.",
        "tip": "Live vacation posts say your house is empty, and birthdays and pet names are common security-question answers.",
        "slug": "social-media-oversharing",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Posting beach photos while you're still on vacation?

Live posts tell people your house is empty. And birthdays, pet names and your high school mascot are common answers to security questions. Share the trip once you're home, and keep those details off your public profile.

Take the free 2-minute Cyber Checkup to see what else is easy to fix.""",
    },
    {
        "date": "2026-10-29",
        "file": "29_medicare-benefits-scams.jpg",
        "headline": "Benefits callers can be fakes.",
        "tip": "Medicare and Social Security won't threaten you or ask for gift cards. Hang up and call the number on medicare.gov or ssa.gov.",
        "slug": "medicare-benefits-scams",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Did someone call saying your Medicare or Social Security benefits will stop unless you act today?

Hang up. Medicare and Social Security won't threaten you or ask you to pay with gift cards. If you're worried, look up the number on medicare.gov or ssa.gov and call them yourself.

Helping a parent with calls like this? Take the free 2-minute Cyber Checkup together.""",
    },
    {
        "date": "2026-10-30",
        "file": "30_memphis-household-check.jpg",
        "headline": "Memphis: a quick home tech check.",
        "tip": "Before the holidays, make sure every computer at home is updated and backed up, and everyone knows who to call when something looks off.",
        "slug": "memphis-household-check",
        "link_path": "/memphis1",
        "local": "memphis",
        "caption": """Memphis, with the holidays coming, is every computer in your house in good shape?

Take ten minutes this weekend. Make sure each one is updated, the photos and files are backed up, and everyone knows who to call when a message looks off.

Want someone to check it with you? Start with the free 2-minute Cyber Checkup.""",
    },
    {
        "date": "2026-10-31",
        "file": "31_halloween-scam-tip.jpg",
        "headline": "Scary but true: fake charities.",
        "tip": "Fundraiser texts can be fake. Look the charity up yourself and give through its own website.",
        "slug": "halloween-scam-tip",
        "link_path": "/checkup-start",
        "local": None,
        "caption": """Scary but true: some of the charity appeals hitting your phone this season aren't real.

If a text or post asks you to donate to a cause you've never heard of, don't use the link. Look the charity up yourself and give through its own website.

Take the free 2-minute Cyber Checkup before the holiday rush.""",
    },
]


def build_link(path: str, slug: str, platform: str) -> str:
    return (
        f"https://www.everacyber.com{path}"
        f"?utm_source={platform}&utm_medium=social"
        f"&utm_campaign=cybersecurity-awareness-month&utm_content={slug}"
    )


def hashtags_for(local: str | None) -> str:
    tags = "#CybersecurityAwarenessMonth #Evera"
    if local == "memphis":
        tags += " #Memphis"
    elif local == "bakersfield":
        tags += " #Bakersfield"
    return tags


def assert_no_em_dash(text: str, context: str) -> None:
    if "\u2014" in text:
        raise ValueError(f"Em dash found in {context}")


def main() -> None:
    import csv

    rows: list[dict[str, str]] = []
    for p in POSTS:
        for field in ("headline", "tip", "caption"):
            assert_no_em_dash(p[field], f"{p['date']} {field}")

        out = OUT / p["file"]
        render_card(p["headline"], p["tip"], out)

        for platform in PLATFORMS:
            link = build_link(p["link_path"], p["slug"], platform)
            caption = f"{p['caption'].strip()}\n{link}"
            rows.append(
                {
                    "date": p["date"],
                    "image_file": p["file"],
                    "platform": platform,
                    "caption": caption,
                    "link": link,
                    "hashtags": hashtags_for(p["local"]),
                }
            )

    csv_path = OUT / "posts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "image_file", "platform", "caption", "link", "hashtags"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(POSTS)} images and {len(rows)} CSV rows to {csv_path}")


if __name__ == "__main__":
    main()
