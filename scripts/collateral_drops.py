"""Cards removed per Evera Marketing review (PR #2)."""

from __future__ import annotations

# Square JPG basename without extension (set-slug)
DROP_OUTPUT_BASENAMES = {
    "03-protect-mom-dad-20",
    "01-free-checkup-6-new",
    "01-free-checkup-13",
    "02-plans-pricing-1",
    "02-plans-pricing-2",
    "02-plans-pricing-3",
    "04-scam-help-25",
    "05-free-scam-guide-30-3",
    "07-launch-special-l2-mem2",
    "07-launch-special-l3",
    "07-launch-special-l7",
    "07-launch-special-l8",
    "07-launch-special-l9",
    "05-free-scam-guide-22-amazon",
    "05-free-scam-guide-22-apple",
    "05-free-scam-guide-22-bofa",
    "05-free-scam-guide-22-capitalone",
    "05-free-scam-guide-22-chase",
    "05-free-scam-guide-22-firstsouthfinancial",
    "05-free-scam-guide-22-irs",
    "05-free-scam-guide-22-ms",
    "05-free-scam-guide-22-pp",
    "05-free-scam-guide-22-regions",
    "05-free-scam-guide-22-ssa",
    "05-free-scam-guide-22-truist",
    "05-free-scam-guide-22-usbank",
    "05-free-scam-guide-22-wellsfargo",
    "05-free-scam-guide-22-bankofthesierra",
    "05-free-scam-guide-22-valleystrong",
    "05-free-scam-guide-22-firsthorizon",
    "05-free-scam-guide-22-ofcu",
}


def slug_from_basename(base: str) -> str:
    return base.split("-", 1)[1]


DROP_SLUGS = {slug_from_basename(b) for b in DROP_OUTPUT_BASENAMES}


def is_dropped_slug(slug: str) -> bool:
    return slug in DROP_SLUGS


def is_dropped_basename(base: str) -> bool:
    return base in DROP_OUTPUT_BASENAMES
