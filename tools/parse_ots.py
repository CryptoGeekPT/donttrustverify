#!/usr/bin/env python3
"""
Minimal OpenTimestamps .ots file parser.
Extracts: file hash, calendar URLs (pending), Bitcoin block attestations.

Based on the OTS binary format spec in github.com/opentimestamps/python-opentimestamps:
- Magic: b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"
- Version: varint
- File hash op: 1 byte (0x02=sha1, 0x03=ripemd160, 0x08=sha256, 0x67=keccak256)
- File hash digest: N bytes
- Then: timestamp tree

Op codes inside timestamp tree:
- 0x00 + attestation: terminal (8-byte tag + varint length + data)
  - Pending tag:  b"\x83\xdf\xe3\x0d\x2e\xf9\x0c\x8e"  (URI follows)
  - Bitcoin tag:  b"\x05\x88\x96\x0d\x73\xd7\x19\x01"  (block height varint)
- 0xff: fork (mark current state, then run sub-tree, then return to mark)
- 0xf0: append (varint length + bytes to append to current state)
- 0xf1: prepend
- 0x02: reverse
- 0x03: hexlify
- 0x08: sha256
- 0x67: ripemd160
"""

import struct
import sys

MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"

# Attestation tags
TAG_PENDING = b"\x83\xdf\xe3\x0d\x2e\xf9\x0c\x8e"
TAG_BITCOIN = b"\x05\x88\x96\x0d\x73\xd7\x19\x01"
TAG_LITECOIN = b"\x06\x86\x9a\x0d\x73\xd7\x1b\x45"
TAG_ETHEREUM = b"\x30\xfe\x80\x87\xb5\xc7\xea\xd7"

class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
    def read(self, n):
        b = self.data[self.pos:self.pos+n]
        self.pos += n
        return b
    def read_varuint(self):
        val = 0
        shift = 0
        while True:
            b = self.data[self.pos]
            self.pos += 1
            val |= (b & 0x7f) << shift
            if (b & 0x80) == 0:
                return val
            shift += 7
    def read_varbytes(self):
        n = self.read_varuint()
        return self.read(n)
    def peek(self, n=1):
        return self.data[self.pos:self.pos+n]
    def eof(self):
        return self.pos >= len(self.data)


def parse_attestation(r, current_hash, results):
    tag = r.read(8)
    body = r.read_varbytes()
    if tag == TAG_PENDING:
        sub = Reader(body)
        uri = sub.read_varbytes().decode('utf-8', errors='replace')
        results.append(("PENDING", uri, current_hash.hex()))
    elif tag == TAG_BITCOIN:
        sub = Reader(body)
        height = sub.read_varuint()
        results.append(("BITCOIN", height, current_hash.hex()))
    elif tag == TAG_LITECOIN:
        sub = Reader(body)
        height = sub.read_varuint()
        results.append(("LITECOIN", height, current_hash.hex()))
    elif tag == TAG_ETHEREUM:
        results.append(("ETHEREUM", body.hex(), current_hash.hex()))
    else:
        results.append(("UNKNOWN", tag.hex(), body.hex()))


def apply_op(r, current_hash):
    op = r.read(1)[0]
    if op == 0xf0:
        suffix = r.read_varbytes()
        return current_hash + suffix
    elif op == 0xf1:
        prefix = r.read_varbytes()
        return prefix + current_hash
    elif op == 0x02:
        return current_hash[::-1]
    elif op == 0x03:
        return current_hash.hex().encode('ascii')
    elif op == 0x08:
        import hashlib
        return hashlib.sha256(current_hash).digest()
    elif op == 0x67:
        import hashlib
        return hashlib.new('ripemd160', current_hash).digest()
    else:
        raise ValueError(f"Unknown op 0x{op:02x} at pos {r.pos-1}")


def parse_timestamp(r, current_hash, results):
    while True:
        op = r.peek(1)
        if not op:
            return
        op = op[0]
        if op == 0x00:
            r.read(1)
            parse_attestation(r, current_hash, results)
            return
        elif op == 0xff:
            r.read(1)
            parse_timestamp(r, current_hash, results)
        else:
            current_hash = apply_op(r, current_hash)


def parse_ots(path):
    with open(path, 'rb') as f:
        data = f.read()
    if not data.startswith(MAGIC):
        raise ValueError("Not an OTS file (bad magic)")
    r = Reader(data[len(MAGIC):])
    version = r.read_varuint()
    print(f"OTS version: {version}")
    op = r.read(1)[0]
    op_names = {0x02: 'sha1', 0x03: 'ripemd160', 0x08: 'sha256', 0x67: 'keccak256'}
    op_lengths = {0x02: 20, 0x03: 20, 0x08: 32, 0x67: 32}
    print(f"File hash op: 0x{op:02x} ({op_names.get(op, '?')})")
    digest = r.read(op_lengths[op])
    print(f"File hash: {digest.hex()}")
    print()
    print("=== Attestations / pending ===")
    results = []
    parse_timestamp(r, digest, results)
    for kind, info, h in results:
        if kind == "BITCOIN":
            print(f"  BITCOIN block {info}  (msg hash {h[:16]}...)")
        elif kind == "PENDING":
            print(f"  PENDING via {info}  (msg hash {h[:16]}...)")
        elif kind == "LITECOIN":
            print(f"  LITECOIN block {info}  (msg hash {h[:16]}...)")
        elif kind == "ETHEREUM":
            print(f"  ETHEREUM tx {info}  (msg hash {h[:16]}...)")
        else:
            print(f"  UNKNOWN tag={info}")
    return results


if __name__ == "__main__":
    parse_ots(sys.argv[1])
