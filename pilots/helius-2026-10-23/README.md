# Helius migration pilot — private research

A retained 12-token Solana migration pilot. The 12 pilot tokens belong to 12 races containing 51 CSV members: 12 fetched and 39 competitors not fetched. This is not a complete race reconstruction. inputs/pilot-races-51-members.csv contains the exact joined scope with pilotFetched flags. The original proxy cutoff selection has 117 candidates; the revised standard-SOL snapshot-graduate universe has 160. These denominators are separate.

139,134 unique transactions; 94,076 bound own-hour trade events; signed creation and exact migration/pool binding for all 12. All 79,672 AMM events have quote-transfer reconciliation, subject to the unresolved schema/log qualifications below. No claims of causal uplift, complete revenue, wallet receipts or profit.

Small repository files contain the selection, verified migration CSV, source-page hashes, plan/summary, methods and final check receipt. Full unchanged compressed provider pages and detailed outputs are in the separate private release asset `helius-pilot-evidence.tar.gz`. No collector or credentials are needed.

## Offline use

Python 3.11+ standard library only. Extract the private asset beside this checkout, then run:

```sh
python3 verify.py --evidence ../helius-pilot-evidence
python3 analyze.py --capture ../helius-pilot-evidence/capture --manifest inputs/pilot-manifest.json --out reproduced-analysis
```

The second command decodes the full retained capture and may take a few minutes. Packaging verification checks the archive digest, every compressed page hash, one decompressed raw hash, vendored imports/PDA derivation and source binding without repeating the full analysis. Historical manifest/analyzer hashes intentionally differ from the portable copies; PROVENANCE.json documents the exact changes.

This package does not fetch the remaining 39 tokens and contains no network acquisition code.
