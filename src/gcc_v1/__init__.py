"""GiadaWare Crystal Codec (GCC v1) - Python prototype."""

from .codec import encode_block, decode_block
from .kernel2310 import (
    MOD_2310,
    PRIMES_PENTAGON,
    update_state_2310,
    state_to_prism_signature_2310,
    kernel_2310_from_digits,
)
from .spectrum import (
    build_filter_bits,
    apply_filter,
    summarize_spectrum,
    spectral_view,
)

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
