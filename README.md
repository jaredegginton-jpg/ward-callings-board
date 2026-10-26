# Meridian 5th Ward Callings Board

Live board (password protected): https://jaredegginton-jpg.github.io/ward-callings-board/

`index.html` is rebuilt every Sunday from LCR (organization, calling, name and sustained date only).
The callings data inside it is encrypted (AES-256-GCM, key derived from the password with PBKDF2-SHA256, 600,000 rounds);
this repository holds no readable member data.

- `src/extract_lcr.js` – run on the LCR Organizations page to list callings (`Organization|Group|Calling|Last, First|Sustained`)
- `src/build.py` – `WARD_BOARD_PASSWORD='…' python3 src/build.py rows.txt index.html "2 Nov 2026"` (needs `pip install cryptography`)
- `src/decrypt.py` – `WARD_BOARD_PASSWORD='…' python3 src/decrypt.py index.html` prints last week's rows for comparison
- `src/template.html` – page layout and password screen
