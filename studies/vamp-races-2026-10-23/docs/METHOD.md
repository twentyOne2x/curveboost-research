# Dataset, windows and proof limits

## Source and matching

The archive covers launches first detected from 22 October 2026 13:00 UTC through 23 October 13:00 UTC. Price observations stop at 23 October 15:15; graduation state stops at 14:22. The source describes database-only extraction, not fresh RPC or metadata downloads.

A main race groups tokens launched within 30 minutes of its anchor, using normalized ticker plus identical/contained/similar name or identical image URI/CID. Alternate 10-minute and 60-minute race IDs are retained. The original README states that 629 already-trading tokens and ten nameless/tickerless tokens were excluded. Creator wallet identity was not retained, so same-creator relaunches and independent copies cannot be separated.

The source has 2,511 races, 8,821 matched member tokens and 18,075 original mint rows. Contested means `n_active_1h_ge_1k_usd >= 2`: 1,219 races and 5,534 members. All members of each contested race are retained, including those below $1,000; this is not a 5,534-active-token claim.

## Exact headline calculation

`leader_2m_mint` is the token with the greatest own first-two-minute USD volume. `winner_1h_mint` is the token with the greatest own first-hour USD volume. Sum `leader_is_winner_1h == '1'` across contested races: 1,007/1,219 = 82.60869565%, shown as 82.6%.

Independently sum `first_launched_is_winner_1h == '1'` in the same races: 577/1,219 = 47.33388023%, shown as 47.3%. The script crosschecks these flags against mint identity and source member maxima. Role identity breaks ties according to the export; rounded values cannot independently resolve exact ties.

Five overall races have blank two-minute leaders/outcomes. Overall leader denominator is 2,506, while first-launch denominator is 2,511. No missing leader enters the contested headline denominator.

## Own-age clocks, selection and overlap

Each token starts its two-minute and one-hour clock at its own source first-trade time. A later member may launch up to 30 minutes after the race anchor. In contested races, 799 have a member not yet born at race-minute two; 365 eventual early leaders were not yet born then, and 667 leaders had not completed their own two-minute window. The contested filter itself depends on later first-hour outcomes.

Therefore the headline does not mean an observer could identify the winner two minutes after the first race token. Own first-two-minute volume is also included within the own-hour outcome. The separate own-minutes-2-to-60 leader result is 718/1,219 = 58.90%; it reduces that overlap but does not eliminate later-member lookahead.

## Flags and sensitivity

Race flags preserve study-window edges, tied/missing early leaders, loose name matching, extreme curve-volume warnings, inactive-copy sets and incomplete 24-hour windows. Member flags preserve missing image metadata, suspicious-transaction-share warnings, late price starts and incomplete history. Flags are source warnings, not proof of malicious trading or clean organic activity.

Removing races flagged `contains_possible_volume_bot`, `edge_of_24h_window_members_may_be_missing`, `tie_for_2m_leader` or `no_2m_volume` leaves 954/1,154 = 82.67% strongest-opening wins and 547/1,154 = 47.40% first-launch wins. Thus recorded flags do not explain away the headline, while unobserved confounding remains.

Tight contested races use exported rounded runner-up/winner percentage at least 50: 494 races, with 368/494 = 74.49% opening-leader wins. One boundary, R1780, reconstructs as 49.97% from rounded member amounts although its exported ratio is 50.0%. Strict reconstruction produces 493. Do not silently mix definitions.

A separate arithmetic review observed 326 rounded ties for minutes-2-to-60 volume, including 311 all-zero races, and 16 tied earliest timestamps. These counts are limitation notes rather than independent chain confirmation. Complete 24-hour results cover only a narrow early subset: 137 contested races.

## Graduation and phase volumes remain source proxies

`graduation_utc` is described as the last bonding-curve trade, not a migration transaction witness. Exported curve/post-graduation USD volumes inherit that proxy and the different snapshot cutoffs. Quote families also differ: 2,667 member tokens are SOL standard, 2,804 SOL flag81 and 3,350 other quote. Do not reprice their mixed USD volumes at 0.95% or call them exact creator-fee accrual.

The export reports 302 graduates across 252 races. These are source-reported states. A separate 12-token standard-SOL pilot later verified migration/pool witnesses for its selected tokens and found four material proxy errors: source proxies were 690, 1,342, 1,379 and 2,005 seconds later than migration. See `pilot-migration-discrepancies.json`; it also retains three small differences. This does not constitute a whole-race reconstruction or correction of every source phase row.

The matched-race export has no creator-fee events, beneficiary routing or wallet receipts. Gross fee components, creator-wallet allocation, holder rewards, cashback, claims and trading profit are separate quantities. The previous 854-history Pigeon/Ram fee calculation is a separate study and is not recomputed here.

## Reproduction boundary

The scripts validate source bytes, exported arithmetic, membership and role consistency. They do not independently verify the underlying database/chain rows, close the missing-competitor universe, identify issuer control, or establish that financed Boost launches produce incremental demand. Original data and article images are preserved; portable outputs are derived alongside them.
