"""
Modulo esterno per filtri spettrografici GCC v1.

Qui vivono:

- la dataclass Spectrum (risultato di un singolo passaggio di filtro);
- i filtri base (luce nera / luce bianca);
- la pipeline dinamica f(Spectrum) -> nuovo filtro.

Dipende solo da:

    from gcc_v1 import spectral_view
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from gcc_v1 import spectral_view


@dataclass
class Spectrum:
    """Risultato di un singolo passaggio spettrografico attraverso il prisma."""

    mode: str  # "black", "white" o nome custom
    filter_bits: Dict[int, int]  # F[p]: bit di ingresso per ogni primo
    out_bits: Dict[int, int]  # out[p]: bit in uscita per ogni primo
    active_primes: List[int]  # lista dei p con out[p] = 1
    active_count: int  # quanti p attivi
    inactive_count: int  # quanti p spenti
    bitvector: List[int]  # [out[p] in ordine primes]


# Firma dei filtri dinamici:
#   f(prev_spectrum, primes) -> dict p -> 0/1
FilterFn = Callable[[Optional[Spectrum], List[int]], Dict[int, int]]


def make_black_filter(primes: List[int]) -> Dict[int, int]:
    """F[p] = 0 per tutti i primi (luce nera)."""
    return {p: 0 for p in primes}


def make_white_filter(primes: List[int]) -> Dict[int, int]:
    """F[p] = 1 per tutti i primi (luce bianca)."""
    return {p: 1 for p in primes}


def _build_spectrum(
    mode: str, primes: List[int], logic_signature: Dict, filter_bits: Dict[int, int]
) -> Spectrum:
    """Wrapper che chiama spectral_view e incapsula il risultato in Spectrum."""
    out_bits, summary = spectral_view(
        primes, logic_signature, mode="custom", custom_bits=filter_bits
    )
    return Spectrum(
        mode=mode,
        filter_bits=filter_bits,
        out_bits=out_bits,
        active_primes=summary["active_primes"],
        active_count=summary["active_count"],
        inactive_count=summary["inactive_count"],
        bitvector=summary["bitvector"],
    )


def spectrum_black(cip: Dict) -> Spectrum:
    """Spettro con luce nera (F[p] = 0)."""
    primes = cip["primes"]
    logic_sig = cip["logic_signature"]
    F = make_black_filter(primes)
    return _build_spectrum("black", primes, logic_sig, F)


def spectrum_white(cip: Dict) -> Spectrum:
    """Spettro con luce bianca (F[p] = 1)."""
    primes = cip["primes"]
    logic_sig = cip["logic_signature"]
    F = make_white_filter(primes)
    return _build_spectrum("white", primes, logic_sig, F)


def spectrum_custom(cip: Dict, mode_name: str, filter_bits: Dict[int, int]) -> Spectrum:
    """Spettro per un filtro custom F[p] definito dall'utente."""
    primes = cip["primes"]
    logic_sig = cip["logic_signature"]
    F_norm = {p: int(filter_bits.get(p, 0)) & 1 for p in primes}
    return _build_spectrum(mode_name, primes, logic_sig, F_norm)


def run_filter_pipeline(cip: Dict, filter_fns: List[FilterFn]) -> List[Spectrum]:
    """Esegue una pipeline di filtri dipendenti dallo Spectrum precedente.

    Esempio:

        def f0(prev, primes):
            return make_black_filter(primes)

        def f1(prev, primes):
            # accendo i primi che erano spenti nello spettro precedente
            return {p: 1 - prev.out_bits[p] for p in primes}

        spectra = run_filter_pipeline(cip, [f0, f1])
    """
    primes = cip["primes"]
    logic_sig = cip["logic_signature"]

    spectra: List[Spectrum] = []
    prev: Optional[Spectrum] = None
    for idx, f in enumerate(filter_fns):
        F = f(prev, primes)
        mode_name = getattr(f, "__name__", f"step_{idx}")
        spec = _build_spectrum(mode_name, primes, logic_sig, F)
        spectra.append(spec)
        prev = spec

    return spectra
