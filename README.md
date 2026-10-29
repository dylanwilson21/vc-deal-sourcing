# vc-deal-sourcing

A Claude skill that sources, scores and ranks startup deals for a venture fund's thesis. Give it a fund website or a thesis, and it returns:

- **A deal workbook (Excel):** 40 ranked deals by default, the top 10 in detail, bottom-up market sizes, and a maximum-price calculation for the best deal. Every score and weight is live, so you can change one and see the ranks move.
- **A one-page top-10 PDF:** logos, links to each company's website and each founder's LinkedIn, and one line on fit plus one on why each company is interesting. It is built to skim in a meeting.
- **A process brief (PDF):** how the list was built and how the scoring works.

Founders carry 45% of the score by default. The skill tunes the weights by backtesting the fund's own past investments, and checks its scores with a blind second reviewer.

## Install

**Claude Code**

Ask Claude:

> Install the skill from https://github.com/OWNER/vc-deal-sourcing into ~/.claude/skills

Or do it yourself:

```bash
git clone https://github.com/OWNER/vc-deal-sourcing /tmp/vc-deal-sourcing
cp -r /tmp/vc-deal-sourcing/vc-deal-sourcing ~/.claude/skills/
```

**Claude app (claude.ai or desktop)**

1. Download `vc-deal-sourcing.zip` from this repo.
2. In Claude, open **Customize > Skills**, click **+**, choose **Upload a skill**, and upload the ZIP.
3. Make sure code execution is on (**Settings > Capabilities**).

## Use

Type one line:

> Source deals for https://yourfund.com

> Find 25 deals for this thesis: seed-stage B2B software in the Southeast, $1-3M checks, lead or co-lead.

Claude asks up to five quick questions (how many deals, check size, your name for the cover, whether you are signed in to PitchBook or Crunchbase in a browser it can use) and then runs. A full run takes roughly 30-60 minutes, most of it research.

**Tips**

- Signing in to PitchBook or Crunchbase in a browser Claude can use makes round and valuation data much better. Without it, the skill uses press releases and SEC filings.
- Claude Code can run research in parallel, so it finishes faster than the Claude app.
- Open the workbook in Excel, Google Sheets or Numbers. Quick-look previewers don't calculate formulas or show wrapped text.

## What it won't do

- It won't scrape LinkedIn. Founder LinkedIn links come only from company team pages, press releases or matching search results.
- It won't get around CAPTCHAs or bot checks.
- It marks figures it could not confirm as unverified, and labels company-reported numbers as such.

## Files

```
vc-deal-sourcing/
  SKILL.md              workflow Claude follows
  references/           rubric, sourcing plan, valuation method, data format
  scripts/              SEC Form D pull, scoring, backtest, logo fetch, Excel and PDF builders
vc-deal-sourcing.zip    same folder, packaged for upload to the Claude app
```

Requires Python 3 with `openpyxl`, `reportlab` and `Pillow` (`cairosvg` optional). Claude installs any that are missing.

## License

MIT
