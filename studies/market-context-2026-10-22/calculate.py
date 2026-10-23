from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
raw=(root/'data/launchpad-series.json').read_bytes()
src=json.loads((root/'data/source.json').read_text())
assert hashlib.sha256(raw).hexdigest()==src['sha256']
data=json.loads(raw)
assert data['through']=='2026-10-22' and data['days']==['2026-10-22']
pump=next(x for x in data['series'] if x['chain']=='solana' and x['pad']=='pumpfun')
launches=pump['tokens_launched'][0]
assert launches==46528
r={'dayUTC':data['through'],'launches':launches,'minutes':1440,'launchesPerMinute':launches/1440,'roundedPerMinute':round(launches/1440),'sourceHashVerified':True}
(root/'results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
