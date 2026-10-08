# Cybersecurity Awareness Month — Oct 17–31, 2026

Daily Facebook/Instagram tip posts for **Evera Cyber** (managed home cybersecurity for families in Bakersfield/Kern County, CA and Memphis, TN).

## Contents

| File | Purpose |
|------|---------|
| `17_*.jpg` … `31_*.jpg` | 1080×1080 tip-card images (Evera logo, CAM header, headline, one tip, “Free 2-minute Cyber Checkup”) |
| `posts.csv` | Scheduling copy: `date`, `image_file`, `caption`, `link`, `hashtags` |
| `../scripts/generate_cam_oct17_31.py` | Regenerates images and CSV from the post definitions |

**Do not schedule via Buffer from this PR** — Evera Marketing reviews and publishes manually.

## Topics (Oct 17–31)

Fresh household topics (no repeat of Oct 7–16 themes: skimmers, passwords/MFA, email, phishing, habits list, updates, deepfake voice, code words, breach response).

| Date | Topic | Landing page |
|------|-------|----------------|
| Oct 17 | Fake package delivery texts | General (`/checkup-start`) |
| Oct 18 | Tech support pop-up scams | General |
| Oct 19 | Grandparent scams | General |
| Oct 20 | Wi‑Fi router passwords | **Kern / Bakersfield** (`/checkup-start`) |
| Oct 21 | Kids & gaming account scams | General |
| Oct 22 | Fake online stores (pre-holiday) | General |
| Oct 23 | QR code scams | General |
| Oct 24 | Facebook Marketplace scams | **Memphis** (`/memphis1`) |
| Oct 25 | Backups & family photos | General |
| Oct 26 | Old devices & dormant accounts | **Kern / Bakersfield** (`/checkup-start`) |
| Oct 27 | Smart TVs & cameras | General |
| Oct 28 | Social media oversharing | General |
| Oct 29 | Medicare & benefits scams (seniors) | General |
| Oct 30 | Memphis household security check | **Memphis** (`/memphis1`) |
| Oct 31 | Halloween “scary but true” — fake charity scams | General |

## Caption rules (same as CAM Prompt 1)

1. **Voice:** Plain language for busy households; practical, not alarmist.
2. **Structure:** Headline (matches the card) → blank line → one short tip (matches the card body) → blank line → optional one-line local note (Kern or Memphis posts only) → blank line → CTA line.
3. **CTA line (exact lead-in):** `Free 2-minute Cyber Checkup →` followed by the full URL (no URL printed on the image).
4. **Length:** Keep the tip to 1–2 sentences; captions should fit a single Facebook post without a “see more” break when possible.
5. **Hashtags:** Stored in the `hashtags` column only (append when publishing).

## Link / UTM rules

- **Base:** `https://everacyber.com`
- **General posts:** `https://everacyber.com/checkup-start`
- **Memphis posts (2):** `https://everacyber.com/memphis1`
- **Kern / Bakersfield posts (2):** `https://everacyber.com/checkup-start`
- **Query string (all posts):**  
  `utm_source=facebook&utm_medium=social&utm_campaign=cybersecurity-awareness-month&utm_content=<topic-slug>`

## Image style

Matches `week1-v2/` tip cards: light blue field, white rounded card, orange “CYBERSECURITY AWARENESS MONTH” label, navy headline and tip, orange “Free 2-minute Cyber Checkup” on the card, full Evera logo from `brand/evera-logo-full-transparent.png` bottom-left. No QR codes or URL text on images.

## Regenerate assets

```bash
python3 scripts/generate_cam_oct17_31.py
```
