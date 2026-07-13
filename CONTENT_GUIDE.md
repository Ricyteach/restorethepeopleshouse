# Content Guide

This documents the site's content structure, ordering, and voice rules, for the build and for future edits.

## Files

- `content/hero.md`: the hero block (title, tagline, hero statement) and the short "who is behind this" footer note.
- `content/tier1.md` through `content/tier5.md`: the accordion sections. Each `###` heading is one accordion item; the prose beneath it is that item's body. The "Tier intro line" at the top of each file is the one-sentence label rendered above that tier's group of items. Nothing else in the file headers is site content.
- `content/essay.md`: the long-form essay, rendered as its own page ("Read the full argument") and linked from the main page.

## Section order (authoritative)

**Tier 1: Why it feels broken**
1. Why your vote feels like it doesn't matter
2. Why you can't vote third party without throwing your vote away
3. Why bipartisan reforms always die in Washington
4. Why your representative ignores you between elections
5. Why scandals never seem to have consequences
6. Why gerrymandering keeps winning
7. Why moderates always lose

**Tier 2: The proposal**
1. The whole proposal in 90 seconds
2. How the portable vote works
3. What stays exactly the same
4. Is this a fringe idea?
5. Won't this empower demagogues?
6. One election cycle, played out

**Tier 3: What's in it for you**
1. If you're a conservative
2. If you're a progressive
3. If you're an independent or politically homeless
4. If you're religious
5. If you've lost faith in both parties
6. What the Founders actually designed

**Tier 4: What would change**
1. Impeachment gets its teeth back
2. The donor and lobbying math
3. Third parties get a real path
4. Fame stops passing for support
5. The job becomes doable by normal people

**Tier 5: The skeptic's corner**
1. If most voters never touch it, how does it do anything?
2. Won't real-time pressure kill political courage?
3. Could it be hacked or coerced?
4. Doesn't this violate one person, one vote?
5. Can 6,500 people actually function as a legislature?
6. What would it cost?
7. What could actually go wrong
8. How could this ever pass?

## Voice and honesty rules

These are load-bearing. The site's credibility strategy is calibrated honesty, and edits must preserve it.

1. **No em dashes, ever.** Use commas, colons, periods, or parentheses. This applies to all rendered text and all future edits.
2. **Double quotation marks only,** including for quotes inside quotes. Never single quotation marks. (Apostrophes in contractions are fine.)
3. **Second person, direct.** The reader is "you." Open each section with its sharpest sentence, not with setup.
4. **"The portable vote"** is the standing name for the proxy mechanism. Use it consistently.
5. **Calibrate claims by type.** Mechanical consequences (the geometry of 50,000-person districts, the arithmetic of lobbying coverage) are stated flatly. Behavioral predictions (who uses the system, how members respond) are stated as predictions, in conditional mood, with the uncertainty owned in the text. Never let a prediction wear a theorem's clothes.
6. **Never claim the Founders would endorse the portable vote.** The permitted claim is continuity of purpose: the expansion restores their documented design; the portable vote is a clearly labeled new mechanism serving that documented purpose.
7. **Concede honestly and specifically.** The sections "What could actually go wrong," "Won't real-time pressure kill political courage?", and the caveats inside other sections are features, not hedges. Do not strengthen the site by weakening them.
8. **Party neutrality is structural, not rhetorical.** The conservative and progressive sections must remain parallel in length, structure, and generosity. Any edit that tilts one should tilt both.
9. **Minimal repetition.** Each section carries at most a one-sentence recap of the proposal, phrased variously. Sections cross-reference each other by name (the site supports deep links) instead of re-explaining.
10. **Rounded numbers, honest sourcing.** ~770,000 per district today; 50,000 target; roughly 6,500 members; ~12,000 registered lobbyists; $5-8B annual cost; 10-15% estimated active proxy participation, always labeled an estimate.

## Editing workflow

To add a section: add a `###` heading and body to the appropriate tier file, then add it to the ordering list above. To reorder: edit the list above and move the section in the file (the build renders sections in file order). To retire a section: remove it from the file and the list. Keep this guide current; it is the source of truth the build reads for structure.
