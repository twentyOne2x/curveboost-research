"""SDK 4.0.0 PDA seeds using retained pure-Python Solana derivation."""
import json,pathlib
from launchlab_decoder import pda,unb58
SCHEMAS=pathlib.Path(__file__).resolve().parents[1]/'schemas'
PUMP=json.loads((SCHEMAS/'pump.json').read_text())['address']
AMM=json.loads((SCHEMAS/'pump_amm.json').read_text())['address']
FEES=json.loads((SCHEMAS/'pump_fees.json').read_text())['address']
ATA='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'
def derive(program,*seeds):return pda(program,list(seeds))['address']
def sharing_config(mint):return derive(FEES,b'sharing-config',unb58(mint))
def bonding_curve(mint):return derive(PUMP,b'bonding-curve',unb58(mint))
def creator_vault(creator):return derive(PUMP,b'creator-vault',unb58(creator))
def amm_creator_vault(creator):return derive(AMM,b'creator_vault',unb58(creator))
def quote_ata(owner,quote,token_program):return derive(ATA,unb58(owner),unb58(token_program),unb58(quote))
def canonical_pool(mint,quote):
 authority=derive(PUMP,b'pool-authority',unb58(mint))
 return derive(AMM,b'pool',(0).to_bytes(2,'little'),unb58(authority),unb58(mint),unb58(quote))
def social_fee(user_id,platform):return derive(FEES,b'social-fee-pda',user_id.encode(),bytes([platform]))
