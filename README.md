# CurveBoost Research

Data, methods, calculation scripts and charts behind **CurveBoost: boost the opening rush**, by [attn.markets](https://x.com/attndotmarkets). Research snapshot: 23 October 2026. CurveBoost is in development; the article remains a draft.

This repository includes the underlying CSV datasets and reproducible calculations. The separate Helius pilot has its own inputs, methods and evidence archive.

## Start with the data

| Dataset | Download or browse | What it contains |
| --- | --- | --- |
| Circular launch universe | [all_mints.csv](studies/vamp-races-2026-10-23/data/all_mints.csv) | 18,075 token rows from the supplied export |
| Matched vamp races | [races.csv](studies/vamp-races-2026-10-23/data/races.csv) · [race_members.csv](studies/vamp-races-2026-10-23/data/race_members.csv) | 2,511 races and 8,821 members, including 5,534 tokens across 1,219 contested races |
| Pigeon and Ram fee windows | [launches-854.csv](studies/creator-fees-854/data/launches-854.csv) | 854 first-hour histories: 583 Pigeon launches and 271 Ram launches, with exact fee inputs |
| Normalized fee events | [events-854.jsonl.gz](https://github.com/twentyOne2x/curveboost-research/releases/download/research-2026-10-23/events-854.jsonl.gz) | 1,759,593 events for independent per-event fee replay; about 293 MB compressed |
| Daily market context | [Tehcscreener response and calculation](studies/market-context-2026-10-22/) | The retained daily aggregate supporting 46,528 launches and about 32 per minute |

For a CSV, open its link and use **Raw** or **Download raw file**. The full repository is available through **Code → Download ZIP**. Large archives are attached to the [research release](https://github.com/twentyOne2x/curveboost-research/releases/tag/research-2026-10-23); hashes and commands are in [ASSETS.md](ASSETS.md).

## Findings and calculations

| Finding | Calculation | Method |
| --- | --- | --- |
| The token with the strongest own first two minutes also led first-hour volume in 82.6% of contested races | 1,007 / 1,219 | [Race definitions and matching](studies/vamp-races-2026-10-23/docs/METHOD.md) |
| The first token launched led first-hour volume in 47.3% of the same races | 577 / 1,219 | [Race study](studies/vamp-races-2026-10-23/) |
| Pigeon: $256,914 more in first-hour creator fees (+66.5%) across 583 launches | 3,604.63 → 6,000.32 SOL | [Fee methodology](studies/creator-fees-854/METHODOLOGY.md) |
| Ram: $83,179 more in first-hour creator fees (+96.1%) across 271 launches | 807.51 → 1,583.14 SOL | [Exact calculation inputs](studies/creator-fees-854/data/launches-854.csv) |

The Circular export is a non-exhaustive sample. A contested race has at least two members with $1,000 or more in their own first-hour volume. Each token's two-minute and one-hour windows start at its own first trade. The comparison is retrospective; it does not measure a common race-minute-two decision or a causal CurveBoost effect.

The fee scenario holds recorded trading activity fixed. All recorded traders, including launchers, are included. Only bonding-curve principal is repriced at 95 basis points; historical post-graduation fees stay unchanged. Dollar figures use the retained $107.24/SOL study valuation. [Exact integer outputs](studies/creator-fees-854/results.json) and [uplift arithmetic](studies/creator-fees-854/figures/uplift-proof.json) are included.

## Charts and article

- [Opening volume and first-hour leadership](studies/vamp-races-2026-10-23/charts/rebuilt/curveboost-opening-volume-v5.png) · [editable SVG](studies/vamp-races-2026-10-23/charts/rebuilt/curveboost-opening-volume-v5.svg)
- [First-hour creator-fee increases](studies/creator-fees-854/figures/curveboost-first-hour-fees-v6.png) · [editable SVG](studies/creator-fees-854/figures/curveboost-first-hour-fees-v6.svg)
- [Article draft](article/boost-draft.txt) · [cover and brand assets](article/)

Chart sources and native rendering scripts live beside the study data. Earlier image versions remain as historical presentation assets.

## Reproduce offline

Python 3.11+ and its standard library reproduce the study tables and race SVG:

```sh
git clone https://github.com/twentyOne2x/curveboost-research.git
cd curveboost-research
python3 reproduce.py
```

No RPC or API key is needed. For the independent event-level replay, download `events-854.jsonl.gz` from the release and run:

```sh
python3 studies/creator-fees-854/scripts/replay_events.py --events events-854.jsonl.gz
```

Optional PNG rendering uses Pillow. Each study's README documents its commands, source hashes and evidence boundaries. [Verification notes](VERIFICATION.md) record the retained checks.

## Separate Helius pilot

[The Helius pilot](pilots/helius-2026-10-23/) covers 12 individual graduates from 12 races with 51 known members; 39 competitors were not fetched. It validates provider/decoder behavior and is separate from the Circular sample and the historical fee examples.

The pilot retains 139,134 unique transactions and verifies creation/migration/pool binding for its 12 subjects. Four CSV graduation proxies were materially late. Quote transfers reconcile for 79,672 AMM events; schema extensions, ambiguous invocation logs and six post-completion events remain documented. Its fee totals are provisional and do not replace the article examples.

[helius-pilot-evidence.tar.gz](https://github.com/twentyOne2x/curveboost-research/releases/download/research-2026-10-23/helius-pilot-evidence.tar.gz) is a separate archive containing the original compressed provider pages and pilot analysis. See the [pilot methods and replay instructions](pilots/helius-2026-10-23/README.md) and [download hashes](ASSETS.md).

## Sources, scope and licensing

- Race export supplied by [@Circular_fi](https://x.com/Circular_fi), with its original README, matching flags and source hashes retained.
- Market context from [@tehcscreener](https://x.com/tehcscreener) and its [public API](https://tehcscreener.com/api).
- Fee policy from [Pump's fee schedule](https://pump.fun/docs/fees); historical inputs and valuation provenance are retained in the fee study.

The included data describe launches, trading volume, creator-fee inputs and the separate transaction pilot. A holder/shareholder census is not included.

Original analysis code and owned charts use the [MIT license](LICENSE). Third-party datasets, avatars and upstream interfaces retain their own rights and provenance; they are not relicensed under MIT. See [source notices](THIRD_PARTY_NOTICES.md).
