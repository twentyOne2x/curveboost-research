# CurveBoost research · attn.markets

Data, methodology, calculations and charts supporting **CurveBoost: boost the opening rush**. Snapshot: 23 October 2026. **Repository visibility: private.** The CurveBoost article is an unpublished draft.

## Check the article's numbers

| Finding | Evidence | Calculation |
| --- | --- | --- |
| 46,528 daily launches, about 32/minute | [Tehcscreener daily response](studies/market-context-2026-10-22/) | 46,528 / 1,440 |
| Strongest own two-minute opening led first-hour volume in 82.6% of contested races | [Circular matched races](studies/vamp-races-2026-10-23/) | 1,007 / 1,219 |
| First launch led first-hour volume in 47.3% | Same 1,219 races | 577 / 1,219 |
| Pigeon: 3,604.63 → 6,000.32 SOL | [854-window fee study](studies/creator-fees-854/) | Reprice curve trades only; preserve recorded pool fees |
| Ram: 807.51 → 1,583.14 SOL | Same fee study | Same calculation |

The race export contains 8,821 tokens in 2,511 matched races, including 5,534 members of 1,219 contested races. A contested race has at least two members with $1,000 in own-first-hour volume. Every token's two-minute and one-hour windows start at its own first trade. This comparison measures retrospective opening leadership; it does not measure a common race-minute-two decision or a causal CurveBoost effect.

The fee examples cover 583 Pigeon and 271 Ram launches. All recorded traders, including launchers, are included. Only bonding-curve principal is repriced at 95 basis points; historical post-graduation fees stay unchanged. The scenario holds recorded trading activity fixed. USD display values use the retained study valuation of $107.24 per SOL. Methodology and exact integer inputs are in the fee folder.

## Reproduce offline

Python 3.11+ and its standard library reproduce the study tables and SVG chart:

```sh
python3 reproduce.py
```

The exact article charts are retained alongside their input tables and rendering code. Optional PNG rendering uses Pillow; the race chart has a standard-library SVG path. See each study's README for commands and evidence boundaries.

## Helius pilot is separate

[The Helius pilot](pilots/helius-2026-10-23/) fetched 12 individual graduates from 12 races containing 51 known members; 39 competitors were not fetched. It is a provider/decoder validation sample, not the source of the article's 82.6% statistic.

It contains 139,134 unique transactions and verifies creation/migration/pool binding for the 12 subjects. Four CSV graduation proxies were materially late. Quote transfers reconcile for 79,672 AMM events, while schema extensions, ambiguous invocation logs and six post-completion events remain documented. New pilot fee totals are provisional and are not substituted into the article examples. Full pilot evidence is a separate private release attachment.

## Sources and navigation

- [Race dataset and definitions](studies/vamp-races-2026-10-23/docs/METHOD.md), supplied by [@Circular_fi](https://x.com/Circular_fi). Source CSVs, original README, flags, full membership and hashes are retained.
- [Market context](studies/market-context-2026-10-22/), from [@tehcscreener](https://x.com/tehcscreener) and its [public API](https://tehcscreener.com/api).
- [Fee methodology](studies/creator-fees-854/METHODOLOGY.md), [Pump fee schedule](https://pump.fun/docs/fees) and retained event provenance.
- [Article draft and cover](article/).
- [Evidence asset index](ASSETS.md).

Original analysis code uses the included MIT license. Source datasets and upstream interfaces retain their own provenance; this repository does not relicense third-party material. See [source notices](THIRD_PARTY_NOTICES.md).
