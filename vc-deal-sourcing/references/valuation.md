# Market sizing and the maximum price

## Bottom-up market size (each top-10 company)

TAM = base figure x filter x unit value.

- **Base figure:** a sourced count of buyers (for example 39,000 US independent insurance agencies, or 6,100 US hospitals) or a sourced dollar pool (for example $906B of US trucking freight revenue). Cite the source.
- **Filter:** the share of that base that would realistically buy. Usually an assumption; say so.
- **Unit value:** annual contract value per buyer, or a take rate on a dollar pool. Companies rarely publish pricing, so this is usually an assumption; say so.
- **Reachable share:** what the company can win in the next 3-5 years. An assumption.
- Add one top-down number as a cross-check, never as the TAM.

The workbook shows every assumption in yellow so a partner can change it.

## Maximum post-money for the pick (venture method)

Inputs, all editable in the workbook:

| Input | Typical default |
|---|---|
| Check size | from the person, default $1M |
| Exit ARR | a plausible slice of the bottom-up market at year 6-7 |
| Exit multiple (x ARR) | 6-10x for vertical software |
| Dilution after entry | Series A 20%, B 15%, C 10%, option pool refreshes 5% (drop the rounds that come before entry) |
| Target gross multiple | 10x |
| Years to exit | 6 |

Calculation:
1. Exit value = exit ARR x multiple.
2. Ownership kept = product of (1 - dilution) for every later round.
3. Ownership needed at exit = check x target multiple / exit value.
4. Ownership needed at entry = (3) / (2).
5. **Maximum post-money = check / (4).**

Then compare against real prices:
- the company's last post-money (PitchBook, press or Form D math), times a reasonable step-up for a round now
- the fund's own recent entry prices at the next stage (from `comps`)

Decision rule: if the price now sits under the maximum but the next-stage price sits above it, say "invest now". If both sit under, the timing is flexible. If neither does, pass or shrink the check. Show a sensitivity grid of exit ARR against exit multiple.
