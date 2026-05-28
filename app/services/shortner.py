import hashlib
import string

from pydantic import HttpUrl

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def base62_encode(num : int):
    if num == 0: 
        return BASE62_ALPHABET[0]
    
    base62 = []
    while num > 0:
        num , rem = divmod(num , 62)
        base62.append(BASE62_ALPHABET[rem])

    return ''.join(reversed(base62))



def generate_hash(url:HttpUrl , length : int = 6):
    sha_256_hash = hashlib.sha256(str(url).encode("utf-8")).digest()
    hash_int = int.from_bytes(sha_256_hash, byteorder="big")
    base62_encoded = base62_encode(hash_int)

    return base62_encoded[:length]

