# Restore the People's House (the website)

A static, two-page advocacy site: `index.html` (hero + five tiers of accordion
sections) and `essay.html` (the long-form argument). No backend, no analytics,
no trackers, no frameworks, no packages to install. The only tool required is
Python (any 3.9+), which is already on this machine.

## How the pieces fit

| File | What it is |
|---|---|
| `content/hero.md` | Hero block (title, tagline, statement) and the footer note |
| `content/tier1.md` ... `tier5.md` | The accordion sections; each `###` heading is one section |
| `content/essay.md` | The long-form essay page |
| `CONTENT_GUIDE.md` | The authoritative section order and the voice rules |
| `build.py` | Turns the markdown into the site in `dist/` (stdlib only) |
| `check-content.py` | Enforces the writing rules (stdlib only) |
| `src/style.css`, `src/site.js`, `src/favicon.svg`, `src/fonts/` | Design, behavior, assets |
| `.github/workflows/deploy.yml` | Builds and publishes to GitHub Pages on every push |

`dist/` is generated output. Never edit it by hand; it is rebuilt from scratch
on every build and is not committed.

## Edit content

1. Edit the wording of a section: change it in its tier file. Done.
2. **Reorder sections**: move the `### heading` block within its tier file AND
   move it in the list in `CONTENT_GUIDE.md`. The build compares the two and
   fails with a clear message if they disagree, so you cannot silently drift.
3. **Add a section**: add a `### heading` and body to a tier file, add it to
   the list in `CONTENT_GUIDE.md`, and add a slug for it to the `SLUGS` table
   at the top of `build.py` (the build tells you exactly what to add if you
   forget).
4. **Retire a section**: remove it from the tier file and the guide list. Its
   `SLUGS` entry can stay (the build prints a harmless note) so the old link
   can be revived later.
5. **Reword a heading**: update the matching key in `SLUGS` too, but KEEP the
   same slug so links you have already shared keep working.

The build enforces the typography rules: if an em dash, en dash, curly quote,
or a single quote used as a quote delimiter appears anywhere in the rendered
pages, the build fails and shows you where. A failed build never deploys.

A second script enforces the writing rules shared with the Taut Engineering
site (no "X, not Y" constructions, no large language model tics, very few
metaphors):

```
python check-content.py
```

It prints FINDING lines, which fail, and note lines, which are for you to
judge. The deploy workflow runs it after the build, so a violation blocks the
deploy. The rules, the exceptions, and what deliberately does not carry over
from the Taut Engineering site are documented in `CONTENT_GUIDE.md`.

## Preview locally

From this folder:

```
python build.py
python -m http.server 8123 --directory dist
```

Then open http://localhost:8123 in a browser. (Opening `dist/index.html`
directly as a file also works in a pinch; the copy-link buttons then use a
fallback because browsers restrict the clipboard on file:// pages.)

## Deploy (GitHub Pages)

One-time setup:

1. Create a new GitHub repository (for example `restore-the-peoples-house`).
   This does NOT conflict with your company site: the one-site-per-account
   limit applies only to the special `<username>.github.io` repository.
   Project sites like this one are unlimited and live at
   `https://<username>.github.io/<repo-name>/`.
2. Push this folder to the repository (branch `main`).
3. In the repository on github.com: Settings > Pages > Build and deployment >
   Source: select **GitHub Actions**.
4. Also check Settings > Environments > github-pages > Deployment branches
   and tags. GitHub sometimes creates this environment with a restriction
   that blocks `main`; if the first deploy fails with "Branch main is not
   allowed to deploy," add `main` to the allowed branches there (or set it
   to "No restriction") and re-run the failed job.

That is the whole setup. From then on, every push to `main` builds the site
(including the hygiene and order checks) and publishes it. You can even edit
a content file directly on github.com in the browser; committing the edit
deploys it. Nothing needs to be installed anywhere.

### Custom domain

This site is configured for **restorethepeopleshouse.org**, set in the
`CNAME` file at the repo root. `build.py` copies that file into `dist/` on
every build. This matters because GitHub Pages deployed via Actions reads
the custom domain from the published artifact: without a `CNAME` file in
`dist/`, GitHub would silently clear the custom domain setting on the next
deploy. To change the domain, edit the `CNAME` file (one line, the domain
name, nothing else) and update the setting under Settings > Pages > Custom
domain to match. To drop the custom domain entirely, delete the `CNAME`
file and clear the setting on github.com.

## Deep-link slugs

Every accordion section has a stable anchor. Visiting a link opens that
section and scrolls to it, and each open section has a "Copy link" button.
Append the slug to the site URL, e.g. `https://.../#gerrymandering`.

| Section | Slug |
|---|---|
| **Tier 1: Why it feels broken** | |
| Why your vote feels like it doesn't matter | `#vote-doesnt-matter` |
| Why you can't vote third party without throwing your vote away | `#wasted-vote` |
| Why bipartisan reforms always die in Washington | `#bipartisan-reforms-die` |
| Why your representative ignores you between elections | `#ignored-between-elections` |
| Why scandals never seem to have consequences | `#scandals` |
| Why gerrymandering keeps winning | `#gerrymandering` |
| Why moderates always lose | `#moderates` |
| **Tier 2: The proposal** | |
| The whole proposal in 90 seconds | `#the-proposal` |
| How the portable vote works | `#portable-vote` |
| What stays exactly the same | `#what-stays-the-same` |
| Is this a fringe idea? | `#fringe-idea` |
| Won't this empower demagogues? | `#demagogues` |
| One election cycle, played out | `#one-cycle` |
| **Tier 3: What's in it for you** | |
| If you're a conservative | `#for-conservatives` |
| If you're a progressive | `#for-progressives` |
| If you're an independent or politically homeless | `#for-independents` |
| If you're religious | `#for-religious-voters` |
| If you've lost faith in both parties | `#lost-faith` |
| What the Founders actually designed | `#founders-design` |
| **Tier 4: What would change** | |
| Impeachment gets its teeth back | `#impeachment` |
| The donor and lobbying math | `#lobbying-math` |
| Third parties get a real path | `#third-parties` |
| Fame stops passing for support | `#fame-audit` |
| The job becomes doable by normal people | `#normal-people` |
| **Tier 5: The skeptic's corner** | |
| If most voters never touch it, how does it do anything? | `#low-participation` |
| Won't real-time pressure kill political courage? | `#political-courage` |
| Could it be hacked or coerced? | `#security` |
| Doesn't this violate one person, one vote? | `#one-person-one-vote` |
| Can 6,500 people actually function as a legislature? | `#chamber-size` |
| What would it cost? | `#cost` |
| What could actually go wrong | `#what-could-go-wrong` |
| How could this ever pass? | `#how-it-passes` |

The essay page has its own chapter anchors, derived from the chapter names:
`essay.html#the-problem`, `#the-proposal`, `#why-it-works`,
`#the-senate-unchanged`, `#objections`, `#what-would-follow`,
`#what-could-actually-go-wrong`, `#the-path`, `#the-pattern`.

## Change the look

All colors and the text measure are CSS variables at the top of
`src/style.css`, with comments. The accent is a single deep green chosen to
keep the design visibly party-neutral; if you change it, change it to
something that is still neither red nor blue. The typeface is Source Serif 4,
self-hosted in `src/fonts/` (no requests to Google or anyone else).

## Placeholder for a future follow/updates link

The footer template in `build.py` (function `footer_html`) contains an HTML
comment marking where a follow or updates link goes when one exists. Nothing
is rendered until you add it.
