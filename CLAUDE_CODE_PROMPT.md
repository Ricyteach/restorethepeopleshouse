# Prompt for Claude Code

I'm building a static advocacy website called "Restore the People's House." Everything you need is in this folder, and the copy is final-draft: your job is to build the site around it, not to write or improve the writing.

Read these in order before doing anything else:
1. `SITE_SPEC.md`: the build specification (structure, accordion behavior, deep links, design direction, tech stack, definition of done).
2. `CONTENT_GUIDE.md`: the authoritative section ordering, the file format, and the voice rules that govern any text you touch.
3. The content itself in `content/`: `hero.md` (hero block and footer note), `tier1.md` through `tier5.md` (the accordion sections; each `###` heading is one item), and `essay.md` (the long-form page).

Then read the frontend-design skill and apply it. The design brief in the spec matters: serious, civic, timeless, typography-led, and visibly party-neutral (no dominant red or blue).

Hard rules I care about most:
- The copy is final. Fix a typo if you find one; never rephrase, trim, punch up, or add argument content. If something seems wrong, ask me instead of editing.
- Zero em dashes or en dashes and zero single-quote delimiters may appear in the rendered site. The content was written clean; your job is to keep it clean, especially through any markdown or smart-quote processing. Grep the built output to verify, and make that check part of the build.
- Deep links to individual sections are a hard requirement. I will link specific sections in emails and posts, so every section needs a stable, sensible slug, a copy-link affordance, and open-on-arrival behavior. Document the slug list in the README.
- Static site only, deployable to GitHub Pages, no backend, no analytics, no trackers.

How I want to work: read everything first, then give me a short plan with the decisions you want my input on (static generator vs. plain HTML, font choice, slug naming, how the essay page relates to the main page). Do not start building until I confirm. Then build to the definition of done in the spec, show me how to preview locally, and set up the GitHub Pages deploy.

Context on me: I'm a structural engineer, not a web developer, although I have a lot of coding and web development experience. Even so, tend to explain choices in plain terms, and keep the project simple enough that I can edit content, reorder sections, and redeploy by myself using the README.