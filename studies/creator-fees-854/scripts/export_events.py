"""Offline owner-only bridge from retained case to a private normalized event asset."""
import argparse,csv,datetime,gzip,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def export(case,out):
 out.mkdir(parents=True,exist_ok=True);sources={};cache={}
 def load(rel,expected=None,keep=False):
  if rel not in cache:
   raw=(case/rel).read_bytes();digest=sha(raw)
   if expected is not None:assert digest==expected,(rel,'source hash mismatch')
   sources[rel]={'sha256':digest,'bytes':len(raw)}
   value=json.loads(gzip.decompress(raw) if rel.endswith('.gz') else raw)
   if keep:cache[rel]=value
   return value
  return cache[rel]
 pop=load('outputs/population-volume-20261015/population.json',keep=True)
 manifest=load('work/population-volume-20261015/capture-feasibility/MANIFEST.json',keep=True)
 mapping={r['mint']:r for r in manifest['rows']}
 rows=list(csv.DictReader((ROOT/'data/launches-854.csv').open()))
 path=out/'events-854.jsonl.gz';temp=out/'events-854.jsonl.gz.tmp';count=0
 print(json.dumps({'pid':os.getpid(),'stage':'export','launches':len(rows)}),flush=True)
 with temp.open('wb') as sink,gzip.GzipFile(fileobj=sink,mode='wb',mtime=0,compresslevel=6) as zipped:
  for row in rows:
   mint=row['mint'];source=row['historicalSourceRelativePath'];start=int(datetime.datetime.fromisoformat(row['creationUtc'].replace('Z','+00:00')).timestamp());end=start+3600
   if source.endswith('/summary.json'):
    summary=load(source,pop['sourceHashes'][source]);assert summary['originalSignedCreationObserved'] and summary['completePrimaryVenueFirstHour'] and not summary['decoderErrors']
    origin=str(Path(source).with_name('events.json.gz'));events=load(origin,summary['eventsHash']['gzipSha256'])
   elif row['cohort']=='ram':
    label='Q5' if mint=='7vDhDEUr1HwviaFkDiVFNXoGKfuMgzV5187jkFEVpump' else 'RAM'
    assert label=='Q5' or mint=='F9FYhirL4XGH3TEQDvBRAg6yDLXZeSNJopJcrDNtXjsR'
    origin='outputs/launch-economics-actual-20261014/volume/capture/'+label+'-normalized-trades.json';events=load(origin)
   else:
    reuse=mapping[mint]['reuse'];origin=reuse['source'];value=load(origin,reuse['sha256'],keep=True)
    if origin.endswith('SEVEN.json'):events=[dict(e,venue='Pump',quotePrincipalLamports=e['quotePrincipalRaw'],actualCreatorFeeLamports=e['creatorFeeRaw']) for e in value['records'][mint]['tradeEvents']]
    elif origin.endswith('enriched-first-hour.json.gz'):events=[dict(e,quotePrincipalLamports=e['quoteAmountRaw'],actualCreatorFeeLamports=e['creatorFeeRaw']) for e in value if e['mint']==mint]
    else:
     assert origin.endswith('per-mint.json');origin='outputs/leverage-fee-benchmark-20261014/repricing/events.json';events=[dict(e,venue='Pump' if e['phase']=='curve' else 'PumpSwap',quotePrincipalLamports=e['quotePrincipalRaw'],actualCreatorFeeLamports=e['actualCreatorFeeRaw']) for e in load(origin,keep=True) if e['mint']==mint and start<=e['blockTime']<end]
   for e in events:
    assert start<=e['blockTime']<end and e['venue'] in ['Pump','PumpSwap'] and e['actualCreatorFeeLamports'] is not None
    principal=int(e['quotePrincipalLamports']);fee=int(e['actualCreatorFeeLamports']);assert principal>=0 and fee>=0
    event={'cohort':row['cohort'],'mint':mint,'phase':'curve' if e['venue']=='Pump' else 'amm','blockTime':e['blockTime'],'principalLamports':str(principal),'observedCreatorFeeLamports':str(fee),'event95FloorLamports':str(principal*95//10000),'sourceRelativePath':origin}
    for k in ['signature','payloadSha256','topLevelInstructionIndex','innerInstructionIndex','logIndex','eventOrdinal','eventIndex','slot','transactionIndex','user','isBuy']:event[k]=e.get(k)
    zipped.write((json.dumps(event,separators=(',',':'))+'\n').encode());count+=1
  sink.flush()
 temp.replace(path)
 digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
 result={'schemaVersion':1,'asset':path.name,'sha256':digest,'compressedBytes':path.stat().st_size,'events':count,'launches':len(rows),'sourceInputs':sources,'nullPolicy':'Unavailable source fields explicitly null.','scope':'Historical normalized event export; no raw RPC re-decoding or provider completeness audit.'}
 (out/'event-asset-provenance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sourceInputs'}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();export(a.case,a.out)
