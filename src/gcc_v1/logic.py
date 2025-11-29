"""Logic core for GCC v1.

Defines:

- a pluggable logical operator interface `LogicOp`;
- a default XOR-based implementation `XorLogicOp`;
- computation of the logical signature per prime:

    T_p(0) = output bit with input 0
    T_p(1) = output bit with input 1

for the whole column corresponding to prime p.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol, runtime_checkable


@runtime_checkable
class LogicOp(Protocol):
    """Abstract logical operator applied to a nodulo (h, p)."""

    name: str

    def apply(self, bit_in: int, exponent: int, *, p: int, h: int) -> int:
        """Apply the logical operator to a single nodulo.

        bit_in   : input bit (0 or 1)
        exponent : nodulo exponent (non-negative integer)
        p        : prime for this column
        h        : depth level
        """
        ...


@dataclass(frozen=True)
class XorLogicOp:
    """XOR-based logical core.

    The exponent is interpreted as "number of flips".

    Applying XOR e times to the bit is equivalent to flipping it
    only if e is odd, leaving it unchanged if e is even.
    """

    name: str = "xor-v1"

    def apply(self, bit_in: int, exponent: int, *, p: int, h: int) -> int:
        if exponent & 1:
            return bit_in ^ 1
        return bit_in


def _apply_column(
    column: List[int],
    bit_in: int,
    *,
    p: int,
    op: LogicOp,
) -> int:
    """Propagate a bit through all noduli in a column for prime p."""
    s = bit_in
    for h, e in enumerate(column):
        if e:
            s = op.apply(s, e, p=p, h=h)
    return s


def build_logic_signature(
    M: List[List[int]],
    primes: List[int],
    op: LogicOp,
) -> Dict:
    """Compute the logical signature per prime.

    For each prime p:

        T0 = T_p(0)  # output with black light (0) at input
        T1 = T_p(1)  # output with white light (1) at input

    Results are cached in a dictionary:

        {
          "logic_mode": op.name,
          "per_prime": {
             p: {"T0": 0/1, "T1": 0/1},
             ...
          }
        }
    """
    H_total = len(M)
    logic_per_prime: Dict[int, Dict[str, int]] = {}

    for j, p in enumerate(primes):
        column = [M[h][j] for h in range(H_total)]
        T0 = _apply_column(column, 0, p=p, op=op)
        T1 = _apply_column(column, 1, p=p, op=op)
        logic_per_prime[p] = {"T0": int(T0), "T1": int(T1)}

    return {
        "logic_mode": op.name,
        "per_prime": logic_per_prime,
    }
