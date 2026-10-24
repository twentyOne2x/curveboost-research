# Scope and calculation

The retained historical study selected854 complete primary-venue first-hour native-SOL Pump launch windows:583 signed Pigeon launches and271 signed Ram launches. Each window begins at signed creation and ends exclusively3600seconds later. This differs from the newer Circular pilot's first-trade clock. The Pigeon census cutoff was2026-10-09T22:47:36Z; Ram's was2026-10-13T16:19:01Z. The854 are the retained complete native-SOL model cohort, not every launch by these wallets or an unbiased market sample. Other quote assets, unsupported venues and incomplete histories are outside this model.

Public wallet identities retained by the original study:

- Pigeon: `gVDXhoGbePACvSqN7CZBtQXFW9eyJwsgudPEwSydAkx`
- Ram: `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`

Use the input table's `all` measure: all observed traders, including the original launcher. No launcher-excluded inputs are used. This does not establish organic activity, independent wallets or beneficiary ownership.

For each launch:

```
recorded = observed_curve_creator_fee + observed_AMM_creator_fee
sensitivity = SUM_curve_events(floor(principal_lamports *95 /10000))
              + observed_AMM_creator_fee
```

Historical AMM fees remain unchanged. Only historical bonding-curve principal is repriced. Buy-plus-sell principal is turnover, not net inflow. Integer units are lamports;1SOL=1,000,000,000lamports. The input `curve_fee95FloorRaw` is the original exact sum of individual event floors. It must not be replaced by flooring total phase volume, which can differ because of rounding.

The primary sensitivity applies95bps even to events with historically zero creator fees. It does not preserve historical zero-fee eligibility.95bps is a static research benchmark, corresponding to a retained published tier; it is not a promise that every actual boosted trade would remain in that tier. No migration path, price formation, financing trades, changed demand, inventory sales, fee split, interest or repayment is simulated. It answers an unchanged-recorded-volume fee-rate question. No creator cash receipts or claims are asserted.

The USD figures use a single archived Kraken last-trade price of$107.24/SOL, captured2026-10-14T12:02:16.847966Z. They are display valuations rounded to whole dollars, not historical event-time revenue or current market value. The bundled response records the original public source URL. Article displays reproduce386,560→643,474USD and86,597→169,776USD.

# Reproducibility boundary

All854 exact per-launch phase tables are bundled and aggregate reproduction is portable and offline. The upstream scripts originally summed normalized retained trade events, checked first-hour/source coverage and matched per-launch volume/fee equalities. Original input-file hashes are retained in `data/provenance.json`.

**Raw RPC page archives are not bundled.** A separate normalized-event release asset now supports independent recomputation of every event floor from its principal and exact854-launch phase reconciliation. It cannot independently re-decode raw chain transactions, verify provider completeness or audit historical beneficial ownership. It does not claim a full raw-chain reproduction. The event source hashes, asset hash and replay receipt make this boundary explicit.

The older `sum-retained-fees.py` performs a different, launcher-excluded uniform95bps calculation across both phases. It is deliberately excluded because it does not reproduce this article's curve-only, all-trader comparison. No figures from the newer12-token migration pilot replace the original854 study.
