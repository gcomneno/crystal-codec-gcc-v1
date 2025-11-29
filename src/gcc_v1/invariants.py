"""CID and CIP invariants for GCC v1.

This module computes:

- CID_p for each prime p:
    H_p, Mass_p, Supp_p, mu_p_q, sigma_p_q

- CIP for the whole prism:
    H_total, total_mass, col_mass, row_mass,
    per_prime (CID_p dump),
    logic_signature, defects (placeholder), matrix_fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import hashlib


@dataclass
class CID:
    """Crystalline Identity for a single prime p."""

    p: int
    H_p: int
    Mass_p: int
    Supp_p: int
    mu_p_q: int   # quantized center of mass (0..65535)
    sigma_p_q: int  # quantized spread (0..65535)


def _compute_cid_for_prime(
    M: List[List[int]],
    prime_index: int,
    p: int,
) -> CID:
    H_total = len(M)
    if H_total == 0:
        return CID(p=p, H_p=0, Mass_p=0, Supp_p=0, mu_p_q=0, sigma_p_q=0)

    col = [M[h][prime_index] for h in range(H_total)]

    # H_p: last non-zero row + 1
    H_p = 0
    for h in range(H_total - 1, -1, -1):
        if col[h] != 0:
            H_p = h + 1
            break

    if H_p == 0:
        return CID(p=p, H_p=0, Mass_p=0, Supp_p=0, mu_p_q=0, sigma_p_q=0)

    truncated = col[:H_p]
    Mass_p = sum(truncated)
    Supp_p = sum(1 for v in truncated if v != 0)

    if Mass_p > 0 and H_p > 1:
        # Center of mass along depth
        num = sum(h * truncated[h] for h in range(H_p))
        mu = num / Mass_p
        norm = H_p - 1
        mu_norm = max(0.0, min(1.0, mu / norm))
        mu_q = int(round(mu_norm * 65535))

        # Variance and spread
        var = sum((h - mu) ** 2 * truncated[h] for h in range(H_p)) / Mass_p
        sigma = var ** 0.5
        sigma_norm = max(0.0, min(1.0, sigma / norm))
        sigma_q = int(round(sigma_norm * 65535))
    else:
        mu_q = 0
        sigma_q = 0

    return CID(
        p=p,
        H_p=H_p,
        Mass_p=Mass_p,
        Supp_p=Supp_p,
        mu_p_q=mu_q,
        sigma_p_q=sigma_q,
    )


def compute_cids(M: List[List[int]], primes: List[int]) -> Dict[int, CID]:
    """Compute CID_p for all primes in column order."""
    return {
        p: _compute_cid_for_prime(M, j, p)
        for j, p in enumerate(primes)
    }


def _compute_matrix_fingerprint(
    M: List[List[int]],
    primes: List[int],
    logic_signature: Dict | None = None,
) -> str:
    """Compute SHA-256 fingerprint of the prism.

    Includes:
      - dimensions,
      - prime list,
      - raw exponent matrix M,
      - logic mode + per-prime unary tables (if provided).
    """
    h = hashlib.sha256()
    H_total = len(M)
    k = len(primes)

    h.update(H_total.to_bytes(4, "big"))
    h.update(k.to_bytes(4, "big"))

    for p in primes:
        h.update(int(p).to_bytes(4, "big", signed=False))

    for row in M:
        for value in row:
            h.update(int(value).to_bytes(4, "big", signed=False))

    if logic_signature is not None:
        mode = logic_signature.get("logic_mode", "")
        h.update(mode.encode("utf-8"))
        per_prime = logic_signature.get("per_prime", {})
        for p in primes:
            bits = per_prime.get(p)
            if bits is None:
                continue
            t0 = int(bits.get("T0", 0)) & 1
            t1 = int(bits.get("T1", 0)) & 1
            h.update(bytes([t0, t1]))

    return h.hexdigest()


def build_cip(
    M: List[List[int]],
    primes: List[int],
    cids: Dict[int, CID],
    logic_signature: Dict,
) -> Dict:
    """Build the CIP (prismatic identity) for the whole prism."""
    H_total_raw = len(M)
    if H_total_raw == 0:
        H_total = 0
    else:
        H_total = max((cid.H_p for cid in cids.values()), default=0)

    k = len(primes)

    # Per-prime summary and mass
    col_mass: List[int] = []
    per_prime_summary: Dict[int, Dict] = {}
    total_mass = 0

    for p in primes:
        cid = cids[p]
        col_mass.append(cid.Mass_p)
        total_mass += cid.Mass_p
        per_prime_summary[p] = asdict(cid)

    # Row mass profile (cut at effective H_total)
    row_mass: List[int] = []
    for h_idx in range(H_total):
        row = M[h_idx]
        row_mass.append(sum(int(v) for v in row))

    fingerprint = _compute_matrix_fingerprint(M, primes, logic_signature)

    defects = {
        "model": "none",
        "params": {},
    }

    return {
        "version": 1,
        "H_total": H_total,
        "k": k,
        "primes": primes,
        "total_mass": total_mass,
        "col_mass": col_mass,
        "row_mass": row_mass,
        "per_prime": per_prime_summary,
        "logic_signature": logic_signature,
        "defects": defects,
        "matrix_fingerprint": fingerprint,
    }
