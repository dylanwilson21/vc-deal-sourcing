---
name: vc-deal-sourcing
description: Source, score and rank startup deals that fit a venture fund's investment thesis, then produce a deal workbook (Excel), a one-page top-10 PDF and a process brief. Use when someone asks to find deals, build a deal list or pipeline, source startups for a VC fund, or prioritize companies against a fund's thesis, given a fund website or thesis text.
---

# VC deal sourcing

Turn a fund's thesis into a verified, ranked list of deals (default 40), pick the best one for a given check size with a maximum valuation, and deliver three files: `<Fund>_Deals.xlsx`, `<Fund>_Top10.pdf` and `<Fund>_Process_Brief.pdf`.

Founders carry the most weight. At seed the product will change and the market estimate is a guess, so who is building the company is the most reliable signal.

Scripts live in this skill's `scripts/` folder. In Claude Code, run them as `python3 ${CLAUDE_SKILL_DIR}/scripts/<name>.py`; in the Claude app, use the path to the skill's `scripts/` folder in the sandbox. Run them from the working folder so outputs land there. Every script prints usage with `--help`.

## Start

1. Ask once, in one message, and use the defaults if the person doesn't answer:
   - Fund website or thesis text (required)
   - Number of deals (default **40**)
   - Check size for the investment pick (default **$1M**)
   - Name for the "Prepared by" line (default: leave blank)
   - Whether they are signed in to PitchBook or Crunchbase in a browser Claude can use (default: no, use public sources)
2. Create a working folder `deal-sourcing-<fund-slug>/` and keep every file there. All data lives in one file, `deals.json`, whose format is in `references/data-schema.md`. Read that file now.
3. Check that Python has `openpyxl`, `reportlab` and `Pillow` (`cairosvg` is optional, for SVG logos). Install what is missing.
4. Make a task list with the steps below so the person can follow progress.

## Steps

**1. Turn the thesis into rules.** Read the fund's website (thesis, team, portfolio pages) or the pasted text. Write `fund` in `deals.json`: geographies (as state and province codes), stages, sectors, check size range, and anything the fund says it avoids. Show the rules in five lines or fewer and continue unless the person corrects them.

**2. Pull the fund's portfolio.** Use PitchBook (investor profile, Investments tab) if the person is signed in; otherwise the fund's portfolio page and press. Record every company the fund has backed (for exclusion) and its recent entry rounds with post-money values in `comps`. These real prices anchor the valuation in step 9. Also keep 20-24 older first checks with known outcomes for the backtest.

**3. Source candidates.** Aim for about twice the deal count. Follow `references/sourcing.md`, which has the search plan and the research prompt to reuse. Use three channels:
   - **Press and regional news.** Split the geography into 3-5 regions and give each region to its own research agent in parallel, using the prompt template. If agents aren't available, research the regions one after another.
   - **SEC Form D filings.** Run `python3 scripts/edgar_formd.py --states IL,OH,... --start YYYY-MM-DD --end YYYY-MM-DD --contact "<email>" --out edgar.json`. These filings show raises that never had a press release. Profile the 15-20 most promising with one research agent.
   - **Accelerator, studio and university cohorts** in the fund's region (list in `references/sourcing.md`).
   Drop anything the fund already owns, anything past the fund's stage, and anything outside its geography. List what you dropped and why in `excluded`.

**4. Score.** Score every candidate 1-5 on the eight factors in `references/rubric.md` and write the scores and a one-line note per company. Then run `python3 scripts/score.py deals.json` to rank.

**5. Backtest the weights (on by default).** Give one research agent the 20-24 historical first checks from step 2. It finds each outcome and scores the company on what was knowable at entry, using the same rubric. Save the result as `backtest` in `deals.json`, then run `python3 scripts/backtest.py deals.json --apply`. This moves weight toward the factors that separated the fund's winners from its losers, within limits, and records the original weights.

**6. Blind second scoring (on by default).** Write short fact-only dossiers for the top ~20 and give them to a separate agent with the rubric, but not your scores. Save its scores as `blind_scores`, then run `python3 scripts/reconcile.py deals.json`. For every gap of a point or more, choose a final score, write one line on why in `settled`, and rerun `score.py`.

**7. Verify the top 20.** Confirm rounds, post-money values, headcount and investors in PitchBook or Crunchbase if the person is signed in, otherwise in press releases and Form D filings. Fill `verified_via`. Mark anything you could not confirm as unverified rather than dropping the caveat. Rerank if facts changed.

**8. Write the top 10.** For each of the top 10, write one sentence on why it fits the thesis (`fit`) and one on why it is interesting (`why`). Keep each under about 30 words. Size each market bottom-up as described in `references/valuation.md`. Find each company's website and each founder's LinkedIn URL. Only use a LinkedIn URL that appears on the company's team page, in a press release, or in a search result whose title matches the person and company. Never build one from a name pattern, and leave it blank if unverified.

**9. Pick one deal and price it.** Choose the best risk-adjusted deal for the check size, usually the #1 company. Fill `pick` following `references/valuation.md`: work back from a plausible exit to the maximum post-money that still returns the target multiple, then compare that maximum with the company's last price and the fund's own recent entry prices from `comps`. Write `why_won` as one or two sentences on why it won overall. Don't compare it against each runner-up one by one.

**10. Build the outputs.** Run these from the working folder:
   - `python3 scripts/fetch_logos.py deals.json` (company and fund logos)
   - `python3 scripts/build_workbook.py deals.json`
   - `python3 scripts/build_onepager.py deals.json`
   - Write the `brief` section of `deals.json` (see the schema), then run `python3 scripts/build_brief.py deals.json`

**11. Check before delivering.** Open both PDFs as images and read them. The one-pager must fit on one page; if it overflows, shorten `fit` and `why`, not the font. Spot-check five numbers in the workbook against their sources. Then send the three files with a two-line summary: the #1 pick and its maximum price.

## Rules

- Never scrape LinkedIn or automate browsing on it; its terms prohibit it. Use it only through links you verified as described in step 8.
- Never complete CAPTCHAs or get around bot checks. If a site blocks automated browsing, say so and use another source.
- Label company-reported numbers as company figures, and anything you could not confirm as unverified.
- Put every assumption in the workbook where a reader can see and change it. The build script marks assumption cells in yellow.
- The person's own data subscriptions (PitchBook, Crunchbase) are used through their signed-in browser at a modest pace, for this task only.
- Keep the outputs free of notes to the person. They are meant to be handed to the fund as they are.

## Files

- `references/data-schema.md`: the `deals.json` format used by every script
- `references/rubric.md`: the eight factors, scoring anchors and default weights
- `references/sourcing.md`: search plan, research-agent prompt and cohort list
- `references/valuation.md`: bottom-up market sizing and the max-price method
- `scripts/`: the scripts named in the steps above. Each one prints `--help`.
