from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .cluster import compute_cluster_signature
from .exponents import build_exponent_matrix
from .invariants import build_cip, compute_cids
from .logic import LogicOp, XorLogicOp, build_logic_signature

# Codec di alto livello per GCC v1:
# - usa exponents / invariants / logic per costruire CIP e CID_p;
# - opzionalmente calcola la Cluster Signature;
# - mantiene un residuo "identity" per la decodifica byte-perfect.

__all__ = ["encode_block", "decode_block"]

__version__ = "0.1.0"


@dataclass
class GCCV1Block:
    """Wrapper dataclass per il blocco GCC v1."""

    header: dict[str, Any]
    invariants: dict[str, Any]
    residual: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "header": self.header,
            "invariants": self.invariants,
            "residual": self.residual,
        }


# ---------------------------------------------------------------------------
# API pubbliche
# ---------------------------------------------------------------------------


def encode_block(
    block: bytes,
    max_prime: int = 31,
    logic_op: LogicOp | None = None,
    *,
    with_cluster: bool = False,
    cluster_mode: str = "canonical",
    cluster_dyn: str = "H-identity",
    cluster_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Codifica un blocco di byte in un oggetto GCC_v1_Block."""
    if not isinstance(block, (bytes, bytearray)):
        raise TypeError("encode_block richiede un oggetto bytes-like")

    # 1. Prisma p-adico (M, primes) dalla logica esistente.
    M, primes = build_exponent_matrix(block, primes=None, max_prime=max_prime)

    # 2. Operatore logico e relativa firma.
    if logic_op is None:
        logic_op = XorLogicOp()
    logic_signature = build_logic_signature(M, primes, logic_op)

    # 3. Invarianti cristalline (CID_p, CIP).
    per_prime_cids = compute_cids(M, primes)
    cip = build_cip(M, primes, per_prime_cids, logic_signature)

    invariants: dict[str, Any] = {"cip": cip, "per_prime": per_prime_cids}

    # 4. Cluster Signature opzionale (layer separato).
    cluster_sig: dict[str, Any] | None = None
    if with_cluster:
        cluster_sig = compute_cluster_signature(
            cip, mode=cluster_mode, dyn_name=cluster_dyn, dyn_params=cluster_params
        )

    # 5. Header (compat con test_basic.py: magic="GCC1" e cip in header).
    header: dict[str, Any] = {
        "magic": "GCC1",
        "version": __version__,
        "block_len": len(block),
        "primes": primes,
        "cip": cip,
    }
    if cluster_sig is not None:
        header["cluster_signature"] = cluster_sig

    # 6. Residuo (modello identity).
    residual: dict[str, Any] = {
        "model_type": "identity",
        "model_params": {},
        "residual_stream": list(block),
    }

    gcc = GCCV1Block(header=header, invariants=invariants, residual=residual)
    return gcc.to_dict()


def decode_block(gcc_obj: Mapping[str, Any]) -> bytes:
    """Decodifica un oggetto GCC_v1_Block in un blocco di byte."""
    if not isinstance(gcc_obj, Mapping):
        raise TypeError("decode_block richiede un mapping (dict-like)")

    header = gcc_obj.get("header")
    residual = gcc_obj.get("residual")

    if not isinstance(header, Mapping) or not isinstance(residual, Mapping):
        msg = "oggetto GCC_v1_Block non valido (header/residual mancanti)"
        raise ValueError(msg)

    magic = header.get("magic")
    if magic not in ("GCC1", "GCCV1"):
        raise ValueError(f"magic non riconosciuto: {magic!r}")

    model_type = residual.get("model_type", "identity")
    if model_type != "identity":
        msg = "decode_block supporta solo model_type='identity'"
        raise NotImplementedError(f"{msg}, trovato {model_type!r}")

    stream = residual.get("residual_stream")
    if not isinstance(stream, (list, tuple)):
        raise ValueError("residual_stream mancante o non sequenza")

    try:
        data = bytes(int(b) & 0xFF for b in stream)
    except Exception as exc:  # noqa: BLE001
        msg = "residual_stream non convertibile in bytes"
        raise ValueError(msg) from exc

    expected_len = header.get("block_len")
    if isinstance(expected_len, int) and expected_len >= 0:
        if len(data) != expected_len:
            # Per ora solo warning silenzioso; in futuro si può rendere un errore.
            pass

    return data
