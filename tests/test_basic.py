from __future__ import annotations

from gcc_v1 import decode_block, encode_block


def test_roundtrip_identity():
    data = b"\x10\x20\x30\x40"
    obj = encode_block(data, max_prime=31)
    restored = decode_block(obj)

    assert restored == data
    header = obj["header"]
    assert header["magic"] == "GCC1"
    assert header["block_len"] == len(data)


def test_cip_structure_present():
    data = b"ABCDEF"
    obj = encode_block(data)
    cip = obj["header"]["cip"]

    assert "H_total" in cip
    assert "primes" in cip
    assert "matrix_fingerprint" in cip
