# Cybersecurity Awareness Month — Oct 17–31, 2026

Daily social posts for **Evera Cyber** (managed home cybersecurity for families in Bakersfield/Kern County, CA and Memphis, TN). Copy and card text match Evera Marketing review (Oct 8, 2026).

## Contents

| File | Purpose |
|------|---------|
| `17_*.jpg` … `31_*.jpg` | 1080×1080 tip-card JPGs (Evera logo, CAM header, headline, one tip, “Free 2-minute Cyber Checkup”) |
| `posts.csv` | `date`, `image_file`, `platform`, `caption`, `link`, `hashtags` (3 rows per day: facebook, instagram, tiktok) |
| `../scripts/generate_cam_oct17_31.py` | Regenerates images and CSV |
| `../brand/fonts/` | Bundled Inter fonts for reproducible renders |

**Do not schedule via Buffer from this PR** — Evera Marketing reviews and publishes manually.

## Topics (Oct 17–31)

| Date | Topic | Landing page |
|------|-------|----------------|
| Oct 17 | Bank and card alerts | General (`/checkup-start`) |
| Oct 18 | Tech support pop-up scams | General |
| Oct 19 | Grandparent scams | General |
| Oct 20 | Wi‑Fi router passwords | **Bakersfield / Kern** (`/bakersfield1`) |
| Oct 21 | Kids and gaming account scams | General |
| Oct 22 | Fake online stores (pre-holiday) | General |
| Oct 23 | QR code scams | General |
| Oct 24 | Facebook Marketplace scams | **Memphis** (`/memphis1`) |
| Oct 25 | Backups and family photos | General |
| Oct 26 | Old devices and dormant accounts | **Bakersfield / Kern** (`/bakersfield1`) |
| Oct 27 | Smart TVs and cameras | General |
| Oct 28 | Social media oversharing | General |
| Oct 29 | Medicare and benefits scams (seniors) | General |
| Oct 30 | Memphis household security check | **Memphis** (`/memphis1`) |
| Oct 31 | Halloween “scary but true” charity scams | General (`utm_content=halloween-scam-tip`) |

Oct 17 uses **bank card alerts** (not package-delivery texts) to avoid duplicating a Memphis package-text post already in Buffer.

## Caption rules (Prompt 1)

1. Open with a question or real situation.
2. Two to four short paragraphs; no stacked one-line fragments.
3. End with one call to action that **starts with a verb**, then the link on the following line.
4. Hashtags live in the `hashtags` column only when publishing.

Full caption text is in `posts.csv` and in `scripts/generate_cam_oct17_31.py`.

## Link / UTM rules

- **Base:** `https://www.everacyber.com`
- **General posts:** `/checkup-start`
- **Memphis (Oct 24, 30):** `/memphis1`
- **Bakersfield / Kern (Oct 20, 26):** `/bakersfield1`
- **Query (all posts):**  
  `utm_source=<facebook|instagram|tiktok>&utm_medium=social&utm_campaign=cybersecurity-awareness-month&utm_content=<topic-slug>`

`posts.csv` has one row per date per platform; only `utm_source` changes between facebook, instagram, and tiktok.

## Hashtags

`#CybersecurityAwarenessMonth #Evera`, plus `#Memphis` or `#Bakersfield` on local posts only.

## Image style

Light blue field, white rounded card (height fits content), orange CAM label, navy headline and body (40px body type), orange “Free 2-minute Cyber Checkup” with at least 32px above it, full official logo PNG at ~600px width bottom-left. No QR codes or URL text on images.

## Regenerate assets

```bash
python3 scripts/generate_cam_oct17_31.py
```
