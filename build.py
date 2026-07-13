#!/usr/bin/env python3
"""Build script for Restore the People's House.

Python standard library only. No packages to install.

    python build.py

Reads the markdown in content/, writes the finished site to dist/,
and FAILS the build if:
  - the section order in the tier files disagrees with CONTENT_GUIDE.md,
  - any accordion section is missing a slug in the SLUGS table below,
  - any em dash, en dash, curly quote, or single-quote delimiter
    appears in the rendered text of the built pages.
"""

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
SRC = ROOT / "src"
DIST = ROOT / "dist"

SITE_TITLE = "Restore the People's House"

# ---------------------------------------------------------------------------
# SLUGS: the stable deep-link ids, one per accordion section.
#
# The key must match the section's ### heading in the tier file EXACTLY.
# The value is the slug used in URLs, e.g. #gerrymandering.
#
# These are hand-assigned on purpose: a slug never changes even if a heading
# is reworded, so links already shared in emails and posts keep working.
# If you add a new section, add a line here; the build will remind you.
# If you reword a heading, update the KEY here but KEEP the same slug.
# ---------------------------------------------------------------------------
SLUGS = {
    # Tier 1: Why it feels broken
    "Why your vote feels like it doesn't matter": "vote-doesnt-matter",
    "Why you can't vote third party without throwing your vote away": "wasted-vote",
    "Why bipartisan reforms always die in Washington": "bipartisan-reforms-die",
    "Why your representative ignores you between elections": "ignored-between-elections",
    "Why scandals never seem to have consequences": "scandals",
    "Why gerrymandering keeps winning": "gerrymandering",
    "Why moderates always lose": "moderates",
    # Tier 2: The proposal
    "The whole proposal in 90 seconds": "the-proposal",
    "How the portable vote works": "portable-vote",
    "What stays exactly the same": "what-stays-the-same",
    "Is this a fringe idea?": "fringe-idea",
    "Won't this empower demagogues?": "demagogues",
    "One election cycle, played out": "one-cycle",
    # Tier 3: What's in it for you
    "If you're a conservative": "for-conservatives",
    "If you're a progressive": "for-progressives",
    "If you're an independent or politically homeless": "for-independents",
    "If you're religious": "for-religious-voters",
    "If you've lost faith in both parties": "lost-faith",
    "What the Founders actually designed": "founders-design",
    # Tier 4: What would change
    "Impeachment gets its teeth back": "impeachment",
    "The donor and lobbying math": "lobbying-math",
    "Third parties get a real path": "third-parties",
    "Fame stops passing for support": "fame-audit",
    "The job becomes doable by normal people": "normal-people",
    # Tier 5: The skeptic's corner
    "If most voters never touch it, how does it do anything?": "low-participation",
    "Won't real-time pressure kill political courage?": "political-courage",
    "Could it be hacked or coerced?": "security",
    "Doesn't this violate one person, one vote?": "one-person-one-vote",
    "Can 6,500 people actually function as a legislature?": "chamber-size",
    "What would it cost?": "cost",
    "What could actually go wrong": "what-could-go-wrong",
    "How could this ever pass?": "how-it-passes",
}


def fail(msg):
    print("\nBUILD FAILED\n" + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Markdown (deliberately tiny)
#
# The content uses only paragraphs, **bold**, and *italic*. This renderer
# handles exactly that and nothing else, so no markdown library can ever
# "helpfully" convert quotes or dashes to typographic characters.
# ---------------------------------------------------------------------------

def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    return t


def paragraphs(body):
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if not block or block == "---":
            continue
        out.append("<p>%s</p>" % inline(re.sub(r"\s*\n\s*", " ", block)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Content parsing
# ---------------------------------------------------------------------------

def parse_hero():
    text = (CONTENT / "hero.md").read_text(encoding="utf-8")
    parts = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            parts[current] = []
        elif line.startswith("# ") or line.strip() == "---":
            current = None
        elif current is not None:
            parts[current].append(line)
    def body(name):
        if name not in parts:
            fail("hero.md is missing the \"## %s\" heading." % name)
        return "\n".join(parts[name]).strip()
    return {
        "title": body("Title"),
        "tagline": body("Tagline"),
        "statement": body("Hero statement"),
        "about": body("Who is behind this"),
    }


def parse_tier(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"# Tier (\d+): (.+)", text)
    if not m:
        fail("%s must start with \"# Tier N: Title\"." % path.name)
    num, title = m.group(1), m.group(2).strip()
    mi = re.search(r"^Tier intro line: (.+)$", text, re.M)
    if not mi:
        fail("%s is missing its \"Tier intro line:\"." % path.name)
    intro = mi.group(1).strip()
    sections = []
    chunks = re.split(r"^### ", text, flags=re.M)[1:]
    for chunk in chunks:
        heading, _, body = chunk.partition("\n")
        heading = heading.strip()
        body = re.sub(r"^\s*---\s*$", "", body, flags=re.M).strip()
        sections.append({"heading": heading, "body": body})
    return {"num": num, "title": title, "intro": intro, "sections": sections}


def parse_guide_order():
    text = (ROOT / "CONTENT_GUIDE.md").read_text(encoding="utf-8")
    try:
        block = text.split("## Section order (authoritative)")[1]
        block = block.split("## ")[0]
    except IndexError:
        fail("CONTENT_GUIDE.md is missing the \"## Section order (authoritative)\" heading.")
    tiers = []
    for line in block.splitlines():
        m = re.match(r"\*\*Tier (\d+): (.+)\*\*", line.strip())
        if m:
            tiers.append({"num": m.group(1), "title": m.group(2).strip(), "sections": []})
            continue
        m = re.match(r"\d+\.\s+(.+)", line.strip())
        if m and tiers:
            tiers[-1]["sections"].append(m.group(1).strip())
    return tiers


def check_order(tiers, guide):
    problems = []
    if len(tiers) != len(guide):
        problems.append("Guide lists %d tiers; found %d tier files." % (len(guide), len(tiers)))
    for t, g in zip(tiers, guide):
        if t["title"] != g["title"]:
            problems.append("Tier %s title mismatch: file says \"%s\", guide says \"%s\"."
                            % (t["num"], t["title"], g["title"]))
        file_heads = [s["heading"] for s in t["sections"]]
        if file_heads != g["sections"]:
            problems.append(
                "Tier %s section order disagrees with CONTENT_GUIDE.md.\n"
                "  In tier%s.md: %s\n  In guide:    %s"
                % (t["num"], t["num"], file_heads, g["sections"]))
    if problems:
        fail("The tier files and CONTENT_GUIDE.md are out of sync. The guide is the\n"
             "source of truth: fix whichever side is wrong, keep both matching.\n\n"
             + "\n".join(problems))


def check_slugs(tiers):
    missing = []
    for t in tiers:
        for s in t["sections"]:
            if s["heading"] not in SLUGS:
                missing.append(s["heading"])
    if missing:
        fail("These section headings have no slug in the SLUGS table in build.py.\n"
             "Add one line per heading (the slug is the stable #anchor for deep links):\n\n"
             + "\n".join("  \"%s\": \"your-slug-here\"," % h for h in missing))
    used = {s["heading"] for t in tiers for s in t["sections"]}
    stale = [h for h in SLUGS if h not in used]
    if stale:
        print("NOTE: SLUGS entries with no matching section (retired or reworded headings):")
        for h in stale:
            print("  - " + h)


def slugify(name):
    s = name.lower().replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def parse_essay():
    text = (CONTENT / "essay.md").read_text(encoding="utf-8")
    title = None
    subtitle = None
    preface = []
    chapters = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block == "---":
            continue
        if block.startswith("# ") and title is None:
            title = block[2:].strip()
            continue
        m = re.match(r"## ([IVXLC]+)\. (.+)", block)
        if m:
            chapters.append({"num": m.group(1), "name": m.group(2).strip(),
                             "slug": slugify(m.group(2)), "blocks": []})
            continue
        if block.startswith("## ") and subtitle is None:
            subtitle = block[3:].strip()
            continue
        if chapters:
            chapters[-1]["blocks"].append(block)
        else:
            preface.append(block)
    return {"title": title, "subtitle": subtitle, "preface": preface, "chapters": chapters}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

PEDIMENT_SVG = """<svg class="pediment" viewBox="0 0 120 66" aria-hidden="true" focusable="false">
<g fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="square">
<path d="M8 27 L60 5 L112 27"/>
<line x1="14" y1="27" x2="106" y2="27"/>
<line x1="24" y1="35" x2="24" y2="51"/>
<line x1="42" y1="35" x2="42" y2="51"/>
<line x1="60" y1="35" x2="60" y2="51"/>
<line x1="78" y1="35" x2="78" y2="51"/>
<line x1="96" y1="35" x2="96" y2="51"/>
<line x1="14" y1="57" x2="106" y2="57"/>
<line x1="6" y1="64" x2="114" y2="64"/>
</g>
</svg>"""


def page_head(title, description, extra=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/SourceSerif4-Roman-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/style.css">
%s</head>
""" % (html.escape(title), html.escape(description), extra)


def footer_html(hero, home_link=False):
    back = ""
    if home_link:
        back = '\n<p class="footer-back"><a href="index.html">Back to the sections</a></p>'
    return """<footer class="site-footer">
<div class="footer-inner">
<h2>Who is behind this</h2>
%s%s
<!-- PLACEHOLDER (not rendered): when a follow/updates link exists, add it here,
     e.g. <p class="footer-follow"><a href="...">Follow updates</a></p> -->
</div>
</footer>""" % (paragraphs(hero["about"]), back)


def item_html(heading, body, slug):
    return """<section class="item" id="%(slug)s">
<h3 class="item-heading">
<button type="button" class="item-toggle" id="%(slug)s-btn" aria-expanded="false" aria-controls="%(slug)s-panel">
<span class="item-title">%(title)s</span>
<span class="item-icon" aria-hidden="true"></span>
</button>
</h3>
<div class="item-panel" id="%(slug)s-panel" role="region" aria-labelledby="%(slug)s-btn">
<div class="item-panel-inner">
%(body)s
<p class="copy-row"><button type="button" class="copy-link" data-slug="%(slug)s" aria-label="Copy a direct link to this section">Copy link</button></p>
</div>
</div>
</section>""" % {"slug": slug, "title": inline(heading), "body": paragraphs(body)}


def tier_html(tier):
    items = "\n".join(item_html(s["heading"], s["body"], SLUGS[s["heading"]])
                      for s in tier["sections"])
    return """<section class="tier" aria-labelledby="tier-%(num)s-title">
<header class="tier-head">
<p class="tier-kicker">Tier %(num)s</p>
<h2 id="tier-%(num)s-title">%(title)s</h2>
<p class="tier-intro">%(intro)s</p>
</header>
<div class="tier-items">
%(items)s
</div>
</section>""" % {"num": tier["num"], "title": inline(tier["title"]),
                 "intro": inline(tier["intro"]), "items": items}


def build_index(hero, tiers):
    tiers_html = "\n".join(tier_html(t) for t in tiers)
    return page_head(SITE_TITLE, hero["tagline"]) + """<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="hero">
%(pediment)s
<h1>%(title)s</h1>
<p class="tagline">%(tagline)s</p>
<div class="hero-statement">
%(statement)s
</div>
</header>
<main id="main">
%(tiers)s
<section class="essay-cta" aria-label="The full argument">
<a class="essay-link" href="essay.html">Read the full argument</a>
</section>
</main>
%(footer)s
<script src="assets/site.js"></script>
</body>
</html>
""" % {
        "pediment": PEDIMENT_SVG,
        "title": inline(hero["title"]),
        "tagline": inline(hero["tagline"]),
        "statement": paragraphs(hero["statement"]),
        "tiers": tiers_html,
        "footer": footer_html(hero),
    }


def build_essay(hero, essay):
    chapters = []
    for ch in essay["chapters"]:
        body = "\n".join("<p>%s</p>" % inline(re.sub(r"\s*\n\s*", " ", b)) for b in ch["blocks"])
        chapters.append(
            '<section class="chapter" aria-labelledby="%(slug)s-h">\n'
            '<h2 id="%(slug)s"><span id="%(slug)s-h"><span class="chapter-num">%(num)s.</span> %(name)s</span></h2>\n'
            "%(body)s\n</section>"
            % {"slug": ch["slug"], "num": ch["num"], "name": inline(ch["name"]), "body": body})
    preface = "\n".join("<p>%s</p>" % inline(re.sub(r"\s*\n\s*", " ", b)) for b in essay["preface"])
    return page_head("%s | %s" % (essay["subtitle"], SITE_TITLE), hero["tagline"]) + """<body class="essay-page">
<a class="skip-link" href="#main">Skip to content</a>
<header class="essay-header">
<p class="crumb"><a href="index.html">Back to the sections</a></p>
%(pediment)s
<h1>%(title)s</h1>
<p class="subtitle">%(subtitle)s</p>
<div class="preface">
%(preface)s
</div>
</header>
<main id="main" class="essay-body">
%(chapters)s
</main>
%(footer)s
</body>
</html>
""" % {
        "pediment": PEDIMENT_SVG,
        "title": inline(essay["title"]),
        "subtitle": inline(essay["subtitle"]),
        "preface": preface,
        "chapters": "\n".join(chapters),
        "footer": footer_html(hero, home_link=True),
    }


# ---------------------------------------------------------------------------
# Hygiene check: no em/en dashes, no curly quotes, no single-quote delimiters
# in the rendered text of the built pages.
# ---------------------------------------------------------------------------

BANNED = [
    ("—", "em dash"),
    ("–", "en dash"),
    ("‘", "left curly single quote"),
    ("’", "right curly single quote"),
    ("“", "left curly double quote"),
    ("”", "right curly double quote"),
]


def visible_text(page):
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<[^>]*>", " ", s)
    return html.unescape(s)


def hygiene_check(name, page):
    text = visible_text(page)
    errors = []
    for ch, label in BANNED:
        for m in re.finditer(re.escape(ch), text):
            ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            errors.append("%s: %s near: ...%s..." % (name, label, ctx.strip()))
    # A straight single quote opening a quotation (start of line, after a space,
    # or after a bracket or double quote) is a delimiter; apostrophes inside or
    # at the end of words are fine.
    for m in re.finditer(r"(?:^|[\s(\[{\"])'", text):
        ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        errors.append("%s: single quote used as a quote delimiter near: ...%s..." % (name, ctx.strip()))
    return errors


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def main():
    hero = parse_hero()
    tiers = [parse_tier(CONTENT / ("tier%d.md" % i)) for i in range(1, 6)]
    guide = parse_guide_order()
    check_order(tiers, guide)
    check_slugs(tiers)
    essay = parse_essay()

    total = sum(len(t["sections"]) for t in tiers)
    pages = {
        "index.html": build_index(hero, tiers),
        "essay.html": build_essay(hero, essay),
    }

    errors = []
    for name, page in pages.items():
        errors.extend(hygiene_check(name, page))
    if errors:
        fail("Typography hygiene check failed (em/en dashes and single-quote\n"
             "delimiters are banned in rendered output):\n\n" + "\n".join(errors))

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    for name, page in pages.items():
        with open(DIST / name, "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
    shutil.copy(SRC / "style.css", DIST / "assets" / "style.css")
    shutil.copy(SRC / "site.js", DIST / "assets" / "site.js")
    shutil.copy(SRC / "favicon.svg", DIST / "assets" / "favicon.svg")
    shutil.copytree(SRC / "fonts", DIST / "assets" / "fonts")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    print("Built dist/ with %d accordion sections across %d tiers, plus the essay page." % (total, len(tiers)))
    print("Hygiene check passed: no em/en dashes, no curly quotes, no single-quote delimiters.")
    slug_list = [(SLUGS[s["heading"]], s["heading"]) for t in tiers for s in t["sections"]]
    print("Slugs: " + ", ".join("#" + s for s, _ in slug_list))


if __name__ == "__main__":
    main()
