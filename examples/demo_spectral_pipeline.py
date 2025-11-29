from __future__ import annotations

import os
import sys

# Assicuriamoci che la root del progetto sia nel sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gcc_v1 import encode_block  # noqa: E402
from lab.spectral_filters import (  # noqa: E402
    Spectrum,
    make_black_filter,
    run_filter_pipeline,
    spectrum_black,
    spectrum_white,
)


def invert_prev(prev: Spectrum | None, primes):
    """f(Spectrum): accende i primi che erano spenti, spegne quelli accesi."""
    if prev is None:
        return make_black_filter(primes)
    return {p: 1 - prev.out_bits[p] for p in primes}


def main() -> None:
    block = b"Hello, GCC v1!"
    gcc_obj = encode_block(block, max_prime=31)
    cip = gcc_obj["header"]["cip"]

    spec_b = spectrum_black(cip)
    spec_w = spectrum_white(cip)

    print("BLACK active:", spec_b.active_primes)
    print("WHITE active:", spec_w.active_primes)

    spectra = run_filter_pipeline(cip, [invert_prev, invert_prev])
    for s in spectra:
        print(f"{s.mode}: active={s.active_primes}")


if __name__ == "__main__":
    main()
