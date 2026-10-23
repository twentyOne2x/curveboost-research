"""Reproduce article aggregate from exact saved per-event floor sums. Offline stdlib."""
import csv
from decimal import Decimal as D, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'pigeon':(583,3604627644417,6000318444577),'ram':(271,807507512206,1583142686732)}
def sol(n): return format(D(n)/D(10**9),'.9f')
def usd(n): return str((D(n)/D(10**9)*D('107.24')).quantize(D('1'),rounding=ROUND_HALF_UP))
def calculate():
 raw=(ROOT/'data/launches-854.csv').read_bytes()
 rows=list(csv.DictReader(raw.decode().splitlines()));assert len(rows)==854
 assert len({r['mint'] for r in rows})==854
 out=[]
 for cohort,(count,actual_expected,reprice_expected) in EXPECTED.items():
  part=[r for r in rows if r['cohort']==cohort];assert len(part)==count
  actual=sum(int(r['curve_actualFeeRaw'])+int(r['amm_actualFeeRaw']) for r in part)
  counter=sum(int(r['curve_fee95FloorRaw'])+int(r['amm_actualFeeRaw']) for r in part)
  assert(actual,counter)==(actual_expected,reprice_expected)
  out.append(dict(cohort=cohort,launches=count,actualFeeLamports=str(actual),curveOnly95FeeLamports=str(counter),actualFeeSOL=sol(actual),curveOnly95FeeSOL=sol(counter),upliftSOL=sol(counter-actual),actualUSDHistoricalDisplay=usd(actual),curveOnly95USDHistoricalDisplay=usd(counter)))
 result={'inputSha256':hashlib.sha256(raw).hexdigest(),'rows':854,'quoteAsset':'native SOL / WSOL','integerScale':'1000000000 lamports per SOL','valuation':{'USDperSOL':'107.24','capturedUTC':'2026-10-14T12:02:16.847966Z','kind':'single historical display valuation, not event-time USD or present value'},'formula':'actual=sum(curve_actualFeeRaw+amm_actualFeeRaw); counterfactual=sum(curve_fee95FloorRaw+amm_actualFeeRaw). curve_fee95FloorRaw is the saved SUM over events of floor(principalLamports*95/10000).','results':out}
 (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__': print(json.dumps(calculate()['results'],indent=2))
