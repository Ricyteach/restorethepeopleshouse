# Restore the People's House: Site Build Specification

This specifies how to build the site. All copy is final-draft and lives in `content/`; structure and ordering live in `CONTENT_GUIDE.md`. This spec covers behavior, design, and tech.

## What this site is

A static, single-page advocacy site (plus one essay page) for a two-part US House reform: restore the founding ratio of one representative per 50,000 people (House grows to roughly 6,500), and give every voter a "portable vote" they can reassign to any representative in their state at any time. The core interaction is a tiered accordion of ~32 sections readers open in any order. The audience is a wide, cross-partisan general public; the credibility strategy is calibrated honesty, and the copy already embodies it. Do not punch up, soften, or editorialize the copy during the build.

## Tech stack

- Static output, no backend. Plain HTML/CSS/vanilla JS, or Astro/11ty if it makes the markdown pipeline cleaner. No SPA frameworks. Must deploy to GitHub Pages without special configuration.
- No analytics, trackers, cookies, or email capture in v1. The footer includes a clearly marked placeholder where a follow/updates link can go later.
- Content is authored in markdown; the build parses each tier file's `###` headings into accordion items per `CONTENT_GUIDE.md`. Preserve bold/italic emphasis.

## Hard content rules (enforce at build)

- Zero em dashes and zero en dashes in rendered output. The source content has already been written clean, but verify with a final grep of the built site and fail the build if any appear.
- Double quotation marks only; no single quotation marks as quote delimiters anywhere in rendered text. (Apostrophes in contractions are fine.) Beware smart-quote transforms in any markdown processor: configure typographic processing so it never converts to single quotes or em dashes.
- Do not generate, invent, or rewrite argument content. The copy is final-draft. Typos may be fixed; claims may not be altered.

## Page structure

1. **Hero**, from `content/hero.md`: title, tagline, hero statement. This copy is written; render it, do not draft it.
2. **The accordion**, five tiers in the order given in `CONTENT_GUIDE.md`, each tier preceded by its one-line intro (also in the content files). Tier 1 should be visually the most inviting; Tier 5 can be denser.
3. **Essay access**: a clearly labeled link ("Read the full argument") to a second page rendered from `content/essay.md`, with comfortable long-form typography and a link back.
4. **Footer**: the "Who is behind this" note from `hero.md`, a placeholder for future updates/follow link (marked as placeholder in a comment, not rendered as visible lorem), and per-section share affordances if lightweight.

## Accordion behavior

- Heading always visible as the click target with a clear expand/collapse affordance. Multiple items can be open simultaneously; never auto-collapse siblings.
- Smooth, quick height transition; disable under `prefers-reduced-motion`.
- **Deep links are a hard requirement.** Each section gets a stable slug id derived from its heading (e.g. `#if-most-voters-never-touch-it-how-does-it-do-anything` may be shortened to a sensible stable slug like `#low-participation`; document the chosen slugs in the README because the owner will use them in emails and posts). Visiting a slug URL opens that section and scrolls to it. Provide a small "copy link" affordance on each open section.
- Keyboard accessible: real buttons, Enter/Space toggling, correct `aria-expanded`/`aria-controls`.

## Visual design direction

Read the frontend-design skill before building and apply it. Intent:

- Serious, civic, trustworthy, a little timeless: closer to a well-set book or a serious institution than to a campaign or a startup. The party-neutrality of the proposal must be legible in the design itself: no dominant red or blue; a restrained neutral palette with one accent used consistently.
- Typography-led; a strong readable serif suits the restoration register. Generous line height, 65-75 character measure, real hierarchy. Mobile-first: most readers arrive on phones from shared links, and the accordion must feel excellent on a narrow screen.
- Fast and light: one webfont at most, minimal JS, no heavy assets. Should score well on Lighthouse without special effort.
- The hero may carry a subtle, tasteful motif evoking the People's House or the founding era; decoration must never crowd the argument.

## Non-goals for v1

No interactive proxy simulator, no backend, no blog, no analytics, no email capture wiring, no new content.

## Definition of done

- Builds and previews locally; deploys to GitHub Pages via a documented command or workflow.
- All 32 sections render in the `CONTENT_GUIDE.md` order; tier intros present; hero and essay page present.
- Accordion supports multiple-open, keyboard access, reduced motion, and working deep links with documented slugs.
- Grep of built output confirms zero em/en dashes and zero single-quote delimiters.
- README explains: how to edit or reorder content via the tier files and `CONTENT_GUIDE.md`, how to run locally, how to deploy, and the slug list.
