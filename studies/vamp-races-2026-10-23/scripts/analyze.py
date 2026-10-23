import collections
import csv
import hashlib
import io
import json
import statistics
import argparse
from datetime import datetime
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description='Offline reproduction of the matched-race export.')
parser.add_argument('--data', type=Path, default=PACKAGE / 'data')
parser.add_argument('--out', type=Path, default=PACKAGE / 'results')
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
provenance = json.loads((args.data / 'source-hashes.json').read_text())

def number(value):
    return float(value.replace(',', '.')) if value else None

def stamp(value):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

def outcome(rows, field):
    eligible = [r for r in rows if r[field] != '']
    n = sum(r[field] == '1' for r in eligible)
    return {'yes': n, 'denominator': len(eligible), 'pct': n / len(eligible) * 100 if eligible else None}

raw = {name: (args.data / name).read_bytes() for name in ['races.csv', 'race_members.csv', 'all_mints.csv', 'README.txt']}
for name, content in raw.items():
    assert hashlib.sha256(content).hexdigest() == provenance['membersSha256'][name], 'Source hash mismatch: ' + name

data = {name: list(csv.DictReader(io.StringIO(content.decode('utf-8-sig')), delimiter=';'))
        for name, content in raw.items() if name.endswith('.csv')}
races, members, all_mints = (data[k] for k in ['races.csv', 'race_members.csv', 'all_mints.csv'])
groups = collections.defaultdict(list)
for member in members:
    groups[member['race_id']].append(member)
assert len({r['race_id'] for r in races}) == len(races)
assert len({m['mint'] for m in members}) == len(members)
assert sum(int(r['n_members']) for r in races) == len(members)
for race in races:
    ms = groups[race['race_id']]
    assert len(ms) == int(race['n_members'])
    assert sum(number(m['vol_1h_usd']) >= 1000 for m in ms) == int(race['n_active_1h_ge_1k_usd'])
    assert abs(sum(number(m['vol_1h_usd']) for m in ms) - number(race['race_vol_1h_usd'])) <= len(ms)

def cohort(label, rows):
    total = sum(number(r['race_vol_1h_usd']) for r in rows)
    post = sum(number(r['race_postgrad_vol_1h_usd']) for r in rows)
    early = sum(number(m['vol_2m_usd']) for r in rows for m in groups[r['race_id']])
    return {
        'label': label, 'races': len(rows), 'members': sum(int(r['n_members']) for r in rows),
        'leaderWins1h': outcome(rows, 'leader_is_winner_1h'),
        'leaderWinsAfter2m': outcome(rows, 'leader_is_winner_after_2m'),
        'leaderWins24h': outcome(rows, 'leader_is_winner_24h'),
        'firstLaunchWins1h': outcome(rows, 'first_launched_is_winner_1h'),
        'firstHourWinnerWins24h': outcome(rows, 'winner_1h_is_winner_24h'),
        'uniformRandomAllMembersMeanPct': statistics.mean(100 / int(r['n_members']) for r in rows),
        'uniformRandomActiveMembersMeanPct': statistics.mean(100 / int(r['n_active_1h_ge_1k_usd']) for r in rows)
            if all(int(r['n_active_1h_ge_1k_usd']) >= 2 for r in rows) else None,
        'volume1hUsd': total, 'postgradVolume1hUsd': post, 'postgradSharePct': post / total * 100,
        'aggregateOwn2mVolumePctOf1h': early / total * 100,
    }

active = [r for r in races if int(r['n_active_1h_ge_1k_usd']) >= 2]
tight = [r for r in races if number(r['second_vs_winner_1h_pct']) is not None
         and number(r['second_vs_winner_1h_pct']) >= 50]
active_tight = [r for r in tight if int(r['n_active_1h_ge_1k_usd']) >= 2]
grad_races = [r for r in races if int(r['n_graduated']) > 0]
exclude = {'contains_possible_volume_bot', 'edge_of_24h_window_members_may_be_missing', 'tie_for_2m_leader', 'no_2m_volume'}
clean = lambda rows: [r for r in rows if not exclude.intersection(r['flags'].split('|'))]
cohorts = [cohort(label, rows) for label, rows in [
    ('all', races), ('contested', active), ('tight_all_export_rounded', tight),
    ('tight_contested_export_rounded', active_tight), ('all_flag_sensitivity', clean(races)),
    ('contested_flag_sensitivity', clean(active)),
    ('all_without_extreme_volume_flags', [r for r in races if 'contains_possible_volume_bot' not in r['flags']]),
    ('graduated_races', grad_races),
]]

def timing(rows):
    late_members = late_leaders = unfinished_leaders = 0
    for race in rows:
        anchor = stamp(race['first_launch_utc'])
        ms = groups[race['race_id']]
        late_members += any((stamp(m['launch_utc']) - anchor).total_seconds() > 120 for m in ms)
        leader = next((m for m in ms if m['mint'] == race['leader_2m_mint']), None)
        if leader:
            delay = (stamp(leader['launch_utc']) - anchor).total_seconds()
            late_leaders += delay > 120
            unfinished_leaders += delay > 0
    return {'races': len(rows), 'racesWithMemberNotBornAtRaceMinute2': late_members,
            'leadersNotBornAtRaceMinute2': late_leaders,
            'leadersOwn2mWindowNotCompleteAtRaceMinute2': unfinished_leaders}

positive = [m for m in members if number(m['vol_1h_usd']) > 0]
active_ids = {r['race_id'] for r in active}
winners = [m for m in positive if m['rank_1h'] == '1']
active_winners = [m for m in winners if m['race_id'] in active_ids]
graduates = [m for m in members if m['graduated_by_snapshot'] == '1']

def shares(ms):
    values = [number(m['vol_2m_usd']) / number(m['vol_1h_usd']) for m in ms]
    return {'positiveMembers': len(values), 'medianOwn2mSharePct': statistics.median(values) * 100,
            'membersWithAtLeast90PctInOwn2m': sum(v >= .9 for v in values),
            'membersWithAtLeast90PctInOwn2mPct': sum(v >= .9 for v in values) / len(values) * 100}

lead_bands = []
for label, test in [('at_least_5x', lambda x: x >= 5), ('2_to_5x', lambda x: 2 <= x < 5),
                    ('below_1_25x', lambda x: x < 1.25)]:
    rs = [r for r in races if number(r['leader_lead_vs_2nd_x']) is not None and test(number(r['leader_lead_vs_2nd_x']))]
    lead_bands.append({'label': label, 'leaderWins1h': outcome(rs, 'leader_is_winner_1h')})

result = {
    'sourceZip': provenance['archiveName'], 'sourceSha256': provenance['archiveSha256'],
    'membersSha256': {name: hashlib.sha256(content).hexdigest() for name, content in raw.items()},
    'sourceWindowUtc': ['2026-10-22 13:00:00', '2026-10-23 13:00:00'],
    'counts': {'races': len(races), 'members': len(members), 'allMints': len(all_mints)},
    'cohorts': cohorts, 'timingContested': timing(active), 'leadBandsAll': lead_bands,
    'openingShares': {'allPositiveMembers': shares(positive), 'allWinners': shares(winners), 'contestedWinners': shares(active_winners)},
    'graduation': {'racesWithGraduate': len(grad_races), 'racesWithMultipleGraduates': sum(int(r['n_graduated']) > 1 for r in races),
                   'firstGraduateIs1hWinner': sum(r['first_graduate_mint'] == r['winner_1h_mint'] for r in grad_races),
                   'firstGraduateIs2mLeader': sum(r['first_graduate_mint'] == r['leader_2m_mint'] for r in grad_races),
                   'graduatedMembers': len(graduates),
                   'medianTimeToGraduationMin': statistics.median(number(m['time_to_graduation_min']) for m in graduates),
                   'graduatedUnder2Min': sum(number(m['time_to_graduation_min']) < 2 for m in graduates),
                   'graduationTimeMethod': 'Source proxy: last bonding-curve trade, not independently verified migration receipt'},
    'raceFlags': dict(collections.Counter(v for r in races for v in r['flags'].split('|') if v)),
    'memberFlags': dict(collections.Counter(v for m in members for v in m['flags'].split('|') if v)),
    'curveFamilies': dict(collections.Counter(m['curve_family'] for m in members)),
    'noNetworkAcquisition': True,
    'proof': 'Export arithmetic and ranks verified; underlying chain rows and creator identities not independently verified.',
}
# Bind the article comparison to exact members and explicit role identities.
for race in races:
    ms = groups[race['race_id']]
    by_mint = {m['mint']: m for m in ms}
    assert race['winner_1h_mint'] in by_mint
    assert number(by_mint[race['winner_1h_mint']]['vol_1h_usd']) == max(number(m['vol_1h_usd']) for m in ms)
    if race['leader_2m_mint']:
        assert race['leader_2m_mint'] in by_mint
        assert number(by_mint[race['leader_2m_mint']]['vol_2m_usd']) == max(number(m['vol_2m_usd']) for m in ms)
        assert (race['leader_2m_mint'] == race['winner_1h_mint']) == (race['leader_is_winner_1h'] == '1')
    assert (race['first_launched_mint'] == race['winner_1h_mint']) == (race['first_launched_is_winner_1h'] == '1')
contested = next(c for c in cohorts if c['label'] == 'contested')
assert result['counts'] == {'races': 2511, 'members': 8821, 'allMints': 18075}
assert contested['races'] == 1219 and contested['members'] == 5534
assert contested['leaderWins1h']['yes'] == 1007 and contested['leaderWins1h']['denominator'] == 1219
assert contested['firstLaunchWins1h']['yes'] == 577 and contested['firstLaunchWins1h']['denominator'] == 1219
result['graduation']['verificationStatus'] = 'Export proxy only; selected migration discrepancies documented separately in docs/pilot-migration-discrepancies.json. Export not silently corrected.'
result['phaseVolumeStatus'] = 'Source-proxy USD phase allocation, not independently verified creator-fee accrual.'
(args.out / 'vamp-review.json').write_text(json.dumps(result, indent=2))
for name, rows in [('contested-races.csv', active), ('contested-members.csv', [m for m in members if m['race_id'] in active_ids])]:
    with (args.out / name).open('w', newline='') as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter=';')
        writer.writeheader(); writer.writerows(rows)
proof = {'status': 'PASS', 'sourceHashesVerified': True, 'sourceCounts': result['counts'], 'contestedRaces': 1219, 'contestedMembers': 5534,
         'strongestOpening': {'n': 1007, 'd': 1219, 'displayPct': '82.6%'}, 'firstLaunched': {'n': 577, 'd': 1219, 'displayPct': '47.3%'},
         'scope': 'Offline arithmetic and export role checks. No RPC and no causal or online predictor claim.'}
(args.out / 'verification.json').write_text(json.dumps(proof, indent=2))
print(json.dumps(proof, indent=2))
