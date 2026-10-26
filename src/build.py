"""Build the Ward Callings Board from LCR rows.

Input: callings.txt — one row per calling, pipe-separated:
  Organization|Group (sub-groups joined with ' › ')|Calling|Last, First|Sustained (e.g. 23 Feb 2025)
Vacant callings have empty name and date. Only names, callings and sustained dates are kept.

The data is encrypted (AES-256-GCM, key from PBKDF2-SHA256) with the password in the
WARD_BOARD_PASSWORD environment variable, so the published page shows nothing without it.
Usage: WARD_BOARD_PASSWORD='...' python3 src/build.py callings.txt index.html "2 Nov 2026"
Requires: pip install cryptography
"""
import json, sys, os, base64, datetime, pathlib

here = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here / "callings.txt"
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else here / "Ward Callings Board.html"
updated = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().strftime("%-d %b %Y")

raw_rows = []
for line in src.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    parts = line.split("|")
    assert len(parts) == 5, line
    raw_rows.append([p.strip() for p in parts])
rows = [list(r) for r in raw_rows]

# Vacant callings the bishopric doesn't want shown (org, group prefix, calling)
HIDE_IF_VACANT = [
    ("Aaronic Priesthood Quorums", "Priests Quorum", "Advisor"),
    ("Aaronic Priesthood Quorums", "Priests Quorum", "Assistant Secretary"),
]
rows = [r for r in rows if r[3] or not any(
    r[0] == o and r[1].startswith(g) and r[2] == c for o, g, c in HIDE_IF_VACANT)]

# Sections and callings the bishopric doesn't want on the board at all (filled or vacant)
HIDE_GROUPS = [
    ("Aaronic Priesthood Quorums", "Additional Aaronic Priesthood Quorums Callings"),
    ("Other Callings", "Church Magazines"),
    ("Other Callings", "Welfare and Self-Reliance"),
]
HIDE_CALLING_PREFIXES = ["Scheduler--"]
rows = [r for r in rows
        if (r[0], r[1]) not in HIDE_GROUPS
        and not any(r[2].startswith(p) for p in HIDE_CALLING_PREFIXES)]

# Tidy vacancies:
#  1. at most one vacant slot per calling within a group
#  2. no vacant teacher slot when that class already has 2+ teachers
filled = {}
for o, g, c, n, _ in rows:
    if n:
        filled[(o, g, c)] = filled.get((o, g, c), 0) + 1
kept, seen_vacant = [], set()
for r in rows:
    o, g, c, n, _ = r
    if not n:
        key = (o, g, c)
        if key in seen_vacant:
            continue
        if "teacher" in c.lower() and filled.get(key, 0) >= 2:
            continue
        seen_vacant.add(key)
    kept.append(r)
dropped = len(rows) - len(kept)
rows = kept

data = {"ward": "Meridian 5th Ward", "updated": updated, "rows": rows, "raw": raw_rows}

password = os.environ.get("WARD_BOARD_PASSWORD", "")
if not password:
    sys.exit("WARD_BOARD_PASSWORD is not set; refusing to build an unencrypted board.")
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ITER = 600_000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
ct = AESGCM(key).encrypt(iv, json.dumps(data, ensure_ascii=False).encode(), None)
b64 = lambda b: base64.b64encode(b).decode()
payload = {"enc": {"salt": b64(salt), "iv": b64(iv), "iter": ITER, "ct": b64(ct)}}

html = (here / "template.html").read_text(encoding="utf-8")
html = html.replace("__PAYLOAD__", json.dumps(payload))
out.write_text(html, encoding="utf-8")
print(f"{dropped} extra vacancies hidden; {len(rows)} rows, {sum(1 for r in rows if r[3])} filled -> {out}")
