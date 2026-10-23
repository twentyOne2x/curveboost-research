# Private evidence downloads

Private draft release: [research-2026-10-23](https://github.com/twentyOne2x/boost-research/releases/tag/untagged-ad6a6ad78bb44ddfaeac). GitHub authentication and repository access are required.

| Asset | Contents | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| events-854.jsonl.gz | 1,759,593 normalized fee events across 854 launch windows | 293,253,211 | `9afb5773f3f4e71e7bc6b58e28052c766b2a4444c5ccb073755b5391e828018b` |
| helius-pilot-evidence.tar.gz | 595 original compressed provider pages and retained pilot analysis | 319,582,179 | `febfd6fc2d8fe61f6e79b092c483f96d3c700b1fa731ff45d2ddb188e068cf1f` |

Download with GitHub CLI from the repository root:

```sh
gh release download research-2026-10-23 --repo twentyOne2x/boost-research --pattern events-854.jsonl.gz --pattern helius-pilot-evidence.tar.gz
python3 studies/creator-fees-854/scripts/replay_events.py --events events-854.jsonl.gz
python3 pilots/helius-2026-10-23/verify.py --archive helius-pilot-evidence.tar.gz
```

The fee replay independently recomputes the 95-basis-point floor from each event principal and checks all 854 launches against their phase tables. The Helius command verifies the evidence archive; full pilot re-decoding is documented in the pilot README and retains its unresolved schema/log issues.
