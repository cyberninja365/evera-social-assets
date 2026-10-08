#!/usr/bin/env python3
"""Generate collateral-social/posts.csv and README.md from manifest + captions."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "collateral-social" / "manifest.json"
OUT_CSV = ROOT / "collateral-social" / "posts.csv"
OUT_README = ROOT / "collateral-social" / "README.md"

FOUNDING = (
    "We also have a limited-time Founding Member offer that locks in your pricing for the first 12 months."
)
PLANS_BLURB = (
    "Plans start at Personal $24/mo (regular $29), Home+ $49/mo ($59), and Family $74/mo ($89). "
    "Add-ons include extra computer $15/mo, Internet Protection $14/mo, Remote Tech Support $49/mo, "
    "and Identity Protection $19/mo."
)

BANK_LABELS = {
    "amazon": "Amazon",
    "apple": "Apple",
    "bankofthesierra": "Bank of the Sierra",
    "bofa": "Bank of America",
    "capitalone": "Capital One",
    "chase": "Chase",
    "firsthorizon": "First Horizon",
    "firstsouthfinancial": "First South Financial",
    "irs": "the IRS",
    "ms": "Microsoft",
    "ofcu": "your credit union",
    "pp": "PayPal",
    "regions": "Regions Bank",
    "ssa": "Social Security",
    "truist": "Truist",
    "usbank": "U.S. Bank",
    "valleystrong": "Valley Strong",
    "wellsfargo": "Wells Fargo",
}


def link(slug: str, campaign: str, platform: str, memphis: bool = False) -> str:
    base = (
        "https://www.everacyber.com/memphis1"
        if memphis
        else "https://www.everacyber.com/checkup-start"
    )
    return (
        f"{base}?utm_source={platform}&utm_medium=social&utm_campaign={campaign}"
        f"&utm_content={slug}"
    )


def hashtags_for(entry: dict) -> str:
    tags = ["#EveraCyber", "#HomeCybersecurity"]
    if entry.get("memphis"):
        tags.append("#Memphis")
    elif "launch-special-l2-bak" in entry["slug"] or entry["set"] in ("01", "03", "05"):
        if "mem" not in entry["slug"]:
            tags.append("#KernCounty")
    else:
        tags.append("#CyberSafety")
    return " ".join(tags[:3])


def cta_checkup(url: str) -> str:
    return f"Start your free cyber checkup here: {url}"


def cta_quiz(url: str) -> str:
    return f"Take the scam awareness quiz here: {url}"


def cta_ask(url: str) -> str:
    return f"Not sure if a message is real? Ask us first: {url}"


def caption_for(item: dict) -> str:
    slug = item["slug"]
    set_id = item["set"]
    memphis = slug in ("launch-special-l2-mem1", "launch-special-l2-mem2")

    # --- Set 01: Free Cyber Checkup ---
    if slug == "free-checkup-4":
        return (
            "When was the last time you looked at how healthy your home network actually is?\n\n"
            "Most of us set up Wi‑Fi years ago and never think about it again. A free cyber checkup "
            "shows where your devices and accounts might be exposed, in plain language.\n\n"
            "No pressure, just a clear picture of what to fix first."
        )
    if slug == "free-checkup-9":
        return (
            "Kids are on tablets, you're paying bills online, and the router is blinking in the closet.\n\n"
            "That is a lot of doors for bad guys to knock on. A free cyber checkup walks through the "
            "basics: devices, Wi‑Fi, email, and the simple fixes that help.\n\n"
            "Takes a few minutes and you keep the report."
        )
    if slug == "free-checkup-13":
        return (
            "Got a stack of passwords saved in your browser and hope that counts as a plan?\n\n"
            "We see that a lot around Bakersfield and Kern County. A free cyber checkup flags weak spots "
            "like old software, risky settings, and signs your info may already be out there.\n\n"
            "You'll get a score and a short list of next steps."
        )
    if slug == "free-checkup-18-new":
        return (
            "Your antivirus icon is green. Does that mean you're actually covered?\n\n"
            "Usually it means one piece is working. A free cyber checkup looks at the whole house: "
            "network, devices, and common scam entry points.\n\n"
            "Easy to read, no geek speak."
        )
    if slug == "free-checkup-6-new":
        return (
            "Thinking about upgrading your home internet gear but not sure what is safe to buy?\n\n"
            "Wrong settings on a new router can leave you wide open. Start with a free cyber checkup so "
            "you know what shape you're in before you change anything.\n\n"
            "We'll point out what matters for your setup."
        )

    # --- Set 02: Plans & Pricing ---
    if set_id == "02":
        openings = {
            "plans-pricing-1": (
                "Antivirus alone doesn't stop the texts about fake deliveries or the \"bank\" calls anymore.\n\n"
                "Evera is built for homes, not office IT. You get protection on your devices plus real "
                "U.S.-based people when something feels off."
            ),
            "plans-pricing-2": (
                "If you've ever paid for \"computer tune‑up\" software and still felt nervous clicking links, "
                "you're not alone.\n\n"
                "We bundle monitoring, scam help, and support so you're not juggling five apps."
            ),
            "plans-pricing-3": (
                "Wondering what you actually get for a monthly home security plan?\n\n"
                "No hidden tiers or surprise annual bills. Monthly pricing, cancel when you need to."
            ),
            "plans-pricing-6": (
                "One laptop for work, one for the kids, phones on every plan… that's a Personal plan day.\n\n"
                "Personal is $24/mo right now (regular $29) and covers the basics for a smaller household."
            ),
            "plans-pricing-7": (
                "Two adults, a teen, and a smart TV that still uses the factory password?\n\n"
                "That's where Home+ fits. $49/mo (regular $59) for more devices and tighter coverage."
            ),
            "plans-pricing-7-new": (
                "Home+ is the sweet spot when you have a few computers and everyone's streaming on different apps.\n\n"
                "$49/mo (regular $59). We watch for malware, risky sites, and the weird pop‑ups that show up "
                "after kids install \"free\" games."
            ),
            "plans-pricing-9-new": (
                "Grandma's iPad, your work laptop, and the gaming PC in the back room all count.\n\n"
                "Family is $74/mo (regular $89) when you want everyone under one roof covered."
            ),
            "plans-pricing-10-new": (
                "Need an extra computer covered without jumping to the next plan?\n\n"
                "Add another PC or Mac for $15/mo. Handy when a kid heads to college with a hand‑me‑down laptop."
            ),
            "plans-pricing-11": (
                "Public Wi‑Fi at coffee shops is convenient. It's also a favorite spot for snoops.\n\n"
                "Internet Protection is $14/mo and helps keep traffic safer when you're off your home network."
            ),
            "plans-pricing-11-new": (
                "Traveling for work or visiting family and living on hotel Wi‑Fi?\n\n"
                "Internet Protection ($14/mo) adds a layer when you're not on your own router."
            ),
            "plans-pricing-12": (
                "Sometimes you just need a human to remote in and fix the printer… or the virus you swear you didn't click.\n\n"
                "Remote Tech Support is $49/mo if you want scheduled help from our U.S. team."
            ),
            "plans-pricing-15": (
                "Identity theft cleanup is a nightmare you don't want to DIY.\n\n"
                "Identity Protection is $19/mo and pairs with monitoring so you get a heads‑up early."
            ),
            "plans-pricing-15-new": (
                "Data breaches hit big stores and small towns alike.\n\n"
                "For $19/mo, Identity Protection helps you watch for misuse and know who to call if something slips through."
            ),
            "plans-pricing-16": (
                "Already infected or handing a slow PC to your parents?\n\n"
                "Cyber Cleanup is $99 standalone, or $49 when you add a plan. We scrub malware and tighten settings."
            ),
            "plans-pricing-16-new": (
                "That \"your computer is locked\" screen is scary. We see it weekly.\n\n"
                "Cyber Cleanup ($99, or $49 with a plan) is a one‑time deep clean before we put ongoing protection on."
            ),
            "plans-pricing-17": (
                "Not sure which plan fits? Most households land on Home+.\n\n"
                "We can walk through device counts and habits on a quick call before you commit."
            ),
            "plans-pricing-17-new": (
                "Comparing us to the antivirus bundle that came free with your laptop?\n\n"
                "Those tools rarely include someone you can call when a scammer is on the phone with Mom."
            ),
            "plans-pricing-18": (
                "Bundles are only useful if you understand the bill.\n\n"
                f"{PLANS_BLURB}"
            ),
            "plans-pricing-40": (
                "If you're still reading the fine print on three different security apps, pause.\n\n"
                f"{PLANS_BLURB} {FOUNDING}"
            ),
        }
        body = openings.get(
            slug,
            "Shopping for home cybersecurity shouldn't feel like buying a used car.\n\n"
            f"{PLANS_BLURB}",
        )
        if "Founding Member" not in body and slug not in ("plans-pricing-18",):
            body += f"\n\n{FOUNDING}"
        return body

    # --- Set 03: Protect Mom & Dad ---
    if set_id == "03":
        mom_dad = {
            "protect-mom-dad-8-new": (
                "Mom still writes passwords on a sticky note by the monitor?\n\n"
                "Instead of playing unpaid IT, give her a team that answers the phone. Evera blocks common "
                "threats and lets her ask a real person before she clicks."
            ),
            "protect-mom-dad-14": (
                "Dad got a pop‑up that said \"call Microsoft now\" and he almost did.\n\n"
                "Those screens are designed to panic people. With Evera he can call us first and we'll talk "
                "him through it."
            ),
            "protect-mom-dad-14-2": (
                "Ever get a text from Mom that just says \"Is this real?\" with a screenshot?\n\n"
                "You're not alone. Evera gives parents direct access to U.S.-based help so you don't have "
                "to troubleshoot after dinner every night."
            ),
            "protect-mom-dad-19": (
                "Parents want to bank online but they're nervous about scams.\n\n"
                "We help them spot fake alerts and know when to hang up. Protection runs in the background "
                "while they live their lives."
            ),
            "protect-mom-dad-19-new": (
                "If your folks still forward every chain email \"just in case,\" they need a safer outlet.\n\n"
                "They can forward suspicious stuff to us or call. We would rather answer a silly question "
                "than help after money is gone."
            ),
            "protect-mom-dad-20": (
                "Remote access scams target seniors because they're polite on the phone.\n\n"
                "Teach Mom one rule: if someone wants to control the screen, hang up and call Evera."
            ),
            "protect-mom-dad-20-new": (
                "Dad proud he fixed the printer himself… but installed three toolbars in the process?\n\n"
                "We've cleaned up worse. A Family plan covers their PC and someone they can talk to without "
                "feeling dumb."
            ),
            "protect-mom-dad-21-new-mom": (
                "Something weird popped up on Mom's computer and she called you first.\n\n"
                "What if she had a number where someone actually answers? Evera is built for that moment."
            ),
            "protect-mom-dad-21-new-dad": (
                "Dad answered a call about his \"compromised account\" and almost gave them a code.\n\n"
                "Hang up is always allowed. With Evera he can verify the story with us before he acts."
            ),
            "protect-mom-dad-26": (
                "You live in Kern County but your parents are across town or across the state.\n\n"
                "Distance makes tech support harder. Evera gives them the same help you'd want nearby."
            ),
            "protect-mom-dad-36": (
                "Gift card scams sound obvious until it's your parent on the phone with a \"bank investigator.\"\n\n"
                "We train families on the scripts scammers use and block a lot of the junk before it lands."
            ),
            "protect-mom-dad-37": (
                "Mom loves Facebook marketplace deals. So do thieves.\n\n"
                "We help her spot fake buyers and shady links without taking her off the site entirely."
            ),
            "protect-mom-dad-38": (
                "Ever notice how patient you have to be when explaining two‑factor codes to Dad?\n\n"
                "Our support team does that every day, calmly, without making anyone feel small."
            ),
            "protect-mom-dad-39": (
                "You can't put a firewall between your parents and every scammer who calls.\n\n"
                "You can put Evera on their devices so there's backup when you're not in the room."
            ),
        }
        return mom_dad.get(
            slug,
            "Your parents shouldn't have to guess if a warning on their screen is real.\n\n"
            "Evera gives them protection plus a phone number that reaches a person who will slow down and explain.",
        )

    # --- Set 04: Ask Evera / Scam Help ---
    if set_id == "04":
        scam_help = {
            "scam-help-23-1": (
                "That text about a \"suspicious charge\" showed up while you were in line at the store.\n\n"
                "Scammers love fake fraud alerts because they make you tap before you think. Don't click. "
                "Call your bank with the number on your card, or ask us if you're stuck."
            ),
            "scam-help-23-2": (
                "Same scary message, different phone number every time?\n\n"
                "That's the pattern. Real banks don't rush you through links in a panic text. "
                "Screenshot it and ask Evera if you want a second opinion."
            ),
            "scam-help-24": (
                "Someone on the phone said they're from fraud department and need you to \"verify\" your PIN.\n\n"
                "Hang up. No legit company asks for that. If you're shaking after the call, we're here to walk through what happened."
            ),
            "scam-help-25": (
                "Email says your package is held unless you pay a small fee today?\n\n"
                "Check the tracking on the store's real site, not the link in the message. When it still feels weird, ask us."
            ),
            "scam-help-33": (
                "Got a DM from a \"friend\" asking for money on a new account?\n\n"
                "Cloned profiles are common. Message your friend another way before you send anything."
            ),
            "scam-help-34": (
                "Utility company threatening shutoff unless you pay with crypto?\n\n"
                "That's a scam. Real utilities send paper bills and give you time. Call the number on your bill, not the text."
            ),
            "scam-help-35": (
                "Not sure if you're being rushed, scared, or surprised into acting?\n\n"
                "Those three feelings are the scam toolkit. Pause and ask Evera before you pay, install, or share a code."
            ),
        }
        return scam_help.get(
            slug,
            "When a message feels urgent and your stomach drops, that's the time to slow down.\n\n"
            "Forward it or call us. We'd rather talk for five minutes than help pick up the pieces later.",
        )

    # --- Set 05: Free Scam Guide ---
    if set_id == "05":
        if slug.startswith("free-scam-guide-22-"):
            key = slug.replace("free-scam-guide-22-", "")
            if key in BANK_LABELS:
                who = BANK_LABELS[key]
                return (
                    f"Your phone says \"{who}\" is calling. Could still be a stranger with a fake caller ID.\n\n"
                    f"Scammers spoof banks like {who} all the time. They may know your name or last charge. "
                    "That doesn't prove it's real.\n\n"
                    "Hang up and call the number on your card, or ask Evera before you share anything."
                )
        if slug == "free-scam-guide-22":
            return (
                "Bank on the caller ID doesn't mean bank on the phone.\n\n"
                "We put together a free scam guide with the scripts we hear every week. Read it before the next "
                "\"fraud alert\" text hits."
            )
        extra = {
            "free-scam-guide-27": (
                "IRS season brings real refunds and fake agents demanding gift cards.\n\n"
                "The IRS does not threaten arrest over the phone. Save our number for when a relative forwards you a scary voicemail."
            ),
            "free-scam-guide-28": (
                "Microsoft will not call because your home PC sent an error.\n\n"
                "Those calls are scams. If someone wants remote access, hang up and tell us what they said."
            ),
            "free-scam-guide-29": (
                "Amazon \"account problem\" texts are everywhere in Kern County right now.\n\n"
                "Log in by typing amazon.com yourself. Don't tap the link in the message."
            ),
            "free-scam-guide-30-1-mom": (
                "Mom forwarded a \"free prize\" email and asked if it's legit.\n\n"
                "That's exactly when to step in. Our guide walks through the red flags she can spot herself."
            ),
            "free-scam-guide-30-1-dad": (
                "Dad almost bought gift cards because someone said his Social Security number was frozen.\n\n"
                "Government agencies don't work that way. Share the guide with him before the next call."
            ),
            "free-scam-guide-30-2": (
                "Kids learn scams from TikTok. Parents learn them the hard way.\n\n"
                "Our free scam guide is short enough to read at the kitchen table together."
            ),
            "free-scam-guide-30-3": (
                "Neighborhood group chat is great until someone posts a sketchy link \"for a deal.\"\n\n"
                "The guide covers how fake discounts steal login info."
            ),
            "free-scam-guide-31": (
                "You don't need to be paranoid. You need a checklist.\n\n"
                "Download the free scam guide and keep it where everyone in the house can see it."
            ),
        }
        return extra.get(
            slug,
            "Scammers copy logos you trust. Our free guide shows what real companies never ask for.\n\n"
            "Share it with neighbors who keep asking you tech questions.",
        )

    # --- Set 06 ---
    if slug == "talk-to-a-real-person-8":
        return (
            "Tired of chatbots that send you in circles when your computer is acting up?\n\n"
            "Evera answers with real people in the U.S. You can call when something feels wrong, not just when software throws an error code.\n\n"
            "That's the whole point of how we're set up."
        )

    # --- Set 07: Launch Special ---
    if set_id == "07":
        if slug == "launch-special-l2-mem1" or slug == "launch-special-l2-mem2":
            return (
                "Memphis friends, did you get another sketchy text about a missed delivery today?\n\n"
                "We're local now, and we built Evera for households that want protection without a corporate help desk. "
                f"{FOUNDING}\n\n"
                "Personal $24/mo, Home+ $49/mo, Family $74/mo, all monthly."
            )
        if slug == "launch-special-l2-bak":
            return (
                "Bakersfield neighbors, home Wi‑Fi shouldn't be the weak link while everything else in the house is smart.\n\n"
                "Evera is live in Kern County with plans for real families and real phones you can call. "
                f"{FOUNDING}"
            )
        launch = {
            "launch-special-l1": (
                "Evera is new in town, but the scams aren't.\n\n"
                "We combine always‑on protection with U.S.-based support so you're not on hold with someone reading a script overseas."
            ),
            "launch-special-l3": (
                "Launch week is a good time to finally deal with the old laptop in the guest room.\n\n"
                "Founding Member pricing locks your rate for the first 12 months while we grow locally."
            ),
            "launch-special-l4": (
                "You shouldn't need a computer science degree to keep your family safe online.\n\n"
                "We keep the tech running quietly and pick up the phone when you're worried."
            ),
            "launch-special-l5": (
                "If you've been waiting for a simpler option than piecing together five apps, this is it.\n\n"
                f"{PLANS_BLURB} {FOUNDING}"
            ),
            "launch-special-l6": (
                "Neighbors keep asking us what we do differently.\n\n"
                "We watch your devices, block junk, and you talk to a real person here in the U.S. when something smells off."
            ),
            "launch-special-l7": (
                "Still forwarding scam screenshots to your group chat?\n\n"
                "Forward them to us instead. That's what we're here for."
            ),
            "launch-special-l8": (
                "Launch specials come and go. Locked‑in pricing for 12 months doesn't have to.\n\n"
                "Founding Member rates are open now for Bakersfield and Memphis households."
            ),
            "launch-special-l9": (
                "Your home has a lock on the front door. Your router deserves the same energy.\n\n"
                "Start with a free checkup, then pick a plan that fits how your family actually uses the internet."
            ),
            "launch-special-l10": (
                "We're building Evera for the long haul in communities we live in.\n\n"
                f"{FOUNDING} Come say hi and see if we're a good fit."
            ),
        }
        return launch.get(
            slug,
            "We're rolling out home cybersecurity built for normal families, not IT departments.\n\n"
            f"{FOUNDING}",
        )

    # --- Set 08 ---
    if slug == "scam-quiz-5":
        return (
            "Could you spot a fake delivery text before you tapped the link?\n\n"
            "Most folks miss one or two on our scam quiz the first time. It's a quick way to see what your household already knows.\n\n"
            "No grades, just practical examples from real cases we see."
        )

    return (
        "Worried about scams hitting your home or your parents?\n\n"
        "Evera helps Kern County and Memphis families stay safer online with clear tools and people you can call."
    )


def closing_cta(item: dict, platform: str) -> str:
    slug = item["slug"]
    campaign = item["campaign"]
    memphis = slug in ("launch-special-l2-mem1", "launch-special-l2-mem2")
    url = link(slug, campaign, platform, memphis=memphis)
    if item["set"] == "08":
        return cta_quiz(url)
    if item["set"] in ("04", "05") and "scam" in slug:
        return cta_ask(url) if item["set"] == "04" else cta_checkup(url)
    if item["set"] == "02":
        return f"See plans and start here: {url}"
    return cta_checkup(url)


def full_caption(item: dict, platform: str) -> str:
    body = caption_for(item).strip()
    cta = closing_cta(item, platform)
    if cta.split(":")[0] in body:
        return f"{body}\n\n{cta}"
    return f"{body}\n\n{cta}"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    rows: list[dict] = []
    readme_sections: list[str] = [
        "# Evera collateral social (review draft)\n",
        "Square images are 1080×1080 JPG. Instagram portrait versions use the same slug with `-ig` before `.jpg` (1080×1350).\n",
        "Rep info, QR codes, and scan prompts were removed from artwork. Six cards used a vertical mailer layout; see manifest `issues`.\n",
        "## Images and captions\n",
    ]

    for item in manifest:
        slug = item["slug"]
        square = item["output_square"]
        portrait = item["output_portrait"]
        campaign = item.get("campaign") or ""
        for platform, image_file, note in (
            ("facebook", square, "Square 1080×1080 — Facebook / TikTok"),
            ("instagram", portrait, "Portrait 1080×1350 — Instagram"),
        ):
            cap = full_caption({**item, "campaign": _campaign_for(item)}, platform)
            rows.append(
                {
                    "set": item["set"],
                    "image_file": image_file,
                    "platform_note": note,
                    "caption": cap,
                    "link": link(slug, _campaign_for(item), platform, memphis=slug in ("launch-special-l2-mem1", "launch-special-l2-mem2")),
                    "hashtags": hashtags_for({**item, "memphis": slug in ("launch-special-l2-mem1", "launch-special-l2-mem2")}),
                }
            )

        cap_fb = full_caption({**item, "campaign": _campaign_for(item)}, "facebook")
        readme_sections.append(f"### `{square}` / `{portrait}`\n\n{cap_fb}\n\n")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["set", "image_file", "platform_note", "caption", "link", "hashtags"],
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    issues = [x for x in manifest if x.get("issues")]
    if issues:
        readme_sections.append("## Cards to review (layout)\n\n")
        for x in issues:
            readme_sections.append(
                f"- `{x['output_square']}` — source `{x['source_file']}` — {', '.join(x['issues'])}\n"
            )

    OUT_README.write_text("".join(readme_sections))
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    print(f"Wrote {OUT_README}")


CAMPAIGN_BY_SET = {
    "01": "free-cyber-checkup",
    "02": "plans-pricing",
    "03": "protect-mom-dad",
    "04": "scam-help",
    "05": "free-scam-guide",
    "06": "talk-to-a-real-person",
    "07": "launch-special",
    "08": "scam-quiz",
}


def _campaign_for(item: dict) -> str:
    return CAMPAIGN_BY_SET.get(item["set"], "free-cyber-checkup")


if __name__ == "__main__":
    main()
