from __future__ import annotations

from gcc_v1 import encode_block
from gcc_v1.cluster import decode_cluster_code


def test_cluster_signature_presence_and_codecs_roundtrip():
    block = b"cluster + crystal"
    obj = encode_block(
        block,
        max_prime=31,
        with_cluster=True,
        cluster_mode="canonical",
        cluster_dyn="H-identity",
        cluster_params={"max_iter": 8},
    )

    header = obj["header"]
    assert "cluster_signature" in header, "cluster_signature mancante dall'header"

    cs = header["cluster_signature"]

    # Campi base devono esserci
    assert cs.get("version") == "cluster-v1"
    assert "band_mode" in cs
    assert "max_band_index" in cs
    assert "bands" in cs
    assert "cluster_vector" in cs
    assert "code" in cs
    assert "params" in cs

    cluster_vector = cs["cluster_vector"]
    max_band_index = cs["max_band_index"]
    code = cs["code"]

    # max_band_index deve essere coerente con la lunghezza del vettore
    assert max_band_index == len(cluster_vector) - 1

    # Round-trip codec binario: code -> cluster_vector
    decoded = decode_cluster_code(code, max_band_index)
    assert list(decoded) == list(cluster_vector)
