#!/usr/bin/env python3
"""Check the RtPH content against the writing rules.

    python check-content.py

Exits non-zero and prints one line per finding when something fails.

The rules come from the Taut Engineering site's repository instructions
(github.com/Ricyteach/ricyteach.github.io, CLAUDE.md language rules 1 to 10,
with the word lists and reasoning in docs/ai-tics.md). The adaptations for
this site are recorded in CONTENT_GUIDE.md and summarized here:

  - Rule 4 ("X, not Y"), rule 5 (metaphors), rule 9 and rule 10 (large
    language model tics) apply to body prose.
  - Section headings and the hero block are excluded by the owner. Violations
    there are printed as notes so they stay visible without failing the build.
  - The TE first person singular voice rule does NOT apply here. This site is
    written in the second person per CONTENT_GUIDE.md rule 3.
  - TE rules about seals, service pages, Jekyll front matter, publish dates
    and article length are specific to that site and are not checked.
  - Where a TE rule and CONTENT_GUIDE.md disagree, CONTENT_GUIDE.md wins.
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Written as escapes so the characters themselves never appear in this file.
EM_DASH = "—"
EN_DASH = "–"
CURLY = ["‘", "’", "“", "”"]

PROHIBITED_SUBSTRINGS = [
    "would rather",
    "'d rather",
    ", not ",
    "and it matters",
    "and that matters",
    "matters a lot",
    "carries over",
    "carried over",
    "bakes in",
    "baked in",
    "moves the needle",
    "table stakes",
    "growth engine",
    "workhorse",
    "workhorses",
    "bottleneck",
]

PROHIBITED_PATTERNS = [
    (r"\bis not\b[^.!?]{0,80}[.!?]\s+It is\b", "contrast pair across a sentence break"),
    (r"\bnot only\b[^.!?]{0,80}\bbut also\b", "not only, but also construction"),
    (r"\bis not (just|merely|simply)\b[^.!?]{0,60}[,.]\s*(it|that) is\b",
     "contrast pair using not just or not merely"),
    (r"\?\s+(The answer is|Answer:|Simple\.|Yes\.|No\.)", "rhetorical question and answer"),
    # Variants of language rule 4 that the TE checker's sentence-break pattern
    # does not reach. "rather than" is deliberately absent: it is an ordinary
    # comparative and the TE instructions themselves use it throughout.
    (r"\bis not\b[^.!?]{0,80};\s*it is\b", "contrast pair joined by a semicolon"),
    (r"\bis not\b[^.!?]{0,70}\bbut\b", "contrast pair using not X but Y"),
]

# Text that a rule flags but that stays, with the reason recorded. Following
# the precedent in the TE repository's docs/ai-tics.md, where anchor, bridge
# and framework were removed from the lists after testing showed their literal
# use here was genuine. A finding is suppressed when its match falls inside one
# of these strings.
EXCEPTIONS = [
    ('"It will empower demagogues."',
     'quotes the objection verbatim so it matches the section heading "Won\'t '
     'this empower demagogues?", which the owner excluded from editing'),
    ('"Don\'t waste your vote"',
     "quotes a folk saying, and altering a quotation to satisfy a style rule "
     "would misquote it"),
]

# Large language model tics. Failure list, from docs/ai-tics.md on the TE site.
AI_TIC_WORDS = [
    "tapestry", "realm", "mosaic", "symphony", "labyrinth", "beacon",
    "cornerstone", "testament", "cacophony", "kaleidoscope", "odyssey",
    "ecosystem", "crucible", "linchpin", "juggernaut", "watershed",
    "delve", "delves", "delving", "embark", "embarks", "embarking",
    "navigate", "navigates", "navigating", "foster", "fosters", "fostering",
    "elevate", "elevates", "elevating", "harness", "harnesses", "harnessing",
    "streamline", "streamlines", "streamlining", "underscore", "underscores",
    "underscoring", "showcase", "showcases", "showcasing", "unlock",
    "unlocks", "unlocking", "usher", "ushers", "ushering", "illuminate",
    "illuminates", "illuminating", "spearhead", "spearheads",
    "pivotal", "paramount", "unwavering", "meticulous", "meticulously",
    "commendable", "intricate", "intricacies", "seamless", "seamlessly",
    "multifaceted", "myriad", "plethora", "transformative", "unparalleled",
    "cutting-edge", "state-of-the-art", "game-changing", "groundbreaking",
    "invaluable", "indispensable",
    "serves as", "stands as", "represents a",
    "it is important to note", "it is worth noting", "it is worth mentioning",
    "it should be noted", "in today's", "in the realm of", "when it comes to",
    "plays a crucial role", "plays a vital role", "plays a key role",
    "a wide range of", "a wide array of", "navigating the complexities",
    "in conclusion", "in summary", "that being said", "needless to say",
    "at the end of the day", "the fact of the matter",
    "moreover", "furthermore", "additionally,", "notably,", "importantly,",
    "interestingly,", "firstly", "secondly", "thirdly",
    "unleash", "supercharge", "turbocharge", "revolutionize", "empower",
    "leverage", "leveraging", "utilize", "utilizing", "utilization",
    "robust and", "and robust",
]

# Flagged for a human to judge rather than failed automatically. Several have
# an ordinary use in describing the mechanism: a representative holds a proxy,
# a vote carries weight.
REVIEW_WORDS = [
    "carries", "carry", "holds", "flags", "flagged", "surfaces",
    "lands", "gates", "unpacks",
    "bedrock", "resonate", "resonates", "robust", "landscape",
    "foundation of", "cement", "amplify", "amplifies", "core", "key to",
    "pillar", "pillars", "seismic shift", "fault line", "groundwork",
    "scaffold", "scaffolding",
]


def split_body(text):
    """Return (body, headings). Headings are excluded from failures."""
    body_lines = []
    headings = []
    for line in text.splitlines():
        if line.startswith("#"):
            headings.append(line.lstrip("#").strip())
            body_lines.append("")
        elif line.startswith("Tier intro line:"):
            headings.append(line.split(":", 1)[1].strip())
            body_lines.append("")
        else:
            body_lines.append(line)
    return "\n".join(body_lines), headings


def excerpt(text, start, before=45, after=45):
    return " ".join(text[max(0, start - before):start + after].split())


def allowed_spans(text):
    """Character ranges covered by a documented exception."""
    spans = []
    for phrase, _reason in EXCEPTIONS:
        for m in re.finditer(re.escape(phrase), text):
            spans.append((m.start(), m.end()))
    return spans


def scan(label, text, findings, notes, hard=True):
    bucket = findings if hard else notes
    spans = allowed_spans(text)

    def excused(pos):
        return any(a <= pos < b for a, b in spans)

    for ch, name in [(EM_DASH, "em dash"), (EN_DASH, "en dash")]:
        for m in re.finditer(re.escape(ch), text):
            bucket.append("%s: %s: ...%s..." % (label, name, excerpt(text, m.start())))
    for ch in CURLY:
        for m in re.finditer(re.escape(ch), text):
            bucket.append("%s: curly quote: ...%s..." % (label, excerpt(text, m.start())))

    for phrase in PROHIBITED_SUBSTRINGS:
        pattern = r"\b" + re.escape(phrase) + r"\b" if phrase[-1].isalpha() else re.escape(phrase)
        for m in re.finditer(pattern, text, re.I):
            if not excused(m.start()):
                bucket.append("%s: prohibited %r: ...%s..."
                              % (label, phrase, excerpt(text, m.start())))

    for phrase in AI_TIC_WORDS:
        pattern = r"\b" + re.escape(phrase) + r"\b" if phrase[-1].isalpha() else re.escape(phrase)
        for m in re.finditer(pattern, text, re.I):
            if not excused(m.start()):
                bucket.append("%s: large language model tic %r: ...%s..."
                              % (label, phrase, excerpt(text, m.start())))

    for pattern, name in PROHIBITED_PATTERNS:
        for m in re.finditer(pattern, text):
            if not excused(m.start()):
                bucket.append("%s: %s: ...%s..." % (label, name, excerpt(text, m.start(), 40, 70)))

    for m in re.finditer(r"\w+n't\b", text):
        if not excused(m.start()):
            bucket.append("%s: contraction: ...%s..." % (label, excerpt(text, m.start())))

    for word in REVIEW_WORDS:
        for m in re.finditer(r"\b" + re.escape(word) + r"\b", text, re.I):
            notes.append("%s: review %r: ...%s..." % (label, word, excerpt(text, m.start())))


def check_built_pages(findings, notes):
    """Check the rendered pages, which is where the interface wording lives.

    The content files do not contain the button labels, the link text or the
    footer heading, so those would otherwise never be checked. Headings and
    the hero block are stripped first, because the owner excluded them.
    """
    pages = sorted(glob.glob(os.path.join(ROOT, "dist", "*.html")))
    for path in pages:
        html = open(path, encoding="utf-8").read()
        html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
        html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
        html = re.sub(r"<header\b.*?</header>", " ", html, flags=re.S | re.I)
        html = re.sub(r"<h[1-6]\b.*?</h[1-6]>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]*>", " ", html)
        for entity, char in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                             ("&quot;", '"'), ("&#39;", "'")]:
            text = text.replace(entity, char)
        scan(os.path.basename(path), text, findings, notes, hard=True)
    return len(pages)


def main():
    findings = []
    notes = []

    paths = sorted(glob.glob(os.path.join(ROOT, "content", "*.md")))
    for path in paths:
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        body, headings = split_body(text)

        # The hero block and the section headings are excluded by the owner.
        hard = (name != "hero.md")
        scan(name, body, findings, notes, hard=hard)

        for h in headings:
            scan("%s [heading]" % name, h, notes, notes, hard=False)

    page_count = check_built_pages(findings, notes)

    for note in notes:
        print("note:", note)
    for finding in findings:
        print("FINDING:", finding)

    if EXCEPTIONS:
        print("\nDocumented exceptions, kept on purpose:")
        for phrase, reason in EXCEPTIONS:
            print("  %s\n      %s" % (phrase, reason))

    print("\nchecked %d content files and %d built pages, %d findings, %d notes"
          % (len(paths), page_count, len(findings), len(notes)))
    if not page_count:
        print("(run python build.py first to check the rendered pages too)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
