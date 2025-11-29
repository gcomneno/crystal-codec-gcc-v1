from __future__ import annotations

import json

from gcc_v1 import encode_block, decode_block

def main() -> None:
    block = b"Hello, GCC v1!"
    gcc_obj = encode_block(block, max_prime=31)

    print("=== GCC v1 HEADER ===")
    print(json.dumps(gcc_obj["header"], indent=2))

    print("\n=== CIP (prism identity) ===")
    print(json.dumps(gcc_obj["header"]["cip"], indent=2))

    restored = decode_block(gcc_obj)
    print("\n=== ROUND TRIP ===")
    print("Restored:", restored)
    print("OK:", restored == block)

if __name__ == "__main__":
    main()
