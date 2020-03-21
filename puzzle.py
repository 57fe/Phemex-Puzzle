from typing import Union
import bitcoin

# 58 character alphabet used
BITCOIN_ALPHABET = \
    b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
RIPPLE_ALPHABET = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
alphabet = BITCOIN_ALPHABET

def scrub_input(v: Union[str, bytes]) -> bytes:
    if isinstance(v, str):
        v = v.encode('ascii')
    return v

def b58encode_int(
    i: int, default_one: bool = True, alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    if not i and default_one:
        return alphabet[0:1]
    string = b""
    while i:
        i, idx = divmod(i, 58)
        string = alphabet[idx:idx+1] + string
    return string

def b58encode(
    v: Union[str, bytes], alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    v = scrub_input(v)
    nPad = len(v)
    v = v.lstrip(b'\0')
    nPad -= len(v)
    p, acc = 1, 0
    for c in reversed(v):
        acc += p * c
        p = p << 8
    result = b58encode_int(acc, default_one=False, alphabet=alphabet)
    return alphabet[0:1] * nPad + result

def b58decode_int(
    v: Union[str, bytes], alphabet: bytes = BITCOIN_ALPHABET
) -> int:
    v = v.rstrip()
    v = scrub_input(v)
    decimal = 0
    for char in v:
        decimal = decimal * 58 + alphabet.index(char)
    return decimal

def b58decode(
    v: Union[str, bytes], alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    v = v.rstrip()
    v = scrub_input(v)
    origlen = len(v)
    v = v.lstrip(alphabet[0:1])
    newlen = len(v)
    acc = b58decode_int(v, alphabet=alphabet)
    result = []
    while acc > 0:
        acc, mod = divmod(acc, 256)
        result.append(mod)
    return b'\0' * (origlen - newlen) + bytes(reversed(result))

def b58encode_check(
    v: Union[str, bytes], alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    v = scrub_input(v)
    digest = sha256(sha256(v).digest()).digest()
    return b58encode(v + digest[:4], alphabet=alphabet)

def b58decode_check(
    v: Union[str, bytes], alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    result = b58decode(v, alphabet=alphabet)
    result, check = result[:-4], result[-4:]
    digest = sha256(sha256(result).digest()).digest()
    if check != digest[:4]:
        raise ValueError("Invalid checksum")
    return result    

def int2bytes(i, enc):
    return i.to_bytes((i.bit_length() + 7) // 8, enc)

def convert_hex(str, enc1, enc2):
    return int2bytes(int.from_bytes(bytes.fromhex(str), enc1), enc2).hex()
        
#1 
prime = 957496696762772407663  

#2
second = b58decode_int('SatoshiNakamoto', alphabet=BITCOIN_ALPHABET) #124728751148945267645137860
hex2 = (str('%x'% second))  #672c5725fa8fc1aa52c3c4
little_big2 = convert_hex(hex2, 'big', 'little') #c4c352aac18ffa25572c67
second_sol = int(little_big2, 16) #237871847045914904726285415

#3
third = b58decode_int('Phemex', alphabet=RIPPLE_ALPHABET) #14899878097
hex3 = (str('%010x'% third))  #035f251581
little_big3 = convert_hex(hex3, 'big', 'little') #d1181a7803
third_sol = int(little_big3, 16) #554405551875

#END
big = prime * second_sol * third_sol #126272244427365764086102017718794198001099243823071433146875
hex = (str('%064x'% big)) #00000000000000141dc7bec50472bb381be8e18f6d6b397773d71fc5d91d41fb
uncompressed = bitcoin.privtoaddr(hex) #1LPmwxe59KD6oEJGYinx7Li1oCSRPCSNDY
WIFC = bitcoin.encode_privkey(hex,'wif_compressed') #KwDiBf89QgGfm2CrqioD77Q1g7urAhFcGUyUCQP3GdGAwCQRszmY
compressed = bitcoin.privtoaddr(WIFC) #1h8BNZkhsPiu6EKazP19WkGxDw3jHf9aT
print('COMPRESSED WIF:', WIFC)
print('UNCOMPRESSED ADDRESS:', uncompressed)
print('COMPRESSED ADDRESS:', compressed)