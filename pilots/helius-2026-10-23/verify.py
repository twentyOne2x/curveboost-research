"""Focused offline package verification; no network and no full analysis rerun."""
import argparse,gzip,hashlib,importlib.util,json,pathlib,sys,tarfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=pathlib.Path);p.add_argument('--archive',type=pathlib.Path);a=p.parse_args()
 spec=importlib.util.spec_from_file_location('portable_analyzer',ROOT/'analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 manifest=json.loads((ROOT/'inputs/pilot-manifest.json').read_text());plan=json.loads((ROOT/'capture/plan.json').read_text());assert len(manifest['pilot'])==12
 for subject in manifest['pilot']:
  streams={r['phase']:r['address'] for r in plan['streams'] if r['mint']==subject['mint']}
  assert streams['curve']==m.PDA.bonding_curve(subject['mint']);assert streams['amm']==m.PDA.canonical_pool(subject['mint'],m.WSOL)
 provenance=json.loads((ROOT/'PROVENANCE.json').read_text())
 for n,h in provenance['vendoredFiles'].items():assert sha((ROOT/n).read_bytes())==h,n
 source=json.loads((ROOT/'results/source-pages.json').read_text());sample=source[0];checked=0
 if a.archive:
  asset=json.loads((ROOT/'PRIVATE-ASSET.json').read_text());assert sha(a.archive.read_bytes())==asset['sha256']
  hashes=json.loads((ROOT/'results/compressed-page-hashes.json').read_text())
  with tarfile.open(a.archive,'r|gz') as t:
   for entry in t:
    prefix='helius-pilot-evidence/capture/'
    if entry.name.startswith(prefix) and entry.name[len(prefix):] in hashes:
     rel=entry.name[len(prefix):];b=t.extractfile(entry).read();assert sha(b)==hashes[rel],rel
     if rel==sample['path']:assert sha(gzip.decompress(b))==sample['rawSha256']
     checked+=1
 elif a.evidence:
  hashes=json.loads((ROOT/'results/compressed-page-hashes.json').read_text())
  summary=json.loads((a.evidence/'capture/summary.json').read_text())
  for stream in summary['streams']:
   for page in stream['pages']:
    b=(a.evidence/'capture'/page['path']).read_bytes();assert sha(b)==hashes[page['path']]
    if page['path']==sample['path']:assert sha(gzip.decompress(b))==sample['rawSha256']
    checked+=1
 else:p.error('supply --archive or --evidence')
 assert checked==len(source)==595
 print(json.dumps({'status':'PASS','vendoredImports':True,'derivedPdaPairs':12,'pagesPresent':checked,'sampleRawHashVerified':True,'fullAnalysisRerun':False,'networkCalls':0}))
if __name__=='__main__':main()
