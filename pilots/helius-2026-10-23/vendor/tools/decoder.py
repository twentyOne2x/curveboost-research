"""Generic retained Borsh/instruction decoder; Python standard library only."""
import decimal, datetime, json, pathlib
SCHEMAS = pathlib.Path(__file__).resolve().parents[1] / 'schemas'
IDL = json.loads((SCHEMAS/'pump.json').read_text())
FEE_IDL = json.loads((SCHEMAS/'pump_fees.json').read_text())
AMM_IDL = json.loads((SCHEMAS/'pump_amm.json').read_text())
TYPES = {t['name']: t['type'] for t in IDL['types']}
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
EVENT_CPI_TAG = bytes.fromhex('e445a52e51cb9a1d')
decimal.getcontext().prec = 50
def b58(raw):
    n = int.from_bytes(raw, "big")
    result = ""
    while n:
        n, rem = divmod(n, 58)
        result = ALPHABET[rem] + result
    return "1" * (len(raw) - len(raw.lstrip(b"\0"))) + result

def unb58(value):
    n = 0
    for char in value:
        n = n * 58 + ALPHABET.index(char)
    return b"\0" * (len(value) - len(value.lstrip("1"))) + (n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b"")

def units(n, decimals):
    return format(decimal.Decimal(n) / decimal.Decimal(10 ** decimals), "f")

def utc(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def tx_url(sig):
    return "https://solscan.io/tx/" + sig

class Reader:
    def __init__(self, raw, types=None):
        self.raw = raw
        self.position = 8
        self.types = types or TYPES

    def take(self, count):
        if self.position + count > len(self.raw):
            raise EOFError()
        result = self.raw[self.position:self.position + count]
        self.position += count
        return result

    def value(self, typ):
        if typ == "pubkey":
            return b58(self.take(32))
        if typ == "bool":
            value = self.take(1)[0]
            if value > 1:
                raise ValueError("Invalid Borsh bool")
            return bool(value)
        if isinstance(typ, str) and typ[:1] in {"u", "i"} and typ[1:].isdigit():
            return str(int.from_bytes(self.take(int(typ[1:]) // 8), "little", signed=typ[0] == "i"))
        if typ == "string":
            return self.take(int.from_bytes(self.take(4), "little")).decode("utf-8")
        if isinstance(typ, dict) and "vec" in typ:
            return [self.value(typ["vec"]) for _ in range(int.from_bytes(self.take(4), "little"))]
        if isinstance(typ, dict) and "defined" in typ:
            definition = self.types[typ["defined"]["name"]]
            if definition["kind"] == "enum":
                variant = definition["variants"][self.take(1)[0]]
                if variant.get("fields"):
                    raise ValueError("Enum with fields requires explicit decoder")
                return variant["name"]
            fields = definition["fields"]
            if fields and isinstance(fields[0], str):
                return [self.value(field) for field in fields]
            return {field["name"]: self.value(field["type"]) for field in fields}
        if isinstance(typ, dict) and "option" in typ:
            return self.value(typ["option"]) if self.take(1)[0] else None
        raise ValueError("Unsupported IDL field type: " + str(typ))

def flatten_instructions(tx):
    """Assign parent programs using recorded stackHeight, preserving execution order."""
    inner = {group["index"]: group["instructions"] for group in tx["meta"].get("innerInstructions", [])}
    result = []
    for outer_index, instruction in enumerate(tx["transaction"]["message"]["instructions"]):
        result.append({**instruction, "topLevelInstructionIndex": outer_index, "innerInstructionIndex": None, "parentProgram": None})
        stack = {1: instruction["programId"]}
        for inner_index, ix in enumerate(inner.get(outer_index, [])):
            height = ix.get("stackHeight")
            result.append({**ix, "topLevelInstructionIndex": outer_index, "innerInstructionIndex": inner_index,
                           "parentProgram": stack.get(height - 1) if height else None})
            if height:
                stack = {depth: value for depth, value in stack.items() if depth < height}
                stack[height] = ix["programId"]
    return result
