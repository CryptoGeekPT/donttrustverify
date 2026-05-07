# donttrustverify

Source code for the [donttrustverify.pt/verify/](https://donttrustverify.pt/verify/) public integrity record of *A Simbiose IA-Blockchain* / *The AI-Blockchain Symbiosis* (Tiago Pinto, 2026).

The book argues that in the era of Synthetic Intelligence, authorship becomes a verifiable function. This repository, together with the live site, applies that thesis to the book itself: SHA-256 of the manuscript's base version, anchored to Bitcoin via OpenTimestamps, registered with Portuguese state authorities (IGAC).

The repository exists so anyone can audit the page itself — the HTML, the CSS, the OpenTimestamps proofs, the verification tooling — and confirm independently that the cryptographic anchors published on the live site are real.

---

## What's in here
```
site/                       Static files served at donttrustverify.pt
├── verify/
│   ├── pt/index.html       PT verification record
│   ├── en/index.html       EN verification record
│   └── index.html          Bilingual landing
└── static/
    ├── style.css           Shared CSS — zero JS, zero analytics, zero deps
    ├── hash/*.txt          SHA-256 hashes of the manuscript base versions
    └── ots/*.ots           OpenTimestamps proofs

tools/
└── parse_ots.py            Standalone OTS file parser — pure Python, no deps

docs/
└── nginx-snippet.conf      Reference Nginx config for serving the site
```
---

## Quick verification

The fastest way to confirm the cryptographic anchors are real:

### Option 1 — Web verifier (no installation)

Drop the `.ots` file into [dgi.io/ots/](https://dgi.io/ots/). The verifier returns the Bitcoin block height and timestamp directly. No PDF needed.

### Option 2 — Standalone Python parser (no third-party libraries)

The `tools/parse_ots.py` script in this repo parses the OTS binary format directly — no `opentimestamps-client` install, no network calls. Useful for offline verification or when you want to read exactly what's in the proof.

```bash
python3 tools/parse_ots.py site/static/ots/A_Simbiose_IA_Blockchain_PT_base_2026-04-30.pdf.ots
```

Expected output for the Phase 2 PT proof:

```
File hash: f8a54af6ac1a0f9bc27d2f6e550fdce75a0e20f0850253f9077e20b510c1e6e6

=== Attestations / pending ===
  PENDING via https://alice.btc.calendar.opentimestamps.org
  PENDING via https://bob.btc.calendar.opentimestamps.org
  BITCOIN block 948164
  PENDING via https://finney.calendar.eternitywall.com
  BITCOIN block 948254
```

The two Bitcoin block heights can then be checked on any block explorer:
- [mempool.space/block/948164](https://mempool.space/block/948164)
- [mempool.space/block/948254](https://mempool.space/block/948254)

### Option 3 — Standard OpenTimestamps client

```bash
pipx install opentimestamps-client
ots info site/static/ots/A_Simbiose_IA_Blockchain_PT_base_2026-04-30.pdf.ots
```

Expected output is functionally equivalent to Option 2, plus extra metadata.

---

## Phase 1 / Phase 2

The manuscript registration evolved in two phases:

| Phase | Date | IGAC reference | Manuscript SHA-256 | Bitcoin blocks |
|---|---|---|---|---|
| 1 (PT, EN) | 20 Apr 2026 | reg. 596/2026 (PT), 610/2026 (EN) | PT `5af95710…` / EN `4ec54921…` | 945970, 946046 |
| 2 (PT only) | 5 May 2026 | endorsement 32/2026 | PT `f8a54af6…` | 948164, 948254 |

Phase 2 corresponds to a content-amendment endorsement (Portuguese Decree-Law 143/2014) registering editorial corrections applied to the base manuscript. Phase 1 remains published as proof of anteriority — both phases are independently verifiable.

The site explains the rationale and verification paths in detail at [donttrustverify.pt/verify/](https://donttrustverify.pt/verify/).

---

## Why this is hosted in two places

- **The author's VPS** ([donttrustverify.pt](https://donttrustverify.pt)) — primary, served directly without CDN.
- **This GitHub repository** — public mirror of the artefacts, independent of the VPS, browsable in version control.

Hosting the `.ots` files in two independent locations adds redundancy. If the VPS goes down, the proofs remain auditable here. If GitHub goes down, the proofs remain auditable on the VPS. The Bitcoin blockchain itself is the real anchor — both copies just point to it.

---

## Reproducing the site locally

```bash
git clone https://github.com/CryptoGeekPT/donttrustverify
cd donttrustverify
python3 -m http.server 8080 --directory site
# Visit http://localhost:8080/verify/pt/
```

To deploy as a production replica, `docs/nginx-snippet.conf` shows the Nginx configuration used on the live site.

---

## License

- **Code** (HTML, CSS, Python tooling, Nginx config) — MIT, see `LICENSE`.
- **Cryptographic artefacts** (`.ots` files, `.txt` hashes) — CC0 / public domain, see `LICENSE-CONTENT`. They are mathematical facts, not copyrightable expression. Mirror them anywhere.

The book's manuscript itself is **not** in this repository. It is published commercially through Amazon KDP. The base PDF that produced these hashes is held by the author, by the IGAC archive, and (upon publication) by the National Library of Portugal as part of legal deposit.

---

## Contact

Tiago Pinto — [@CryptoGeekPT](https://x.com/cryptogeekpt) on X.

The book: *A Simbiose IA-Blockchain: Garantir a Verdade e a Autonomia na Era da Inteligência Sintética* (PT) / *The AI-Blockchain Symbiosis: Verification, Power, and Autonomy in the Age of Synthetic Intelligence* (EN). Available on Amazon.

---

*Don't trust. Verify.*
