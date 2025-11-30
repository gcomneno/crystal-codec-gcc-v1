"""Exponent matrix builder for GCC v1.

This module defines a *toy* model that turns a block of integers into
an exponent matrix M[h][j], where:

- h = depth level (0 .. H-1)
- j = index of prime p_j in the primes list

For each prime p, we:
  1. compute the total p-adic exponent over the whole block;
  2. decompose that exponent over depth levels using powers of two, so that
     sum_h M[h][j] = total exponent for p.

The goal is not mathematical rigor (yet), but a clean, testable structure.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple


def sieve_primes(limit: int) -> List[int]:
    """Return list of primes <= limit using a simple sieve."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : limit + 1 : step] = [False] * (((limit - start) // step) + 1)
    return [i for i, is_p in enumerate(sieve) if is_p]


def v_p(n: int, p: int) -> int:
    """p-adic valuation v_p(n) for n != 0, returning 0 for n == 0."""
    if n == 0:
        return 0
    n = abs(n)
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def infer_primes_from_block(block: Iterable[int], max_prime: int = 31) -> List[int]:
    """Infer the list of primes to use.

    For the prototype we simply take all primes <= max_prime.
    """
    return sieve_primes(max_prime)


def build_exponent_matrix(
    block: Iterable[int], primes: List[int] | None = None, max_prime: int = 31
) -> Tuple[List[List[int]], List[int]]:
    """Build a toy exponent matrix M[h][j] from a block of integers.

    Strategy (toy, but deterministic):

    1. Normalize the block to a list of integers (0..255).
    2. Choose a set of primes (by default all primes <= max_prime).
    3. For each prime p_j:
         E_p = sum over n of v_p(block[n])
    4. Let E_max = max_j E_p. If E_max == 0, the matrix is empty.
    5. Depth H = bit_length(E_max).
    6. For each depth level h:
         M[h][j] = (bit_h of E_p) * 2^h
       so that sum_h M[h][j] = E_p for each j.

    Returns:
        M: list of H rows, each a list of len(primes) integers.
        primes: the list of primes in column order.
    """
    values = [int(x) for x in block]
    if primes is None:
        primes = infer_primes_from_block(values, max_prime=max_prime)

    totals: List[int] = []
    for p in primes:
        e_total = 0
        for n in values:
            if n == 0:
                continue
            e_total += v_p(n, p)
        totals.append(e_total)

    if not totals:
        return [], primes

    max_e = max(totals)
    if max_e == 0:
        # no p-adic content at all
        return [], primes

    H = max_e.bit_length()
    M: List[List[int]] = []

    for h in range(H):
        row: List[int] = []
        weight = 1 << h
        for e_total in totals:
            bit = (e_total >> h) & 1
            row.append(bit * weight)
        M.append(row)

    return M, primes


def build_exponent_prism(block: bytes, primes: list[int]) -> list[list[int]]:
    """Compat wrapper per codec.py: delega alla funzione exponents esistente."""
    return build_exponent_matrix(block, primes)
