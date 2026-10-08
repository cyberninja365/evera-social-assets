"""Copy and layout metadata for kept PR #2 collateral cards (56 slugs)."""

from __future__ import annotations

from typing import Literal, TypedDict

HeroMode = Literal["photo", "phone", "none"]
LinkGeo = Literal["bakersfield", "memphis"]


class CardContent(TypedDict, total=False):
    set_id: str
    campaign: str
    headline: str
    subhead: str
    bullets: list[str]
    cta_bar: str
    hero_mode: HeroMode
    pricing_line: str
    founding_on_image: bool
    link_geo: LinkGeo


def _card(
    set_id: str,
    campaign: str,
    headline: str,
    subhead: str,
    *,
    bullets: list[str] | None = None,
    cta_bar: str = "Take the free 2-minute Cyber Checkup:",
    hero_mode: HeroMode = "photo",
    pricing_line: str = "",
    founding_on_image: bool = False,
    link_geo: LinkGeo | None = None,
    image_lines: list[str] | None = None,
    phone_caller: str = "",
    phone_hint: str = "",
) -> CardContent:
    out: CardContent = {
        "set_id": set_id,
        "campaign": campaign,
        "headline": headline,
        "subhead": subhead,
        "cta_bar": cta_bar,
        "hero_mode": hero_mode,
    }
    if bullets:
        out["bullets"] = bullets
    if pricing_line:
        out["pricing_line"] = pricing_line
    if founding_on_image:
        out["founding_on_image"] = True
    if link_geo:
        out["link_geo"] = link_geo
    if image_lines:
        out["image_lines"] = image_lines
    if phone_caller:
        out["phone_caller"] = phone_caller
    if phone_hint:
        out["phone_hint"] = phone_hint
    return out


START_CTA = "Start with the free 2-minute Cyber Checkup:"
CHECKUP_CTA = "Take the free 2-minute Cyber Checkup:"
BAK_CTA = "Bakersfield, take the free 2-minute Cyber Checkup:"
MEM_CTA = "Memphis, take the free 2-minute Cyber Checkup:"

FOUNDING_IMAGE = (
    "limited-time Founding Member offer that locks in your pricing for the first 12 months"
)

CARDS: dict[str, CardContent] = {
    # --- 01 Free Cyber Checkup ---
    "free-checkup-18-new": _card(
        "01",
        "free-cyber-checkup",
        "How protected are you?",
        "Your antivirus icon is green. Does that mean the whole house is covered?",
        bullets=[
            "Usually it means one piece is working. The free Cyber Checkup looks at the rest: "
            "your Wi-Fi, your devices and the common ways scams get in."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "free-checkup-4": _card(
        "01",
        "free-cyber-checkup",
        "How healthy is your digital home?",
        "When did you last check on the Wi-Fi you set up years ago?",
        bullets=[
            "The free Cyber Checkup shows where your devices and accounts might be exposed, "
            "in plain language, with a short list of what to fix first."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "free-checkup-9": _card(
        "01",
        "free-cyber-checkup",
        "Are you actually protected?",
        "Kids on tablets, bills paid online, and a router blinking in the closet. Sound familiar?",
        bullets=[
            "That's a lot of ways in for a scammer. The free Cyber Checkup walks through the basics "
            "and gives you simple next steps you can keep."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    # --- 02 Plans & Pricing ---
    "plans-pricing-10-new": _card(
        "02",
        "plans-pricing",
        "Home cybersecurity, handled.",
        "Businesses have someone watching their computers. Why shouldn't your family?",
        bullets=[
            "Evera's team monitors your home computers, blocks threats and picks up the phone "
            "when something looks off. Plans start at $24/mo."
        ],
        cta_bar=START_CTA,
        pricing_line="Plans from $24/mo",
    ),
    "plans-pricing-11-new": _card(
        "02",
        "plans-pricing",
        "Serious protection doesn't have to cost a fortune.",
        "Think real protection for the house costs a fortune?",
        bullets=[
            "Personal is $24/mo, Home+ is $49/mo and Family is $74/mo, all monthly. Right now we also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        pricing_line="Personal $24/mo (regular $29) · Home+ $49/mo (regular $59) · Family $74/mo (regular $89)",
        founding_on_image=True,
        image_lines=["Monthly plans for real households."],
    ),
    "plans-pricing-11": _card(
        "02",
        "plans-pricing",
        "Keep their world safer online.",
        "Homework, games, group chats. How much of your kids' day happens online now?",
        bullets=[
            "We watch the family computers for threats and harmful sites, and you can call a real person "
            "when something seems wrong."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "plans-pricing-12": _card(
        "02",
        "plans-pricing",
        "A safer, brighter tomorrow starts at home.",
        "Wish someone could just remote in and fix the computer for you?",
        bullets=[
            "Remote Tech Support is $49/mo, and our U.S. team connects to the computer and handles it with you on the phone."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Remote Tech Support $49/mo",
    ),
    "plans-pricing-15-new": _card(
        "02",
        "plans-pricing",
        "A brighter childhood online.",
        "Did your kid just get their first laptop?",
        bullets=[
            "Set it up right from day one. Our team keeps an eye on it for threats and risky sites, "
            "and you get someone to call when you're not sure."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "plans-pricing-15": _card(
        "02",
        "plans-pricing",
        "New home. New risks.",
        "Just moved in and hooked everything up to the new Wi-Fi?",
        bullets=[
            "A move is a good time to change the router password, update every computer and check what's connected. "
            "The free Cyber Checkup tells you where to start."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "plans-pricing-16-new": _card(
        "02",
        "plans-pricing",
        "Cybersecurity starts at home.",
        "How many computers are on your Wi-Fi right now?",
        bullets=[
            "Each one is a way in for a scammer. Evera's team watches them for you, and Home+ covers a busy household for $49/mo."
        ],
        cta_bar=START_CTA,
        pricing_line="Home+ $49/mo",
    ),
    "plans-pricing-16": _card(
        "02",
        "plans-pricing",
        "Taking a trip?|Keep your digital life protected.",
        "Heading out of town and planning to live on hotel Wi-Fi?",
        bullets=["Internet Protection is $14/mo and adds a layer when you're off your home network."],
        cta_bar=START_CTA,
        pricing_line="Internet Protection $14/mo",
    ),
    "plans-pricing-17-new": _card(
        "02",
        "plans-pricing",
        "Antivirus isn't enough.",
        "Is the antivirus that came with your laptop the only thing protecting it?",
        bullets=[
            "Antivirus can't pick up the phone when a scammer is calling Mom. We watch the computers in your home "
            "and we answer when you call."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "plans-pricing-17": _card(
        "02",
        "plans-pricing",
        "Stronger communities are safer communities.",
        "Ever notice the same scam text going around your whole neighborhood group chat?",
        bullets=[
            "We help local households stay a step ahead of it, with monitoring on your computers and a real person to call. "
            "Plans start at $24/mo."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Plans from $24/mo",
    ),
    "plans-pricing-18": _card(
        "02",
        "plans-pricing",
        "They count on you.|Keep them safe online too.",
        "The dog counts on you. So do the kids and the computer everyone shares.",
        bullets=[
            "Personal $24/mo, Home+ $49/mo, Family $74/mo. Add-ons are an extra computer $15/mo, Internet Protection $14/mo, "
            "Remote Tech Support $49/mo and Identity Protection $19/mo, all monthly. We also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        hero_mode="none",
        pricing_line="Personal $24 · Home+ $49 · Family $74/mo",
        founding_on_image=True,
    ),
    "plans-pricing-40": _card(
        "02",
        "plans-pricing",
        "They took care of you.|Now you can help protect them.",
        "Are your parents still calling you every time a pop-up appears?",
        bullets=[
            "Evera gives them their own team to call, and we watch their computer for threats. "
            "Identity Protection is available for $19/mo."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Identity Protection $19/mo",
    ),
    "plans-pricing-6": _card(
        "02",
        "plans-pricing",
        "Help keep your family safer online.",
        "School, streaming, gaming and social media, all on the same Wi-Fi?",
        bullets=[
            "We keep watch on the family computers and you get real people to call when something feels wrong. "
            "Personal starts at $24/mo."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Personal from $24/mo",
    ),
    "plans-pricing-7-new": _card(
        "02",
        "plans-pricing",
        "Your home IT & security team has your back.",
        "Businesses have an IT department. Who does your family call?",
        bullets=[
            "That's us. Our U.S.-based team monitors your home computers and helps when you call. Home+ is $49/mo, and we have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        pricing_line="Home+ $49/mo",
        founding_on_image=True,
    ),
    "plans-pricing-7": _card(
        "02",
        "plans-pricing",
        "Protect what matters most.",
        "Two adults, a teenager and a computer nobody has updated in months?",
        bullets=[
            "Home+ covers a household like that for $49/mo, with our team watching for threats and answering when you call."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Home+ $49/mo",
    ),
    "plans-pricing-9-new": _card(
        "02",
        "plans-pricing",
        "Everything connected.|Better protected.",
        "Grandma's laptop, your work computer and the gaming PC in the back room. Who's watching all of them?",
        bullets=[
            "Family is $74/mo and covers the whole house. We also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        pricing_line="Family $74/mo",
        founding_on_image=True,
    ),
    # --- 03 Protect Mom & Dad ---
    "protect-mom-dad-14-2": _card(
        "03",
        "protect-mom-dad",
        "Keep the ones who took care of you safe online.",
        "Ever get a screenshot from Mom with just \"Is this real?\"",
        bullets=[
            "Evera gives your parents their own U.S.-based team to ask, so you're not troubleshooting after dinner every night."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-14": _card(
        "03",
        "protect-mom-dad",
        "Who's protecting Mom & Dad online?",
        "Who do your parents call when a scary message pops up?",
        bullets=[
            "If the answer is you, there's a better option. We watch their computer and they can call us first, "
            "any time something looks off."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-19-new": _card(
        "03",
        "protect-mom-dad",
        "Peace of mind lives here.",
        "Do your folks forward every chain email \"just in case\"?",
        bullets=[
            "Now they can forward the suspicious ones to us instead. We'd rather answer a quick question than help after money is gone."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-19": _card(
        "03",
        "protect-mom-dad",
        "A safer online world for their brighter tomorrow.",
        "Are the grandkids on Grandma's computer every time they visit?",
        bullets=[
            "We keep that computer watched and updated, so a game download doesn't turn into a problem for everyone."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-20-new": _card(
        "03",
        "protect-mom-dad",
        "Give Mom & Dad something better than another tech-support phone call.",
        "Dad fixed the printer himself and installed three toolbars along the way?",
        bullets=[
            "Give him a team that can clean it up and that he can call without feeling silly."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-20": _card(
        "03",
        "protect-mom-dad",
        "Local homes. Stronger together.",
        "Does the same scam text make the rounds on your street every few weeks?",
        bullets=[
            "Teach your parents one rule: if someone wants control of the screen, hang up and call us."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-21-new-dad": _card(
        "03",
        "protect-mom-dad",
        "Who does he call?",
        "Dad got a call about his \"compromised account\" and almost read them a code?",
        bullets=[
            "He can always hang up. With Evera, he can call us and check the story before he does anything."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "protect-mom-dad-21-new-mom": _card(
        "03",
        "protect-mom-dad",
        "Who does she call?",
        "Something weird popped up on Mom's computer, and she called you first. Again?",
        bullets=[
            "What if she had a number where someone who knows computers actually answers? That's what we do."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "protect-mom-dad-26": _card(
        "03",
        "protect-mom-dad",
        "They want remote access to your computer.",
        "Live in Kern County while your parents are across town or across the state?",
        bullets=[
            "If anyone asks them for remote access, the answer is no. They can call our team instead and we'll check it with them."
        ],
        cta_bar=CHECKUP_CTA,
        link_geo="bakersfield",
    ),
    "protect-mom-dad-36": _card(
        "03",
        "protect-mom-dad",
        "Protect what matters most.",
        "Your parent's on the phone with a \"bank investigator\" who wants gift cards?",
        bullets=[
            "That's a scam every time. Save our number in their phone so they have someone to call before they buy anything."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "protect-mom-dad-37": _card(
        "03",
        "protect-mom-dad",
        "You can't always be there.|Evera can help.",
        "Can't be at Mom's house every time something goes wrong with the computer?",
        bullets=[
            "We can help remotely, and she gets a real person on the phone instead of a chatbot."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-38": _card(
        "03",
        "protect-mom-dad",
        "Help protect Mom & Dad from scams.",
        "How many times have you explained two-step codes to Dad?",
        bullets=[
            "Our team will do it as many times as he needs, patiently, and help him spot a scam call before it costs him."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-39": _card(
        "03",
        "protect-mom-dad",
        "Keep their digital world brighter tomorrow.",
        "You can't stand between your parents and every scammer who calls.",
        bullets=[
            "You can give them a team that watches their computer and answers the phone when you're not around."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    "protect-mom-dad-8-new": _card(
        "03",
        "protect-mom-dad",
        "Real humans. Real help.",
        "Does Mom still keep her passwords on a sticky note by the monitor?",
        bullets=[
            "Instead of playing unpaid IT, give her a team that answers the phone and helps her check a message before she clicks."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    # --- 04 Scam Help ---
    "scam-help-23-1": _card(
        "04",
        "scam-help",
        "Fraud alert?|It could be a scam.",
        "Did a \"suspicious charge\" text show up while you were in line at the store?",
        bullets=[
            "Fake fraud alerts want you to tap before you think. Don't use the link. Call your bank on the number on the back of your card."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "scam-help-23-2": _card(
        "04",
        "scam-help",
        "Your account has been locked.",
        "Got a text saying your account is locked and you need to click right now?",
        bullets=[
            "That rush is the trick. Close the message and log in the way you normally do. If it's real, you'll see it there."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "scam-help-24": _card(
        "04",
        "scam-help",
        "Microsoft is calling about a virus on your computer... right?",
        "Did \"Microsoft\" call to say your computer has a virus?",
        bullets=[
            "Hang up. Microsoft doesn't call people about viruses. Don't install anything or let them connect to your computer."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "scam-help-33": _card(
        "04",
        "scam-help",
        "Not sure it's real? Ask us.",
        "Strange email, odd text or a pop-up you don't trust?",
        bullets=["Evera customers can send it to us and ask before they click. That one step stops a lot of trouble."],
        cta_bar=CHECKUP_CTA,
        hero_mode="none",
    ),
    "scam-help-34": _card(
        "04",
        "scam-help",
        "Stop. Verify. Ask.",
        "Utility company threatening a shutoff unless you pay with crypto or gift cards today?",
        bullets=["That's a scam. Call the number on your last bill, not the one in the message."],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "scam-help-35": _card(
        "04",
        "scam-help",
        "When in doubt, ask Evera.",
        "Feel rushed, scared or surprised by a call or text?",
        bullets=[
            "Those feelings are what scammers are after. Pause, and ask someone you trust before you pay, install anything or share a code."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="none",
    ),
    # --- 05 Free Scam Guide ---
    "free-scam-guide-22": _card(
        "05",
        "free-scam-guide",
        "Your bank is calling.|Or are they?",
        "Your phone says your bank is calling. Is it really them?",
        bullets=[
            "Caller ID can be faked, and scammers may already know your name. Hang up and call the number on the back of your card."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-27": _card(
        "05",
        "free-scam-guide",
        "A text from your child?|It could be a scam.",
        "A text from a new number says it's your kid with a broken phone and needs money?",
        bullets=["Call your child on the number you already have before you send anything."],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-28": _card(
        "05",
        "free-scam-guide",
        "It sounds exactly like your child.",
        "Would you know if a voice on the phone wasn't really your child?",
        bullets=[
            "Scammers can copy voices from short clips online. Hang up and call your child back on their real number."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-29": _card(
        "05",
        "free-scam-guide",
        "They asked for gift cards?",
        "Has someone on the phone asked you to pay with gift cards?",
        bullets=[
            "That's a scam every time. No real company, bank or government office takes payment that way. Hang up."
        ],
        cta_bar=BAK_CTA,
        hero_mode="phone",
        link_geo="bakersfield",
    ),
    "free-scam-guide-30-1-dad": _card(
        "05",
        "free-scam-guide",
        "Dad says the bank called...",
        "Did Dad get a call from \"the bank\" asking for the code they just texted him?",
        bullets=[
            "That code is the key to his account. A real bank won't ask for it. Hang up and call the number on his card."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-30-1-mom": _card(
        "05",
        "free-scam-guide",
        "Mom says the bank called...",
        "Did Mom get a call from \"the bank\" asking for the code they just texted her?",
        bullets=[
            "That code is the key to her account. A real bank won't ask for it. Hang up and call the number on her card."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-30-2": _card(
        "05",
        "free-scam-guide",
        "They already know your name.|Now they just need the code.",
        "The caller knew your name and your bank. Does that make it real?",
        bullets=[
            "No. That information is easy to find. Never share a code someone texted you, no matter what they already know."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    "free-scam-guide-31": _card(
        "05",
        "free-scam-guide",
        "That delivery text?|It might be fake.",
        "Got a text that your package is on hold?",
        bullets=["Don't tap the link. Check the order on the store's own site or app."],
        cta_bar=CHECKUP_CTA,
        hero_mode="phone",
    ),
    # --- 06 ---
    "talk-to-a-real-person-8": _card(
        "06",
        "talk-to-a-real-person",
        "Protect the ones you care about.",
        "Tired of chatbots that send you in circles when the computer acts up?",
        bullets=[
            "With Evera you call a real person in the U.S., whether it's an error message or a text that just feels wrong."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    # --- 07 Launch ---
    "launch-special-l1": _card(
        "07",
        "launch-special",
        "Evera has arrived.",
        "New in town, and the scams sure aren't.",
        bullets=[
            "Evera's team watches the computers in your home, blocks threats and answers the phone. We also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        founding_on_image=True,
    ),
    "launch-special-l10": _card(
        "07",
        "launch-special",
        "Today's cyber threats are real.|So is your protection.",
        "Scams, malware and stolen passwords. Who's watching for them at your house?",
        bullets=[
            "That's our job. We monitor your home computers and help when something looks off."
        ],
        cta_bar=CHECKUP_CTA,
        hero_mode="none",
    ),
    "launch-special-l2-bak": _card(
        "07",
        "launch-special",
        "Bakersfield, meet Evera.",
        "Bakersfield, who do you call when the family computer starts acting strange?",
        bullets=[
            "Evera is now serving Kern County. Our team watches your home computers and answers the phone. We also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        founding_on_image=True,
        link_geo="bakersfield",
    ),
    "launch-special-l2-mem1": _card(
        "07",
        "launch-special",
        "Memphis, meet Evera.",
        "Memphis, did another sketchy text show up on your phone today?",
        bullets=[
            "Evera is now serving Memphis households. Personal $24/mo, Home+ $49/mo, Family $74/mo, all monthly, with a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=CHECKUP_CTA,
        pricing_line="Personal $24 · Home+ $49 · Family $74/mo",
        founding_on_image=True,
        link_geo="memphis",
    ),
    "launch-special-l4": _card(
        "07",
        "launch-special",
        "Better protection for what matters.",
        "Been meaning to deal with the old laptop in the guest room?",
        bullets=[
            "Start with a free checkup, then pick a plan. We also have a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        founding_on_image=True,
    ),
    "launch-special-l5": _card(
        "07",
        "launch-special",
        "It's more than just antivirus.",
        "Tired of piecing together five different security subscriptions?",
        bullets=[
            "Evera's team handles the monitoring, protection and support for you. Personal $24/mo, Home+ $49/mo, Family $74/mo, with a "
            + FOUNDING_IMAGE
            + "."
        ],
        cta_bar=START_CTA,
        pricing_line="Personal $24 · Home+ $49 · Family $74/mo",
        founding_on_image=True,
    ),
    "launch-special-l6": _card(
        "07",
        "launch-special",
        "Cybersecurity built for your home.",
        "Wondering what we actually do?",
        bullets=[
            "We watch the computers in your home, block threats and pick up the phone when something seems off. "
            "You talk to a real person in the U.S."
        ],
        cta_bar=CHECKUP_CTA,
    ),
    # --- 08 ---
    "scam-quiz-5": _card(
        "08",
        "scam-quiz",
        "Could you spot a scam before you clicked?",
        "Could you spot a fake delivery text before you tapped the link?",
        bullets=[
            "The free Cyber Checkup asks a few quick questions and shows where your household might be caught off guard."
        ],
        cta_bar=CHECKUP_CTA,
    ),
}


PHONE_UI: dict[str, tuple[str, str]] = {
    "free-scam-guide-22": ("Your Bank", "Caller ID can be faked. Hang up and call the number on your card."),
    "scam-help-23-1": ("Fraud alert", "Suspicious charge detected. Was this you?"),
    "scam-help-23-2": ("Account notice", "Your account has been locked. Verify now."),
    "scam-help-24": ("Tech support", "We detected a problem on your computer."),
    "scam-help-34": ("Utility company", "Shutoff scheduled unless you pay today."),
    "free-scam-guide-27": ("New number", "Hi Mom, new phone. Need help."),
    "free-scam-guide-28": ("Family call", "It's me. I need help right away."),
    "free-scam-guide-29": ("Caller", "Pay with gift cards to fix this."),
    "free-scam-guide-30-1-dad": ("Your Bank", "Enter the code we texted you."),
    "free-scam-guide-30-1-mom": ("Your Bank", "Enter the code we texted you."),
    "free-scam-guide-30-2": ("Your Bank", "We already verified your name."),
    "free-scam-guide-31": ("Delivery", "Package on hold. Tap to update."),
    "protect-mom-dad-21-new-dad": ("Bank alert", "Compromised account. Read us the code."),
    "protect-mom-dad-21-new-mom": ("Security alert", "Pop-up on your computer. Call now."),
    "protect-mom-dad-36": ("Bank investigator", "Buy gift cards to secure funds."),
}


def get_card(slug: str) -> CardContent:
    if slug not in CARDS:
        raise KeyError(f"Unknown collateral slug: {slug}")
    c: CardContent = dict(CARDS[slug])
    sub = c.get("subhead", "")
    if "image_lines" not in c:
        lines: list[str] = []
        if sub and len(sub) <= 95:
            lines.append(sub)
        elif c.get("hero_mode") == "none":
            for bullet in c.get("bullets", [])[:2]:
                if len(bullet) <= 120:
                    lines.append(bullet)
        c["image_lines"] = lines
    if c.get("hero_mode") == "phone":
        caller, hint = PHONE_UI.get(slug, ("Unknown caller", "Hang up if it feels rushed or scary."))
        c.setdefault("phone_caller", caller)
        c.setdefault("phone_hint", hint)
    return c


def all_slugs() -> list[str]:
    return sorted(CARDS.keys())
