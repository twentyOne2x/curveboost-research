# Boost matched launch-race research

Study snapshot: 23 October 2026. Prepared for private review.

The strongest own two-minute opening also led own first-hour volume in **1,007/1,219 contested races (82.6%)**. The first token launched led in **577/1,219 (47.3%)**. The contested set contains **5,534 member tokens**. A contested race has at least two tokens with $1,000 or more in own first-hour exported volume.

These are retrospective associations within the matched source export. They are not a Boost success rate, a causal effect, an all-market estimate or an online prediction at race-minute two.

## Reproduce offline

Python 3.10 or newer and the standard library reproduce the tables and native SVG without credentials, RPC or network access:

```sh
python3 scripts/analyze.py
python3 scripts/build_chart.py --svg-only
```

The analysis checks all source hashes, counts, member joins, rounded volume totals, role identities and within-race volume maxima. It writes `results/vamp-review.json`, `results/verification.json`, `results/contested-races.csv` and `results/contested-members.csv`.

Optional PNG recreation uses an already-installed Pillow 10.1 or newer:

```sh
python3 scripts/build_chart.py
```

The renderer tries Arial, DejaVu Sans and Liberation Sans, then Pillow's scalable default font. It needs no machine-specific font path. Native SVG uses standard sans-serif fallbacks and can be opened or exported in any SVG-capable browser/editor. Font rasterization can vary by platform. `charts/original/` preserves the exact article PNG/SVG unchanged; `charts/rebuilt/` holds generated versions.

## Contents

- `data/`: unchanged `races.csv`, `race_members.csv`, `all_mints.csv` and original French `README.txt`; UTF-8, semicolon separators and decimal commas.
- `data/source-hashes.json`: original archive SHA-256 plus individual source-member hashes.
- `docs/METHOD.md`: cohort, own-age windows, missing data, flags and interpretation.
- `docs/pilot-migration-discrepancies.json`: separate timing-only reference from the 12-token migration pilot. Four material discrepancies are identified separately from three differences of five seconds or less. This does not rewrite the CSV or validate its phase-volume allocation.
- `scripts/`: portable offline analysis and chart recreation.
- `results/`: reproducible review and complete contested race/member rows.
- `charts/`: original article graphics and reconstructed counterparts.

No private provider dashboard/account records, credentials, local absolute paths or original raw transaction pilot captures are included. Dataset rows contain public mint identifiers and source-supplied metadata. The repository owner controls integration and access.
