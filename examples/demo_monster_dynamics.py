from __future__ import annotations

from gcc_v1 import encode_block
from gcc_v1.cluster import decode_cluster_code


def main() -> None:
    block = b"H-monster sugli indici"

    for dyn in ["H-identity", "H-band-quadratic", "H-monster-v1"]:
        obj = encode_block(
            block,
            max_prime=31,
            with_cluster=True,
            cluster_mode="canonical",
            cluster_dyn=dyn,
            cluster_params={"max_iter": 16},
        )

        cs = obj["header"]["cluster_signature"]
        print(f"\n=== {dyn} ===")
        print("bands:", cs["bands"])
        print("cluster_vector:", cs["cluster_vector"])
        print("code:", cs["code"])
        decoded = decode_cluster_code(cs["code"], cs["max_band_index"])
        print("roundtrip:", decoded)


if __name__ == "__main__":
    main()
