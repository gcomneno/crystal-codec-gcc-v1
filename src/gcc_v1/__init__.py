"""GiadaWare Crystal Codec (GCC v1) - Python prototype."""

from .codec import decode_block, encode_block
from .kernel2310 import (
    MOD_2310,
    PRIMES_PENTAGON,
    kernel_2310_from_digits,
    state_to_prism_signature_2310,
    update_state_2310,
)
from .spectrum import apply_filter, build_filter_bits, spectral_view, summarize_spectrum

__all__ = [
    "encode_block",
    "decode_block",
    "MOD_2310",
    "PRIMES_PENTAGON",
    "update_state_2310",
    "state_to_prism_signature_2310",
    "kernel_2310_from_digits",
    "build_filter_bits",
    "apply_filter",
    "summarize_spectrum",
    "spectral_view",
]
