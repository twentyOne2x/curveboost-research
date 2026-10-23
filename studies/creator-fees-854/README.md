# CurveBoost: retained first-hour fee sensitivity

Study snapshot: 23 October 2026. Prepared for private review.

This reproduces the article's **583 Pigeon + 271 Ram = 854 launch windows**, including original-launcher trades, from the retained exact integer per-launch phase tables. All amounts represent generated gross creator fees, not money received or claimed by either launcher.

| Cohort | Windows | Recorded gross SOL | Curve-only 95 bps sensitivity SOL |
|---|---:|---:|---:|
| Pigeon / @esotericpigeon |583 |3604.627644417 |6000.318444577 |
| Ram / @ramonos |271 |807.507512206 |1583.142686732 |

Run from this package directory:

```sh
python3 scripts/calculate.py
```

The script uses only Python's standard library. It checks cohort sizes, unique mints and expected exact integers, then writes `results.json`. `data/launches-854.csv` provides every launch's curve and AMM volume, observed fee, saved event-rounded 95 bps fee sum, event counts and historical source reference. The reference paths are provenance identifiers within the original research case; those upstream files are not included here.

`figures/curveboost-first-hour-fees-v4.png` and `.svg` are the current article graphics. Earlier `boost-fees-v4` graphics remain as historical presentation assets. The green increase labels are +$256,914 (+66.5%) for Pigeon and +$83,179 (+96.1%) for Ram, computed from exact lamport differences and the retained $107.24/SOL valuation. [Exact arithmetic](figures/uplift-proof.json) is included. Their exact display inputs are `figures/chart-input.json`; optional `scripts/render_chart.py` requires Pillow and regenerates the graphic with a portable font fallback, so typography may differ. Calculations do not require Pillow.

Read `METHODOLOGY.md` for the counterfactual and evidence limits, `data/provenance.json` for original input hashes, and `MANIFEST.json` for hashes of this package's files.

## Private event asset and independent replay

The separate private release asset `events-854.jsonl.gz` contains the normalized events behind all 854 windows. Download it only from this repository's private release, then run:

```sh
python3 scripts/replay_events.py --events events-854.jsonl.gz
```

Replay derives each 95 bps contribution from its principal, checks the saved event contribution and reconciles all 854 launches' phase volumes, observed fees, event-floor sums, event counts and zero-fee counts. Fields absent in the retained event source are explicitly null. Raw RPC transaction archives remain outside the package; event replay is independent arithmetic over retained normalized evidence, not a new chain decode.

`data/event-asset-provenance.json` binds the separate asset and original normalized input hashes. `data/event-replay-verification.json` records the completed replay. The owner-only offline bridge `scripts/export_events.py --case PATH_TO_ORIGINAL_CASE --out PRIVATE_ASSET_DIRECTORY` can rebuild the asset from the retained case without network access. It requires the original case, unlike the portable replay.

Chart rendering uses the [shared approved CurveBoost identity](../../article/brand/README.md); retain the repository layout so both charts use the same source artwork.

The first-hour creator-fee chart includes the original public profile pictures of @esotericpigeon and @ramonos. Image sources, capture times and hashes are retained in [the avatar provenance](figures/avatars/provenance.json).
