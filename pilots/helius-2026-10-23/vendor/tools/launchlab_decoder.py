"""Bounded, offline LaunchLab census: exact account bytes and retained receipts.

Standard library only. No network, wallet, signing, or mutable service methods.
Run the copied script from the deliverable folder, optionally with --out DIR.
Extends retained inventory IDL/Borsh and fee account decoding conventions.
"""
import argparse, base64, collections, csv, datetime, decimal, hashlib, json, pathlib, re

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
LL = 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj'
CP = 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C'
decimal.getcontext().prec = 60

def b58(raw):
    n = int.from_bytes(raw, 'big'); s = ''
    while n:
        n, r = divmod(n, 58); s = ALPHABET[r] + s
    return '1' * (len(raw) - len(raw.lstrip(b'\0'))) + s

def unb58(s):
    n = 0
    for c in s: n = n * 58 + ALPHABET.index(c)
    return b'\0' * (len(s) - len(s.lstrip('1'))) + (n.to_bytes((n.bit_length()+7)//8, 'big') if n else b'')

def is_edwards_point(raw):
    p = 2**255-19; y = int.from_bytes(raw, 'little') & (2**255-1)
    if y >= p: return False
    d = -121665 * pow(121666, p-2, p) % p
    x2 = (y*y-1) * pow((d*y*y+1) % p, p-2, p) % p
    x = pow(x2, (p+3)//8, p)
    if x*x % p != x2: x = x * pow(2, (p-1)//4, p) % p
    return x*x % p == x2

def pda(program, seeds):
    for bump in range(255, -1, -1):
        q = hashlib.sha256(b''.join(seeds)+bytes([bump])+unb58(program)+b'ProgramDerivedAddress').digest()
        if not is_edwards_point(q): return {'address': b58(q), 'bump': bump, 'program': program, 'seedsHex': [s.hex() for s in seeds]}
    raise ValueError('No valid PDA')

def utc(t): return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def key(k): return k['pubkey'] if isinstance(k, dict) else k
def instructions(tx):
    inner = {g['index']: g['instructions'] for g in tx['meta'].get('innerInstructions', [])}
    for i, ix in enumerate(tx['transaction']['message']['instructions']):
        yield dict(ix, topLevelInstructionIndex=i, innerInstructionIndex=None)
        for n, q in enumerate(inner.get(i, [])): yield dict(q, topLevelInstructionIndex=i, innerInstructionIndex=n)

class Reader:
    def __init__(self, raw, types): self.raw=raw; self.pos=8; self.types=types
    def take(self, n):
        if self.pos+n > len(self.raw): raise EOFError((self.pos, n, len(self.raw)))
        q=self.raw[self.pos:self.pos+n]; self.pos+=n; return q
    def value(self, t):
        if t=='pubkey': return b58(self.take(32))
        if t=='bool':
            q=self.take(1)[0]; assert q in (0,1); return bool(q)
        if t=='string': return self.take(int.from_bytes(self.take(4),'little')).decode()
        if isinstance(t,str) and t[:1] in ('u','i') and t[1:].isdigit(): return str(int.from_bytes(self.take(int(t[1:])//8),'little',signed=t[0]=='i'))
        if isinstance(t,dict) and 'array' in t: return [self.value(t['array'][0]) for _ in range(t['array'][1])]
        if isinstance(t,dict) and 'vec' in t: return [self.value(t['vec']) for _ in range(int.from_bytes(self.take(4),'little'))]
        if isinstance(t,dict) and 'option' in t: return self.value(t['option']) if self.take(1)[0] else None
        if isinstance(t,dict) and 'defined' in t:
            definition=self.types[t['defined']['name']]
            if definition['kind']=='enum':
                variant=definition['variants'][self.take(1)[0]]
                if not variant.get('fields'): return variant['name']
                fs=variant['fields']; return {'variant':variant['name'],'fields':{f['name']:self.value(f['type']) for f in fs} if isinstance(fs[0],dict) and 'name' in fs[0] else [self.value(f.get('type',f) if isinstance(f,dict) else f) for f in fs]}
            return {f['name']:self.value(f['type']) for f in definition['fields']}
        raise ValueError(t)
