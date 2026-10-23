"""Offline, source-bound Pump pilot decoder. No network, environment or credentials."""
import argparse,base64,collections,datetime,gzip,hashlib,importlib.util,json,pathlib,re,sys
sys.dont_write_bytecode=True
SOURCE=pathlib.Path(__file__).resolve().parent/'vendor'
sys.path.insert(0,str(SOURCE/'tools'));import pump_pda as PDA
spec=importlib.util.spec_from_file_location('retained_pilot_decoder',SOURCE/'tools/decoder.py');D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
IDLS={d['address']:d for d in [D.IDL,D.AMM_IDL]};PUMP=D.IDL['address'];AMM=D.AMM_IDL['address'];WSOL='So11111111111111111111111111111111111111112';NATIVE='11111111111111111111111111111111'
TYPES={p:{t['name']:t['type'] for t in d['types']} for p,d in IDLS.items()}
EVENTS={(p,bytes(e['discriminator'])):e['name'] for p,d in IDLS.items() for e in d['events']}
IXS={(p,bytes(i['discriminator'])):i for p,d in IDLS.items() for i in d['instructions']}
class Reader(D.Reader):
 def value(self,t):
  if isinstance(t,dict) and 'array' in t:return [self.value(t['array'][0]) for _ in range(t['array'][1])]
  return super().value(t)
def sha(b):return hashlib.sha256(b).hexdigest()
def stamp(s):return int(datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
def key(a):return a['pubkey'] if isinstance(a,dict) else a
def decode(program,raw):
 name=EVENTS.get((program,raw[:8]))
 if not name:return None
 reader=Reader(raw,TYPES[program]);fields=TYPES[program][name]['fields'];values={};missing=[]
 for i,f in enumerate(fields):
  try:values[f['name']]=reader.value(f['type'])
  except EOFError:missing=[v['name'] for v in fields[i:]];break
 return {'eventName':name,'program':program,'values':values,'missingTrailingFields':missing,'unparsedBytes':len(raw)-reader.position,'unparsedTailHex':raw[reader.position:].hex(),'payloadSha256':sha(raw)}
def normalize(tx):
 # GTFA jsonParsed is expected; compiled forms are resolved explicitly when available.
 msg=tx['transaction']['message'];keys=[key(a) for a in msg['accountKeys']]
 loaded=tx['meta'].get('loadedAddresses',{})
 if not any(isinstance(a,dict) and a.get('source')=='lookupTable' for a in msg['accountKeys']):keys+=loaded.get('writable',[])+loaded.get('readonly',[])
 def ix(i):
  r=dict(i)
  if 'programId' not in r:r['programId']=keys[r['programIdIndex']]
  if 'accounts' in r:r['accounts']=[keys[a] if isinstance(a,int) else key(a) for a in r['accounts']]
  return r
 inn={g['index']:g['instructions'] for g in tx['meta'].get('innerInstructions',[])};flat=[]
 for outer,i in enumerate(msg['instructions']):
  outerid=f'{outer}:outer';flat.append(ix(i)|{'outerIndex':outer,'innerIndex':None,'invocationId':outerid,'parentInvocationId':None});stack={1:outerid}
  for k,j in enumerate(inn.get(outer,[])):
   height=j.get('stackHeight');ident=f'{outer}:{k}';parent=stack.get(height-1) if height else None
   flat.append(ix(j)|{'outerIndex':outer,'innerIndex':k,'invocationId':ident,'parentInvocationId':parent})
   if height:stack={dep:val for dep,val in stack.items() if dep<height};stack[height]=ident
 signers=[key(a) for a in msg['accountKeys'] if isinstance(a,dict) and a.get('signer')]
 if not signers and msg.get('header'):signers=keys[:msg['header']['numRequiredSignatures']]
 return flat,signers

def extract(tx,errors):
 flat,signers=normalize(tx);stack=[];committed=[];failed=False
 for li,line in enumerate(tx['meta'].get('logMessages') or []):
  m=re.fullmatch(r'Program (\w+) invoke \[(\d+)\]',line)
  if m:stack.append({'program':m[1],'events':[]});continue
  m=re.match(r'Program (\w+) (success|failed:)',line)
  if m:
   if not stack or stack[-1]['program']!=m[1]:errors.append({'kind':'log_stack_mismatch','line':li});continue
   frame=stack.pop()
   if m[2]=='success':
    if stack:stack[-1]['events']+=frame['events']
    else:committed+=frame['events']
   else:failed=True
   continue
  if line.startswith('Program data: ') and stack and stack[-1]['program'] in IDLS:
   try:
    raw=base64.b64decode(line[14:],validate=True);ev=decode(stack[-1]['program'],raw)
    if ev:stack[-1]['events'].append(ev|{'location':{'logIndex':li},'_raw':raw})
   except Exception as e:errors.append({'kind':'event_decode','line':li,'error':type(e).__name__})
 if stack:errors.append({'kind':'unterminated_log_stack'})
 # Match log/CPI copies by occurrence; never collapse two actual identical events.
 copies=collections.Counter((e['program'],e['payloadSha256']) for e in committed)
 for i in flat:
  if i['programId'] not in IDLS or not i.get('data'):continue
  try:raw=D.unb58(i['data'])
  except Exception as e:errors.append({'kind':'instruction_encoding','error':type(e).__name__});continue
  if raw[:8]!=D.EVENT_CPI_TAG:continue
  raw=raw[8:];tag=(i['programId'],sha(raw))
  if copies[tag]:copies[tag]-=1;continue
  if failed:
   errors.append({'kind':'cpi_event_excluded_ambiguous_failed_invocation','outerIndex':i['outerIndex'],'innerIndex':i['innerIndex']});continue
  try:
   ev=decode(i['programId'],raw)
   if ev:committed.append(ev|{'location':{'outerIndex':i['outerIndex'],'innerIndex':i['innerIndex']},'_raw':raw})
  except Exception as e:errors.append({'kind':'cpi_event_decode','error':type(e).__name__})
 instructions=[];initializations=[]
 for i in flat:
  parsed=i.get('parsed',{})
  if isinstance(parsed,dict) and parsed.get('type') in ['initializeMint','initializeMint2']:initializations.append(parsed.get('info',{}).get('mint'))
  if i['programId'] not in IDLS or not i.get('data'):continue
  try:
   schema=IXS.get((i['programId'],D.unb58(i['data'])[:8]))
   if schema and schema['name'] in ['create','create_v2','migrate','migrate_v2','create_pool']:
    instructions.append({'program':i['programId'],'name':schema['name'],'accounts':{a['name']:v for a,v in zip(schema['accounts'],i.get('accounts',[]))},'location':{'outerIndex':i['outerIndex'],'innerIndex':i['innerIndex']},'instructionSuccess':'ambiguous_internal_failure' if failed else 'transaction_success_no_failed_logs'})
  except Exception as e:errors.append({'kind':'instruction_decode','error':type(e).__name__})
 for e in committed:
  e.pop('_raw',None)
  if e['program']!=AMM or e['eventName'] not in ['BuyEvent','SellEvent']:continue
  v=e['values'];buy=e['eventName']=='BuyEvent';matches=[]
  for ix in flat:
   if ix['programId']==AMM and ix.get('data'):
    raw=D.unb58(ix['data'])
    if raw[:8]==D.EVENT_CPI_TAG and sha(raw[8:])==e['payloadSha256']:matches.append(ix)
  parents={ix['parentInvocationId'] for ix in matches}
  legs=[]
  if len(parents)==1 and None not in parents:
   parent=next(iter(parents))
   for ix in flat:
    parsed=ix.get('parsed',{});info=parsed.get('info',{}) if isinstance(parsed,dict) else {}
    if ix['parentInvocationId']!=parent or parsed.get('type') not in ['transfer','transferChecked']:continue
    if ix['programId'] not in ['TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA','TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb']:continue
    if (buy and info.get('source')==v.get('user_quote_token_account')) or (not buy and info.get('destination')==v.get('user_quote_token_account')):
     amt=info.get('amount',info.get('tokenAmount',{}).get('amount'))
     if amt is not None:legs.append({'source':info.get('source'),'destination':info.get('destination'),'amountRaw':str(amt),'outerIndex':ix['outerIndex'],'innerIndex':ix['innerIndex']})
  e['actualQuoteTransferWitness']=legs
  e['actualUserQuoteTransferRaw']=str(sum(int(x['amountRaw']) for x in legs)) if legs else None

 return committed,instructions,signers,initializations

def analyze(capture,manifest,out):
 out.mkdir(parents=True,exist_ok=True);summaryraw=(capture/'summary.json').read_bytes();summary=json.loads(summaryraw);(out/'capture-summary-input.json').write_bytes(summaryraw);pilot=json.loads(manifest.read_text())['pilot'];errors=[];transactions={};streams=[s for s in summary.get('streams',[]) if s.get('mint') in {p['mint'] for p in pilot}];duplicates=0;coverage=[];sourcehashes=[]
 for stream in streams:
  pages=stream.get('pages',[]);last=None;ok=True
  for page in pages:
   rel=page['path'];p=(capture/rel).resolve()
   if not p.is_relative_to(capture.resolve()):raise ValueError('page outside capture root')
   packed=p.read_bytes();raw=gzip.decompress(packed) if p.suffix=='.gz' else packed
   actual=sha(raw);want=page.get('rawSha256');sourcehashes.append({'path':rel,'rawSha256':actual})
   if want!=actual:errors.append({'kind':'raw_hash_mismatch','path':rel});ok=False;continue
   if page.get('cursorIn')!=last:errors.append({'kind':'cursor_chain_mismatch','path':rel});ok=False
   last=page.get('cursorOut');envelope=json.loads(raw);data=envelope.get('result',{}).get('data')
   if not isinstance(data,list):errors.append({'kind':'missing_page_data','path':rel});ok=False;continue
   if page.get('count')!=len(data):errors.append({'kind':'page_count_mismatch','path':rel});ok=False
   for tx in data:
    try:sig=tx['transaction']['signatures'][0]
    except Exception:errors.append({'kind':'transaction_shape','path':rel});continue
    if sig in transactions:
     duplicates+=1
     if transactions[sig]['tx']!=tx:errors.append({'kind':'duplicate_transaction_conflict','signature':sig});ok=False
     transactions[sig]['sources'].append(rel)
    else:transactions[sig]={'tx':tx,'sources':[rel]}
  coverage.append({k:stream.get(k) for k in ['mint','phase','address','window','terminal','coverageStatus']}|{'pageCount':len(pages),'verifiedRawAndCursorChain':ok,'terminalPageCursorEmpty':last is None,'scope':'Only collector-named curve/canonical pool; not all venues.'})
 events=[];witnesses=[];failedtx=[]
 for sig,t in transactions.items():
  tx=t['tx'];base={'signature':sig,'slot':tx.get('slot'),'blockTime':tx.get('blockTime'),'transactionIndex':tx.get('transactionIndex'),'sourcePages':t['sources']}
  if tx.get('meta',{}).get('err') is not None:failedtx.append(base);continue
  if tx.get('version') not in [None,'legacy',0,1]:errors.append(base|{'kind':'unsupported_transaction_version','version':tx.get('version')});continue
  local=[]
  try:evs,ixs,signers,inits=extract(tx,local)
  except Exception as e:errors.append(base|{'kind':'transaction_decode','error':type(e).__name__});continue
  errors.extend(base|e for e in local)
  for e in evs:
   e['invocationCommitStatus']='ambiguous_truncated_logs' if any(x['kind'] in ['unterminated_log_stack','log_stack_mismatch'] for x in local) else 'successful_transaction_and_no_unresolved_log_path';events.append(base|e)
   if e['unparsedBytes']:errors.append(base|{'kind':'unparsed_event_bytes','eventName':e['eventName'],'count':e['unparsedBytes']})
  for i in ixs:witnesses.append(base|i|{'signers':signers,'initializedMints':inits})
 events.sort(key=lambda e:(e['slot'] or -1,e['transactionIndex'] if e['transactionIndex'] is not None else -1,e['signature'],e['location'].get('logIndex',999999),e['location'].get('outerIndex',999999),e['location'].get('innerIndex') or -1))
 ledgers=[];reports=[]
 for item in pilot:
  mint=item['mint'];start=stamp(item['firstTradeUTC']);end=stamp(item['ownHourEndUTC']);related=[s for s in streams if s.get('mint')==mint];addresses={s['phase']:s['address'] for s in related};pool=addresses.get('amm');expected_curve=PDA.bonding_curve(mint);expected_pool=PDA.canonical_pool(mint,WSOL)
  addresses_match=addresses.get('curve')==expected_curve and pool==expected_pool
  if not addresses_match:errors.append({'kind':'stream_pda_mismatch_or_missing','mint':mint})
  creation=[w for w in witnesses if w['program']==PUMP and w['name'] in ['create','create_v2'] and w['accounts'].get('mint')==mint]
  createproof=[w for w in creation if w['accounts'].get('user') in w['signers'] and mint in w['initializedMints'] and w['instructionSuccess']=='transaction_success_no_failed_logs']
  migrations=[w for w in witnesses if w['program']==PUMP and w['name'] in ['migrate','migrate_v2'] and w['accounts'].get('mint',w['accounts'].get('base_mint'))==mint and w['instructionSuccess']=='transaction_success_no_failed_logs']
  me=[e for e in events if e['eventName']=='CompletePumpAmmMigrationEvent' and e['values'].get('mint')==mint]
  pe=[e for e in events if e['eventName']=='CreatePoolEvent' and e['values'].get('base_mint')==mint]
  # Pool association must be witnessed by exact mint migration ix + event, not collector label alone.
  bound=[e for e in me if addresses_match and e['values'].get('bonding_curve')==expected_curve and e['values'].get('pool')==pool and any(w['signature']==e['signature'] and w['accounts'].get('pool')==pool and w['accounts'].get('bonding_curve')==expected_curve for w in migrations)]
  poolproof=[e for e in pe if e['values'].get('pool')==pool and e['values'].get('quote_mint')==WSOL and e['values'].get('index')=='0' and any(b['signature']==e['signature'] for b in bound)]
  csvstart=start;csvend=end
  creation_time=min((w['blockTime'] for w in createproof if w['blockTime'] is not None),default=None)
  firsts=[e['blockTime'] for e in events if e['eventName']=='TradeEvent' and e['values'].get('mint')==mint and e['blockTime'] is not None and creation_time is not None and e['blockTime']>=creation_time]
  actualfirst=min(firsts) if firsts else None
  if actualfirst is not None:start=actualfirst;end=start+3600
  rows=[]
  for e in events:
   v=e['values'];name=e['eventName'];phase=None;amount=None;fee=None
   if e['program']==PUMP and name=='TradeEvent' and v.get('mint')==mint:
    phase='curve';q=v.get('quote_mint');amount=v.get('quote_amount') if q and q not in [NATIVE,WSOL] else v.get('sol_amount');fee=v.get('creator_fee')
    if q and q not in [NATIVE,WSOL]:errors.append({'kind':'non_SOL_quote','mint':mint,'signature':e['signature']});continue
   elif e['program']==AMM and name in ['BuyEvent','SellEvent'] and v.get('pool')==pool:
    if not poolproof:continue
    phase='amm';fee=v.get('coin_creator_fee')
    if name=='BuyEvent':
     ixname=v.get('ix_name')
     if ixname in ['buy_exact_quote_in','buy_exact_quote_in_v2']:amount=v.get('user_quote_amount_in')
     elif ixname in ['buy','buy_v2']:amount=v.get('quote_amount_in')
     else:amount=None;errors.append({'kind':'unknown_buy_principal_semantics','mint':mint,'signature':e['signature'],'ixName':ixname})
    else:amount=v.get('quote_amount_out')
    total=e.get('actualUserQuoteTransferRaw');fee_parts=[v.get(k) for k in ['lp_fee','protocol_fee','coin_creator_fee','cashback']]
    if total is None or amount is None:errors.append({'kind':'quote_transfer_reconciliation_unavailable','mint':mint,'signature':e['signature']})
    elif all(f is not None for f in fee_parts):
     expected=int(amount)+sum(map(int,fee_parts)) if name=='BuyEvent' else int(amount)-sum(map(int,fee_parts))
     if int(total)!=expected:errors.append({'kind':'quote_transfer_reconciliation_mismatch','mint':mint,'signature':e['signature'],'actual':total,'expected':str(expected),'ixName':v.get('ix_name')})
   elif e['program']==PUMP and name=='PostCompleteBuyEvent' and v.get('mint')==mint:
    errors.append({'kind':'post_complete_buy_requires_separate_phase','mint':mint,'signature':e['signature']});continue
   if not phase:continue
   bt=e['blockTime']
   if bt is None:errors.append({'kind':'missing_blocktime','signature':e['signature']});continue
   if not(min(start,csvstart)<=bt<max(end,csvend)):continue
   row={k:e[k] for k in ['signature','slot','blockTime','transactionIndex','sourcePages','eventName','program','location','payloadSha256','missingTrailingFields','unparsedBytes','invocationCommitStatus']}
   row.update(actualUserQuoteTransferRaw=e.get('actualUserQuoteTransferRaw'),actualQuoteTransferWitness=e.get('actualQuoteTransferWitness'),instructionName=v.get('ix_name'),inActualOwnHour=(start<=bt<end) if actualfirst is not None else None,inCsvOwnHour=csvstart<=bt<csvend,mint=mint,phase=phase,quoteAsset='SOL/WSOL',principalLamports=amount,creatorFeeLamports=fee,cashbackLamports=v.get('cashback'),holderRewardsLamports=v.get('holder_rewards'),creatorFeeUnclaimedLamports=v.get('creator_fee_unclaimed'),user=v.get('user'),eventTimestamp=v.get('timestamp'),isBuy=v.get('is_buy') if phase=='curve' else name=='BuyEvent',feeBps=v.get('creator_fee_basis_points') if phase=='curve' else v.get('coin_creator_fee_basis_points'))
   holder=v.get('holder_rewards');cashback=v.get('cashback')
   row['creatorFeeFieldMeaning']='Gross event creator-fee component, including any holder-routed amount; not wallet income or receipt.'
   row['observedFeeMode']='holder_rewards' if holder is not None and int(holder)>0 else 'cashback' if cashback is not None and int(cashback)>0 else 'creator_fee_component' if fee is not None and int(fee)>0 else 'zero_reported_fee_components' if fee=='0' and holder=='0' and cashback=='0' else 'unknown_or_legacy_fields'
   row['holderRewardRelationship']='Same charged creator-fee component, also reported as holder_rewards; counted once in quote reconciliation.' if holder is not None and fee is not None and int(holder)>0 and int(holder)==int(fee) else 'No positive holder reward observed' if holder=='0' else 'Unresolved holder/creator component relationship'
   row['creatorWalletAccrualComponentLamports']=str(int(fee)-int(holder)) if fee is not None and holder is not None and 0<=int(holder)<=int(fee) else None
   row['creatorWalletAccrualComponentMeaning']='Event component after holder-routing subtraction; not a proven wallet receipt or recipient ownership. Cashback is separately charged/reported.'
   rows.append(row)
  ledgers+=rows;phase_totals={}
  for phase in ['curve','amm']:
   rr=[r for r in rows if r['phase']==phase and (r['inActualOwnHour'] is True if actualfirst is not None else r['inCsvOwnHour'])];ss=[c for c in coverage if c['mint']==mint and c['phase']==phase];complete=bool(ss) and all(s['terminal'] is True and s['coverageStatus']=='provider_terminal' and s['verifiedRawAndCursorChain'] and s['terminalPageCursorEmpty'] and isinstance(s['window'],dict) and s['window'].get('gte',start+1)<=start and s['window'].get('lt',end-1)>=end for s in ss)
   issue_signatures={e.get('signature') for e in errors};quote_issue_signatures={e.get('signature') for e in errors if e['kind'].startswith('quote_transfer_')};phase_totals[phase]={'decodedEvents':len(rr),'windowCoverage':ss,'collectorTerminalAndHashesVerified':complete,'ambiguousInvocationTradeEvents':sum(r['invocationCommitStatus']=='ambiguous_truncated_logs' for r in rr),'schemaAndLogClosure':bool(rr) and all(not r['unparsedBytes'] and not r['missingTrailingFields'] and r['signature'] not in issue_signatures for r in rr),'quoteTransferReconciledEvents':sum(r.get('actualUserQuoteTransferRaw') is not None and r['signature'] not in quote_issue_signatures for r in rr) if phase=='amm' else None}
   for col in ['principalLamports','creatorFeeLamports','cashbackLamports','holderRewardsLamports','creatorWalletAccrualComponentLamports']:
    vals=[int(r[col]) for r in rr if r[col] is not None];phase_totals[phase][col]={'decodedSubtotal':str(sum(vals)) if vals else None,'knownEvents':len(vals),'missingEvents':len(rr)-len(vals),'scope':'decoded events only; not a complete amount unless source coverage and schema closure independently establish it'}
  actual=bound[0]['blockTime'] if bound else None
  reports.append({'mint':mint,'raceId':item['raceId'],'firstTradeUTC':item['firstTradeUTC'],'ownHourEndUTC':item['ownHourEndUTC'],'actualFirstTradeBlockTime':actualfirst,'actualFirstTradeMinusCsvSeconds':actualfirst-csvstart if actualfirst is not None else None,'actualOwnHourEndBlockTime':end if actualfirst is not None else None,'amountWindow':'actual first trade through +3600s' if actualfirst is not None else 'CSV first trade through +3600s; actual first trade unknown','csvWindowDecodedSubtotals':{phase:{col:str(sum(int(r[col]) for r in rows if r['phase']==phase and r['inCsvOwnHour'] and r[col] is not None)) if any(r['phase']==phase and r['inCsvOwnHour'] and r[col] is not None for r in rows) else None for col in ['principalLamports','creatorFeeLamports','cashbackLamports']} for phase in ['curve','amm']},'reportedProxyUTC':item['proxyGraduationUTC'],'migrationBlockTime':actual,'migrationMinusProxySeconds':actual-stamp(item['proxyGraduationUTC']) if actual is not None else None,'signedCreationWitnesses':createproof,'unprovedCreationCandidates':creation if not createproof else [],'migrationInstructionWitnesses':migrations,'migrationEvents':bound,'sameTransactionPoolCreationEvents':poolproof,'derivedBondingCurve':expected_curve,'derivedCanonicalPool':expected_pool,'streamAddressesMatchDerivedPdas':addresses_match,'poolBindingProved':bool(poolproof),'feeModeCountsActualWindow':dict(collections.Counter(r['observedFeeMode'] for r in rows if r['inActualOwnHour'] is True)),'feeModeCountsCsvWindow':dict(collections.Counter(r['observedFeeMode'] for r in rows if r['inCsvOwnHour'])),'feeRoutingNote':'holder_rewards is a routed portion of the charged creator-fee field, not another fee. Confirmed by actual quote-transfer equalities and official PumpSwap holder-reward description. Cashback remains separately reported; receipt/ownership not established.','phases':phase_totals,'orderingLimit':'Slot + transactionIndex + event location when supplied. Missing transactionIndex means exact inter-transaction order within a slot is unknown.'})
 result={'sourceSummarySha256':sha(summaryraw),'manifestSha256':sha(manifest.read_bytes()),'schemas':{p.name:sha(p.read_bytes()) for p in (SOURCE/'schemas').glob('pump*.json')},'decoderSha256':sha((SOURCE/'tools/decoder.py').read_bytes()),'transactions':len(transactions),'duplicatePageOccurrences':duplicates,'failedTransactionsExcluded':failedtx,'coverage':coverage,'mints':reports,'errors':errors,'feeFieldAccounting':'creatorFeeLamports is the gross event creator-fee field; holderRewardsLamports overlaps it and must never be added. creatorWalletAccrualComponentLamports subtracts holder routing, not proof of wallet income/receipt. Cashback is a separate charged component.','proofCeiling':'Observed decoded gross accrual, not claims, profit, demand uplift or all-venue coverage. Missing fields/streams remain unknown. All traders retained. No historical 854 fee values changed.'}
 (out/'ledger.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in ledgers));(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events));(out/'errors.json').write_text(json.dumps(errors,indent=2));(out/'source-pages.json').write_text(json.dumps(sourcehashes,indent=2))
 mode_lines=[f"- {r['mint']}: {json.dumps(r['feeModeCountsActualWindow'],sort_keys=True)}" for r in reports]
 lines=['# Offline migration pilot decode','',f'{len(transactions)} unique transactions; {len(ledgers)} bound own-hour trade events; {len(errors)} retained decoder/coverage issues.','',f'Signed creation proved: {sum(bool(r["signedCreationWitnesses"]) for r in reports)}/{len(reports)}. Migration + same-transaction pool creation binding: {sum(r["poolBindingProved"] for r in reports)}/{len(reports)}.','','See summary.json for per-mint phase subtotals, unknown fields, source coverage and proxy timing differences. No missing amount is promoted to zero; no USD fee conversion.','','These are decoded accrual subtotals, not claims, profit or causal Boost outcomes.']
 lines+=['','## Event fee modes','',*mode_lines,'','Gross creator-fee fields include holder-routed amounts where reported. Holder rewards are not added again. These fields do not prove creator-wallet income or receipt.'];(out/'REPORT.md').write_text('\n'.join(lines)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--capture',type=pathlib.Path,required=True);p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();r=analyze(a.capture,a.manifest,a.out);print(json.dumps({'mints':len(r['mints']),'transactions':r['transactions'],'errors':len(r['errors'])}))
