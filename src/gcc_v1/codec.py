"""High-level GCC v1 codec.

This module ties everything together:

- builds the exponent matrix M from a block of bytes;
- computes CID_p and the global CIP;
- applies the logical core to get the logic_signature;
- packages everything in a GCC v1 logical structure:

    {
      "header": { ... },
      "invariants": { ... },
      "residual": { ... }
    }

For now the residual model is IDENTITY: residual_stream = original data.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from .exponents import build_exponent_matrix
from .logic import XorLogicOp, LogicOp, build_logic_signature
from .invariants import compute_cids, build_cip


def encode_block(
    block: bytes | Iterable[int],
    *,
    max_prime: int = 31,
    logic_op: Optional[LogicOp] = None,
) -> Dict:
    """Encode a block into the GCC v1 logical structure.

    Args:
        block: bytes or iterable of integers (0..255).
        max_prime: upper bound for small primes considered in the exponent matrix.
        logic_op: logical core operator (defaults to XOR-v1).

    Returns:
        A JSON-serializable dictionary with keys:
          - "header"
          - "invariants"
          - "residual"
    """
    # Normalize block to raw bytes and integer values
    if isinstance(block, (bytes, bytearray)):
        raw_bytes = bytes(block)
        values = list(raw_bytes)
    else:
        values = [int(x) & 0xFF for x in block]
        raw_bytes = bytes(values)

    if logic_op is None:
        logic_op = XorLogicOp()

    # Build exponent matrix M and prime list
    M, primes = build_exponent_matrix(values, primes=None, max_prime=max_prime)

    if not M or not primes:
        # Degenerate crystal: no exponents -> minimal structure
        logic_sig = {"logic_mode": logic_op.name, "per_prime": {}}
        cids: Dict[int, object] = {}
        cip = {
            "version": 1,
            "H_total": 0,
            "k": 0,
            "primes": [],
            "total_mass": 0,
            "col_mass": [],
            "row_mass": [],
            "per_prime": {},
            "logic_signature": logic_sig,
            "defects": {
                "model": "none",
                "params": {},
            },
            "matrix_fingerprint": "",
        }
    else:
        logic_sig = build_logic_signature(M, primes, logic_op)
        cids = compute_cids(M, primes)
        cip = build_cip(M, primes, cids, logic_sig)

    header = {
        "magic": "GCC1",
        "version": "0.1.0",
        "block_len": len(raw_bytes),
        "max_prime": max_prime,
        "primes": cip["primes"],
        "cip": cip,
    }

    invariants = {
        "cid_per_prime": {
            int(p): cid.__dict__ for p, cid in cids.items()
        }
    }

    # Residual model: identity.
    # Use a JSON-friendly representation (list of ints 0..255).
    residual = {
        "model_type": "identity",
        "model_params": {},
        "residual_stream": list(raw_bytes),
    }

    return {
        "header": header,
        "invariants": invariants,
        "residual": residual,
    }


def decode_block(gcc_obj: Dict) -> bytes:
    """Decode a GCC v1 structure back to the raw block.

    With the identity model this is trivial: we just reconstruct the bytes
    from residual_stream.
    """
    residual = gcc_obj.get("residual", {})
    model_type = residual.get("model_type")

    if model_type != "identity":
        raise NotImplementedError(
            f"Model type {model_type!r} not supported in this prototype."
        )

    data = residual.get("residual_stream", [])

    if isinstance(data, (bytes, bytearray)):
        return bytes(data)

    if isinstance(data, list):
        return bytes(int(x) & 0xFF for x in data)

    raise TypeError("Unsupported residual_stream type; expected list or bytes-like.")
