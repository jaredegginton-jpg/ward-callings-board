"""Print the LCR rows stored (encrypted) inside a built board, one per line, for diffing.
Usage: WARD_BOARD_PASSWORD='...' python3 src/decrypt.py index.html > last_week.txt
"""
import json, os, re, sys, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

html = open(sys.argv[1] if len(sys.argv) > 1 else "index.html", encoding="utf-8").read()
enc = json.loads(re.search(r"const PAYLOAD = (\{.*?\});\n", html).group(1))["enc"]
d = lambda s: base64.b64decode(s)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(enc["salt"]), iterations=enc["iter"]).derive(
    os.environ["WARD_BOARD_PASSWORD"].encode())
data = json.loads(AESGCM(key).decrypt(d(enc["iv"]), d(enc["ct"]), None))
for r in data.get("raw", data["rows"]):
    print("|".join(r))
