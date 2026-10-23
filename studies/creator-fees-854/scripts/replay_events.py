"""Stream private normalized events; independently recompute every event's95bps floor."""
import argparse,collections,csv,datetime,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def replay(asset):
 rows=list(csv.DictReader((ROOT/'data/launches-854.csv').open()));expected={r['mint']:r for r in rows};totals=collections.defaultdict(collections.Counter);count=0;last=None;completed=set();identities=set()
 with gzip.open(asset,'rt') as handle:
  for line in handle:
   e=json.loads(line);mint=e['mint'];row=expected[mint];assert e['cohort']==row['cohort'];assert e['phase'] in ['curve','amm']
   if mint!=last:
    if last is not None:completed.add(last)
    assert mint not in completed;identities=set();last=mint
   identity=tuple(e.get(k) for k in ['signature','payloadSha256','topLevelInstructionIndex','innerInstructionIndex','logIndex','eventOrdinal','eventIndex']);assert any(x is not None for x in identity);assert identity not in identities;identities.add(identity)
   start=int(datetime.datetime.fromisoformat(row['creationUtc'].replace('Z','+00:00')).timestamp());assert start<=e['blockTime']<start+3600
   principal=int(e['principalLamports']);fee=int(e['observedCreatorFeeLamports']);assert principal>=0 and fee>=0
   independently_repriced=principal*95//10000
   assert independently_repriced==int(e['event95FloorLamports'])
   totals[(mint,e['phase'])].update(volumeRaw=principal,actualFeeRaw=fee,fee95FloorRaw=independently_repriced,events=1,zeroFeeEvents=int(fee==0));count+=1
 for row in rows:
  for phase in ['curve','amm']:
   for field in ['volumeRaw','actualFeeRaw','fee95FloorRaw','events','zeroFeeEvents']:
    assert totals[(row['mint'],phase)][field]==int(row[phase+'_'+field]),(row['mint'],phase,field)
 assert len(rows)==854 and count==1759593
 digest=hashlib.file_digest(asset.open('rb'),'sha256').hexdigest()
 assert digest==json.loads((ROOT/'data/event-asset-provenance.json').read_text())['sha256'],'asset hash mismatch'
 result={'events':count,'launches':len(rows),'phaseFieldEqualities':len(rows)*2*5,'assetSha256':digest,'result':'PASS','method':'95bps floor independently computed from every event principal; complete per-launch phase volume/observed fee/floor/eventcount/zero-feecount equality.'}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--events',type=Path,required=True);p.add_argument('--out',type=Path);a=p.parse_args();r=replay(a.events)
 if a.out:a.out.write_text(json.dumps(r,indent=2)+'\n')
