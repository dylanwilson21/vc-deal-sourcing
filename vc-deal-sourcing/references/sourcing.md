# Sourcing plan

Aim for about twice the requested deal count before scoring. Use three channels. Press finds most companies; Form D filings and cohorts find the ones press misses.

## 1. Press and regional news (parallel research agents)

Split the fund's geography into 3-5 regions of similar startup density. Send each region to its own research agent at the same time, using the prompt below. Fill in the brackets.

```
You are sourcing venture deals. Use web search and web fetch only. Today is [DATE].

Fund thesis: [ONE PARAGRAPH: stage, check size, lead or follow, sectors, geography, what the fund avoids].

YOUR REGION: [REGION, with main cities].

Find [N] real, operating startups in your region that fit. Prefer companies whose last
round closed in the last 6-30 months, so they are plausibly raising next, or strong
pre-institutional teams. EXCLUDE: [FUND PORTFOLIO NAMES] and anything past [STAGE].

Founder quality matters most. For each founder find: role, prior companies and roles,
prior exits, years of experience in this problem, technical depth.

Return per company: name, website, HQ city/state, founded year, one-line description,
sector, business model, founders (as above), every known round (date, amount, lead,
investors, valuation if reported), traction (customers, revenue, growth, headcount),
target customer and any market-size figure with its source, and a source URL for every
key fact. Mark anything unconfirmed "unverified". Do not invent facts.
```

Good sources: regional business journals (Crain's, Business Journals, Inno), regional tech news (Built In, BetaKit, Hypepotamus, Startland, Silicon Prairie News, Venture Nashville), TechCrunch, press-release wires (Business Wire, PR Newswire, Newswire), university and accelerator news pages, and founder posts in search snippets.

## 2. SEC Form D filings

A US company raising money under Regulation D files a Form D. It shows the amount sold, the filing date, the company's business address, the year of incorporation and its industry group. Many seed rounds appear only here.

```
python3 scripts/edgar_formd.py --states IL,IN,OH --start 2026-01-01 --end 2026-10-31 \
  --contact "you@example.com" --out edgar.json
```

- `--contact` is required. The SEC asks automated callers to identify themselves; use the person's email only if they agree, otherwise a generic address.
- Filtering uses the business address, not the state of incorporation, so Delaware companies still show up under their real state.
- Ontario is `A6`; the script accepts any EDGAR location code.
- Results are filtered to likely startups: corporations incorporated recently, tech, health, financial or business-services industry codes, and $0.75M-$15M sold. Adjust with `--min`, `--max` and `--since-year`.
- The search returns at most 1,000 filings per state per query. If a state hits that cap, the script splits the date range automatically.
- Then give the best 15-20 names to one research agent to profile with the same prompt.

## 3. Cohorts, studios and university programs

Search recent cohort and winner lists (last 24 months) in the fund's region. Starting points:
- Accelerators: Techstars (city programs), Y Combinator (filter by city), gener8tor, Alchemist, 500 Global, Plug and Play, sector programs (insurance, health, logistics)
- Venture studios: High Alpha, Redesign Health, Atomic, Pioneer Square Labs, and regional equivalents
- Universities: business-plan competitions (for example the Kaplan New Venture Challenge at UChicago, VentureCat at Northwestern, Rice Business Plan Competition), research commercialization programs and faculty-founder fellowships
- Canada: Creative Destruction Lab, MaRS, DMZ, Communitech, Velocity

Cohort lists often name only companies, so profile the founders before scoring.

## Using the person's data subscriptions

If the person is signed in to PitchBook or Crunchbase in a browser Claude can use, open company profiles one at a time and read the page. Capture: last round, post-money, total raised, headcount, founders, investors and, for PitchBook, the VC Exit Predictor score as a cross-check. Keep the pace modest. If the site shows a bot check, stop and tell the person; don't try to get past it.
