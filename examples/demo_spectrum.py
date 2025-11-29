from __future__ import annotations

import json

from gcc_v1 import encode_block, spectral_view


def main() -> None:
    block = b"Hello, GCC v1!"
    gcc_obj = encode_block(block, max_prime=31)

    cip = gcc_obj["header"]["cip"]
    primes = cip["primes"]
    logic_sig = cip["logic_signature"]

    # Spettro con luce nera
    out_black, spec_black = spectral_view(primes, logic_sig, mode="black")
    # Spettro con luce bianca
    out_white, spec_white = spectral_view(primes, logic_sig, mode="white")

    print("Primes:", primes)

    print("\n=== Spettro logico (luce nera) ===")
    print("out_bits:", out_black)
    print("summary:", json.dumps(spec_black, indent=2))

    print("\n=== Spettro logico (luce bianca) ===")
    print("out_bits:", out_white)
    print("summary:", json.dumps(spec_white, indent=2))


if __name__ == "__main__":
    main()
