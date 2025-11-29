"""Spectral view helpers for GCC v1.

Qui vivono i filtri "luce nera", "luce bianca" e, in generale,
la lettura spettrografica numerica basata sulla logic_signature:

    T_p(0), T_p(1)  per ogni primo p
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

FilterMode = Literal["black", "white", "custom"]


def build_filter_bits(
    primes: List[int],
    mode: FilterMode = "white",
    custom_bits: Optional[Dict[int, int]] = None,
) -> Dict[int, int]:
    """Costruisce il vettore di ingresso F[p] per i vari filtri.

    mode="black"  -> F[p] = 0 per tutti i p
    mode="white"  -> F[p] = 1 per tutti i p
    mode="custom" -> usa custom_bits (serve p -> 0/1)
    """
    if mode == "black":
        return {p: 0 for p in primes}
    if mode == "white":
        return {p: 1 for p in primes}
    if mode == "custom":
        if custom_bits is None:
            raise ValueError("custom_bits deve essere fornito per mode='custom'")
        return {p: int(custom_bits.get(p, 0)) & 1 for p in primes}
    raise ValueError(f"Filtro sconosciuto: {mode!r}")


def apply_filter(
    primes: List[int],
    logic_signature: Dict,
    filter_bits: Dict[int, int],
) -> Dict[int, int]:
    """Applica un filtro F[p] usando la logic_signature (T_p(0), T_p(1))."""
    per_prime = logic_signature.get("per_prime", {})
    out: Dict[int, int] = {}
    for p in primes:
        Fp = int(filter_bits.get(p, 0)) & 1
        bits = per_prime.get(p)
        if bits is None:
            # Se manca l'entry, assumiamo identità (T0=0, T1=1)
            T0, T1 = 0, 1
        else:
            T0 = int(bits.get("T0", 0)) & 1
            T1 = int(bits.get("T1", 1)) & 1
        out[p] = T0 if Fp == 0 else T1
    return out


def summarize_spectrum(
    primes: List[int],
    out_bits: Dict[int, int],
) -> Dict[str, object]:
    """Costruisce una mini 'spettrografia numerica' dell'output."""
    bitvector: List[int] = [int(out_bits.get(p, 0)) & 1 for p in primes]
    active_primes = [p for p, b in zip(primes, bitvector) if b == 1]
    active_count = sum(bitvector)
    inactive_count = len(primes) - active_count

    return {
        "active_primes": active_primes,
        "active_count": active_count,
        "inactive_count": inactive_count,
        "bitvector": bitvector,
    }


def spectral_view(
    primes: List[int],
    logic_signature: Dict,
    mode: FilterMode = "white",
    custom_bits: Optional[Dict[int, int]] = None,
) -> Tuple[Dict[int, int], Dict[str, object]]:
    """Convenience: filtro -> out_bits + spettrografia numerica."""
    from_bits = build_filter_bits(primes, mode=mode, custom_bits=custom_bits)
    out_bits = apply_filter(primes, logic_signature, from_bits)
    spec = summarize_spectrum(primes, out_bits)
    return out_bits, spec
