"""GCC v1 decimal kernel (mod 2310, pentagonal prism on primes 2,3,5,7,11).

SPEC:

- Input: stream di cifre decimali '0'..'9' (non ricostruiamo mai n intero).
- Stato interno: s = n mod 2310, con 2310 = 2 * 3 * 5 * 7 * 11.
- Update step: s_new = (10 * s_old + d) mod 2310.
- Firma prismatica: (r2, r3, r5, r7, r11) = (n mod p) via s.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Union

MOD_2310 = 2310
PRIMES_PENTAGON = (2, 3, 5, 7, 11)

Digit = Union[int, str]


def _digit_to_int(ch: Digit) -> int:
    """Convert a digit (char '0'..'9' or small int) to int in 0..9."""
    if isinstance(ch, int):
        if not (0 <= ch <= 9):
            raise ValueError(f"Digit int fuori range [0..9]: {ch}")
        return ch
    if isinstance(ch, str):
        if len(ch) != 1 or ch < "0" or ch > "9":
            raise ValueError(f"Digit str non valido: {ch!r}")
        return ord(ch) - ord("0")
    raise TypeError(f"Tipo digit non supportato: {type(ch)}")


def update_state_2310(digits: Iterable[Digit]) -> int:
    """Elabora uno stream di cifre decimali e restituisce s = n mod 2310."""
    s = 0
    for ch in digits:
        d = _digit_to_int(ch)
        s = (10 * s + d) % MOD_2310
    return s


@dataclass(frozen=True)
class PrismSignature2310:
    """Firma prismatica pentagonale per il kernel decimale."""

    s_mod: int  # n mod 2310
    residues: Dict[int, int]  # p -> (n mod p)
    vector: List[int]  # [r2, r3, r5, r7, r11]


def state_to_prism_signature_2310(s: int) -> PrismSignature2310:
    """Costruisce la firma prismatica (r2,r3,r5,r7,r11) a partire da s = n mod 2310."""
    if not (0 <= s < MOD_2310):
        raise ValueError(f"s deve essere in [0..{MOD_2310-1}], ricevuto {s}")

    residues: Dict[int, int] = {}
    vector: List[int] = []
    for p in PRIMES_PENTAGON:
        r = s % p
        residues[p] = r
        vector.append(r)

    return PrismSignature2310(s_mod=s, residues=residues, vector=vector)


def kernel_2310_from_digits(digits: Iterable[Digit]) -> PrismSignature2310:
    """Convenience: stream di cifre -> firma prismatica (s_mod + residui)."""
    s = update_state_2310(digits)
    return state_to_prism_signature_2310(s)
