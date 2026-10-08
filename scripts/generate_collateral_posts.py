#!/usr/bin/env python3
"""Generate collateral-social/posts.csv and README.md from manifest + marketing captions."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collateral_content import CARDS, get_card

MANIFEST = ROOT / "collateral-social" / "manifest.json"
OUT_CSV = ROOT / "collateral-social" / "posts.csv"
OUT_README = ROOT / "collateral-social" / "README.md"

FOUNDING_PHRASE = (
    "limited-time Founding Member offer that locks in your pricing for the first 12 months"
)

# Exact caption bodies from suggested-changes (kept cards); CTA line included, link added separately.
CAPTION_BODIES: dict[str, str] = {
    "free-checkup-18-new": (
        "Your antivirus icon is green. Does that mean the whole house is covered?\n\n"
        "Usually it means one piece is working. The free Cyber Checkup looks at the rest: your devices, "
        "your accounts and the common ways scams get in.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-checkup-4": (
        "When did you last check the devices everyone shares at home?\n\n"
        "The free Cyber Checkup shows where your devices and accounts might be exposed, in plain language, "
        "with a short list of what to fix first.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-checkup-9": (
        "Kids on tablets, bills paid online, and passwords saved in too many places. Sound familiar?\n\n"
        "That's a lot of ways in for a scammer. The free Cyber Checkup walks through the basics and gives you "
        "simple next steps you can keep.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-10-new": (
        "Who watches the computers at your house when something looks off?\n\n"
        "Evera's team monitors your home computers, blocks threats and picks up the phone when something looks off. "
        "Plans start at $24/mo.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-11-new": (
        "Think real protection for the house costs a fortune?\n\n"
        "Personal is $24/mo (regular $29), Home+ is $49/mo (regular $59) and Family is $74/mo (regular $89), all monthly. "
        f"Right now we also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-11": (
        "Homework, games, group chats. How much of your kids' day happens online now?\n\n"
        "We watch the family computers for threats and scams, and you can call a real person when something seems wrong.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-12": (
        "Wish someone could just remote in and fix the computer for you?\n\n"
        "Remote Tech Support is $49/mo, and our U.S. team connects to the computer and handles it with you on the phone.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-15-new": (
        "Did your kid just get their first laptop?\n\n"
        "Set it up right from day one. Our team keeps an eye on it for threats and scams, and you get someone to call when you're not sure.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-15": (
        "Just moved in and hooked up every device in the house?\n\n"
        "A move is a good time to update every computer and check what's connected. "
        "The free Cyber Checkup tells you where to start.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-16-new": (
        "How many computers are in your house right now?\n\n"
        "Each one is a way in for a scammer. Evera's team watches them for you, and Home+ covers a busy household for $49/mo (regular $59).\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-16": (
        "Want extra protection beyond your home plan?\n\n"
        "Internet Protection is $14/mo and adds another layer our team manages for you.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-17-new": (
        "Is the antivirus that came with your laptop the only thing protecting it?\n\n"
        "Antivirus can't pick up the phone when a scammer is calling Mom. We watch the computers in your home and we answer when you call.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-17": (
        "Ever notice the same scam text going around your whole neighborhood group chat?\n\n"
        "We help local households stay a step ahead of it, with monitoring on your computers and a real person to call. Plans start at $24/mo.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-18": (
        "The dog counts on you. So do the kids and the computer everyone shares.\n\n"
        "Personal $24/mo (regular $29), Home+ $49/mo (regular $59) and Family $74/mo (regular $89), all monthly. "
        f"We also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-40": (
        "Are your parents still calling you every time a pop-up appears?\n\n"
        "Evera gives them their own team to call, and we watch their computer for threats.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-6": (
        "School, streaming, gaming and social media, all on the computers in your house?\n\n"
        "We keep watch on the family computers and you get real people to call when something feels wrong. Personal starts at $24/mo (regular $29).\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-7-new": (
        "Businesses have an IT department. Who does your family call?\n\n"
        "That's us. Our U.S.-based team monitors your home computers and helps when you call. Home+ is $49/mo (regular $59), and we have a "
        f"{FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-7": (
        "Two adults, a teenager and a computer nobody has updated in months?\n\n"
        "Home+ covers a household like that for $49/mo (regular $59), with our team watching for threats and answering when you call.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "plans-pricing-9-new": (
        "Grandma's laptop, your work computer and the gaming PC in the back room. Who's watching all of them?\n\n"
        f"Family is $74/mo (regular $89) and covers the whole house. We also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-14-2": (
        "Ever get a screenshot from Mom with just \"Is this real?\"\n\n"
        "Evera gives your parents their own U.S.-based team to ask, so you're not troubleshooting after dinner every night.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-14": (
        "Who do your parents call when a scary message pops up?\n\n"
        "If the answer is you, there's a better option. We watch their computer and they can call us first, any time something looks off.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-19-new": (
        "Do your folks forward every chain email \"just in case\"?\n\n"
        "Now they can forward the suspicious ones to us instead. We'd rather answer a quick question than help after money is gone.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-19": (
        "Are the grandkids on Grandma's computer every time they visit?\n\n"
        "We keep that computer watched and updated, so a game download doesn't turn into a problem for everyone.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-20-new": (
        "Dad fixed the printer himself and installed three toolbars along the way?\n\n"
        "Give him a team that can clean it up and that he can call without feeling silly.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-21-new-dad": (
        "Dad got a call about his \"compromised account\" and almost read them a code?\n\n"
        "He can always hang up. With Evera, he can call us and check the story before he does anything.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-21-new-mom": (
        "Something weird popped up on Mom's computer, and she called you first. Again?\n\n"
        "What if she had a number where someone who knows computers actually answers? That's what we do.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-26": (
        "Live in Kern County while your parents are across town or across the state?\n\n"
        "If anyone asks them for remote access, the answer is no. They can call our team instead and we'll check it with them.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-36": (
        "Your parent's on the phone with a \"bank investigator\" who wants gift cards?\n\n"
        "That's a scam every time. Save our number in their phone so they have someone to call before they buy anything.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-37": (
        "Can't be at Mom's house every time something goes wrong with the computer?\n\n"
        "We can help remotely, and she gets a real person on the phone instead of a chatbot.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-38": (
        "How many times have you explained two-step codes to Dad?\n\n"
        "Our team will do it as many times as he needs, patiently, and help him spot a scam call before it costs him.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-39": (
        "You can't stand between your parents and every scammer who calls.\n\n"
        "You can give them a team that watches their computer and answers the phone when you're not around.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "protect-mom-dad-8-new": (
        "Does Mom still keep her passwords on a sticky note by the monitor?\n\n"
        "Instead of playing unpaid IT, give her a team that answers the phone and helps her check a message before she clicks.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-23-1": (
        "Did a \"suspicious charge\" text show up while you were in line at the store?\n\n"
        "Fake fraud alerts want you to tap before you think. Don't use the link. Call your bank on the number on the back of your card.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-23-2": (
        "Got a text saying your account is locked and you need to click right now?\n\n"
        "That rush is the trick. Close the message and log in the way you normally do. If it's real, you'll see it there.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-24": (
        "Did \"Microsoft\" call to say your computer has a virus?\n\n"
        "Hang up. Microsoft doesn't call people about viruses. Don't install anything or let them connect to your computer.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-33": (
        "Strange email, odd text or a pop-up you don't trust?\n\n"
        "Evera customers can send it to us and ask before they click. That one step stops a lot of trouble.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-34": (
        "Utility company threatening a shutoff unless you pay with crypto or gift cards today?\n\n"
        "That's a scam. Call the number on your last bill, not the one in the message.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-help-35": (
        "Feel rushed, scared or surprised by a call or text?\n\n"
        "Those feelings are what scammers are after. Pause, and ask someone you trust before you pay, install anything or share a code.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-22": (
        "Your phone says your bank is calling. Is it really them?\n\n"
        "Caller ID can be faked, and scammers may already know your name. Hang up and call the number on the back of your card.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-27": (
        "A text from a new number says it's your kid with a broken phone and needs money?\n\n"
        "Call your child on the number you already have before you send anything.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-28": (
        "Would you know if a voice on the phone wasn't really your child?\n\n"
        "Scammers can copy voices from short clips online. Hang up and call your child back on their real number.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-29": (
        "Has someone on the phone asked you to pay with gift cards?\n\n"
        "That's a scam every time. No real company, bank or government office takes payment that way. Hang up.\n\n"
        "Bakersfield, take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-30-1-dad": (
        "Did Dad get a call from \"the bank\" asking for the code they just texted him?\n\n"
        "That code is the key to his account. A real bank won't ask for it. Hang up and call the number on his card.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-30-1-mom": (
        "Did Mom get a call from \"the bank\" asking for the code they just texted her?\n\n"
        "That code is the key to her account. A real bank won't ask for it. Hang up and call the number on her card.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-30-2": (
        "The caller knew your name and your bank. Does that make it real?\n\n"
        "No. That information is easy to find. Never share a code someone texted you, no matter what they already know.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "free-scam-guide-31": (
        "Got a text that your package is on hold?\n\n"
        "Don't tap the link. Check the order on the store's own site or app.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "talk-to-a-real-person-8": (
        "Tired of chatbots that send you in circles when the computer acts up?\n\n"
        "With Evera you call a real person in the U.S., whether it's an error message or a text that just feels wrong.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l1": (
        "New in town, and the scams sure aren't.\n\n"
        f"Evera's team watches the computers in your home, blocks threats and answers the phone. We also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l10": (
        "Scams, malware and stolen passwords. Who's watching for them at your house?\n\n"
        "That's our job. We monitor your home computers and help when something looks off.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l2-bak": (
        "Bakersfield, who do you call when the family computer starts acting strange?\n\n"
        f"Evera is now serving Kern County. Our team watches your home computers and answers the phone. We also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l2-mem1": (
        "Memphis, did another sketchy text show up on your phone today?\n\n"
        f"Evera is now serving Memphis households. Personal $24/mo, Home+ $49/mo and Family $74/mo, all monthly, with a {FOUNDING_PHRASE}.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l4": (
        "Been meaning to deal with the old laptop in the guest room?\n\n"
        f"Start with a free checkup, then pick a plan. We also have a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l5": (
        "Tired of piecing together five different security subscriptions?\n\n"
        f"Evera's team handles the monitoring, protection and support for you. Personal $24/mo, Home+ $49/mo and Family $74/mo, with a {FOUNDING_PHRASE}.\n\n"
        "Start with the free 2-minute Cyber Checkup:"
    ),
    "launch-special-l6": (
        "Wondering what we actually do?\n\n"
        "We watch the computers in your home, block threats and pick up the phone when something seems off. You talk to a real person in the U.S.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
    "scam-quiz-5": (
        "Could you spot a fake delivery text before you tapped the link?\n\n"
        "The free Cyber Checkup asks a few quick questions and shows where your household might be caught off guard.\n\n"
        "Take the free 2-minute Cyber Checkup:"
    ),
}

BAKERSFIELD_SLUGS = frozenset(
    {
        "protect-mom-dad-26",
        "free-scam-guide-29",
        "launch-special-l2-bak",
    }
)

MEMPHIS_SLUGS = frozenset({"launch-special-l2-mem1"})

SUGGESTED_SCHEDULE: dict[str, str] = {
    "free-scam-guide-31": "2026-11-01",
    "launch-special-l2-mem1": "2026-11-01",
    "protect-mom-dad-36": "2026-11-15",
    "scam-help-23-2": "2026-11-02",
    "free-scam-guide-28": "2026-11-03",
    "launch-special-l2-bak": "2026-11-04",
    "free-scam-guide-27": "2026-11-05",
    "scam-help-24": "2026-11-06",
}


def path_for_slug(slug: str) -> str:
    card = get_card(slug)
    geo = card.get("link_geo")
    if geo == "bakersfield" or slug in BAKERSFIELD_SLUGS:
        return "bakersfield"
    if geo == "memphis" or slug in MEMPHIS_SLUGS:
        return "memphis"
    return "checkup-start"


def build_link(slug: str, campaign: str, platform: str) -> str:
    path = path_for_slug(slug)
    return (
        f"https://www.everacyber.com/{path}"
        f"?utm_source={platform}&utm_medium=social&utm_campaign={campaign}&utm_content={slug}"
    )


def hashtags_for(slug: str) -> str:
    tags = ["#EveraCyber", "#HomeCybersecurity"]
    card = get_card(slug)
    geo = card.get("link_geo")
    if geo == "bakersfield" or slug in BAKERSFIELD_SLUGS:
        tags.append("#KernCounty")
    elif geo == "memphis" or slug in MEMPHIS_SLUGS:
        tags.append("#Memphis")
    else:
        tags.append("#CyberSafety")
    return " ".join(tags)


def caption_body(slug: str) -> str:
    if slug not in CAPTION_BODIES:
        raise KeyError(f"Missing caption for {slug}")
    return CAPTION_BODIES[slug].strip()


def full_caption(slug: str, campaign: str, platform: str) -> str:
    body = caption_body(slug)
    if platform in ("instagram", "tiktok"):
        return f"{body}\n\nLink in bio"
    url = build_link(slug, campaign, platform)
    return f"{body}\n\n{url}"


def schedule_for(slug: str, platform: str) -> str:
    if slug in SUGGESTED_SCHEDULE:
        return SUGGESTED_SCHEDULE[slug]
    return ""


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    readme_parts = [
        "# Evera collateral social (marketing rebuild)\n\n",
        "Square JPGs are 1080×1080; Instagram portrait files use `-ig` before `.jpg` (1080×1350).\n",
        "Artwork is rebuilt from `scripts/collateral_content.py` and `scripts/build_collateral_social.py` "
        "(designed layouts, no mailer art). Instagram and TikTok captions end with \"Link in bio\"; "
        "UTM links stay in the `link` column.\n\n",
        "Rebuild on a machine with `source/4x6/` mailer PNGs (gitignored) at the repo root, "
        "plus `brand/evera-logo-full-transparent.png`. Run `python3 scripts/build_collateral_social.py` "
        "then `python3 scripts/generate_collateral_posts.py`.\n\n",
        "## Images and captions\n\n",
    ]

    for item in manifest:
        slug = item["slug"]
        if slug not in CAPTION_BODIES:
            continue
        campaign = item.get("campaign") or get_card(slug)["campaign"]
        square = item["output_square"]
        portrait = item["output_portrait"]
        if not square or not portrait:
            continue

        for platform, image_file, note in (
            ("facebook", square, "Square 1080×1080, Facebook"),
            ("tiktok", square, "Square 1080×1080, TikTok"),
            ("instagram", portrait, "Portrait 1080×1350, Instagram"),
        ):
            cap = full_caption(slug, campaign, platform)
            rows.append(
                {
                    "set": item["set"],
                    "image_file": image_file,
                    "platform_note": note,
                    "caption": cap,
                    "link": build_link(slug, campaign, platform),
                    "hashtags": hashtags_for(slug),
                    "suggested_schedule": schedule_for(slug, platform),
                }
            )

        cap_fb = full_caption(slug, campaign, "facebook")
        readme_parts.append(f"### `{square}` / `{portrait}`\n\n")
        readme_parts.append(f"{cap_fb}\n\n")
        readme_parts.append(f"{hashtags_for(slug)}\n\n")
        sched = schedule_for(slug, "facebook") or schedule_for(slug, "tiktok")
        if sched:
            readme_parts.append(f"_Suggested schedule: {sched}_\n\n")

    fieldnames = [
        "set",
        "image_file",
        "platform_note",
        "caption",
        "link",
        "hashtags",
        "suggested_schedule",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    OUT_README.write_text("".join(readme_parts), encoding="utf-8")
    print(f"Wrote {len(rows)} rows ({len(manifest)} cards) to {OUT_CSV}")
    print(f"Wrote {OUT_README}")


if __name__ == "__main__":
    main()
