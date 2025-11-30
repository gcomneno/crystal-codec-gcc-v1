from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Any, Mapping, Sequence

# Cluster Signature per GCC v1.
#
# Strato separato dalla Crystal Signature (CIP):
# - A0: insieme dei primi attivi derivato dal prisma GCC.
# - Bande B_k: gruppi di primi (canonici o by-basis).
# - Vettore di cluster CV_n = (S0, S1, ..., Sn).
# - Codec binario code_n per CV_n.
#
# La dinamica H(I_n) è inizialmente uno stub ("H-identity"), ma l'interfaccia
# è pensata per essere sostituita con la dinamica reale senza rompere il
# formato della Cluster Signature.


# ---------------------------------------------------------------------------
# Utilità base
# ---------------------------------------------------------------------------


def _primes_up_to(n: int) -> list[int]:
    """Restituisce tutti i primi <= n (sieve semplice)."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, isqrt(n) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = [False] * len(range(start, n + 1, step))
    return [i for i, is_prime in enumerate(sieve) if is_prime]


def _band_state_mask(active_primes: set[int], band: Sequence[int]) -> int:
    """Converte A_n ∩ B_k in una maschera di bit locale (0..2^len-1)."""
    mask = 0
    for idx, p in enumerate(band):
        if p in active_primes:
            mask |= 1 << idx
    return mask


# ---------------------------------------------------------------------------
# Codec binario per CV_n = (S0, ..., Sn)
# ---------------------------------------------------------------------------


def encode_cluster_vector(cluster_vector: Sequence[int]) -> int:
    """Codifica (S0, S1, ..., Sn) in un intero code_n.

    Convenzioni:
    - S0 occupa 1 bit (MSB),
    - ogni Sk (k >= 1) occupa 2 bit.
    Totale bit = 1 + 2n se la lunghezza è (n + 1).
    """
    if not cluster_vector:
        return 0

    n = len(cluster_vector) - 1
    s0 = cluster_vector[0] & 1
    code = s0 << (2 * n)

    for k in range(1, len(cluster_vector)):
        sk = cluster_vector[k] & 3
        shift = 2 * (n - k)
        code |= sk << shift

    return code


def decode_cluster_code(code: int, max_band_index: int) -> list[int]:
    """Decodifica code_n nel vettore (S0, ..., Sn) dato n = max_band_index."""
    if max_band_index < 0:
        return []

    n = max_band_index
    s0 = (code >> (2 * n)) & 1
    result = [s0]

    for k in range(1, n + 1):
        shift = 2 * (n - k)
        sk = (code >> shift) & 3
        result.append(sk)

    return result


# ---------------------------------------------------------------------------
# Costruzione di A0 dal CIP
# ---------------------------------------------------------------------------


def make_A0_from_cip(cip: Mapping[str, Any]) -> set[int]:
    """Deriva A0 (insieme dei primi attivi) dalla CIP.

    Allineato a build_cip(...) in invariants.py:

    - cip["primes"]: lista di primi in ordine di colonna.
    - cip["col_mass"]: lista di masse per colonna, stessa lunghezza di primes.

    Strategia:
    - se col_mass è una sequence della stessa lunghezza di primes,
      consideriamo attivo p se col_mass[j] > 0;
    - altrimenti, fallback: tutti i primi sono considerati attivi.
    """
    a0: set[int] = set()

    primes = list(cip.get("primes", []))
    col_mass = cip.get("col_mass")

    if isinstance(col_mass, (list, tuple)) and len(col_mass) == len(primes):
        for p, mass in zip(primes, col_mass, strict=False):
            try:
                prime = int(p)
            except (TypeError, ValueError):
                continue
            if mass:
                a0.add(prime)

    # Fallback: se non abbiamo ricavato nulla, consideriamo tutti i primi.
    if not a0:
        for p in primes:
            try:
                prime = int(p)
            except (TypeError, ValueError):
                continue
            a0.add(prime)

    return a0


# ---------------------------------------------------------------------------
# Costruzione bande
# ---------------------------------------------------------------------------


def build_bands(
    primes: Sequence[int], mode: str = "canonical", band_size: int = 3
) -> list[list[int]]:
    """Costruisce le bande B_k a partire dalla base di primi GCC.

    mode="canonical":
        - genera la lista dei primi standard fino a max(primes),
        - B0 = {2} se 2 è nella base,
        - le bande successive sono blocchi di band_size primi successivi,
          intersecati con la base.

    mode="by-basis":
        - ordina primes,
        - B0 = [primes_sorted[0]],
        - B1, B2, ... sono blocchi consecutivi di band_size elementi
          nella lista base stessa.
    """
    if not primes:
        return []

    basis = sorted({int(p) for p in primes})
    bands: list[list[int]] = []

    if mode == "by-basis":
        bands.append([basis[0]])
        rest = basis[1:]
        for i in range(0, len(rest), band_size):
            chunk = rest[i : i + band_size]
            if chunk:
                bands.append(chunk)
        return bands

    if mode != "canonical":
        msg = f"modalità banda non supportata: {mode!r}"
        raise ValueError(msg)

    max_p = basis[-1]
    all_primes = _primes_up_to(max_p)
    basis_set = set(basis)

    # B0: solo 2, se presente nella base.
    if 2 in basis_set:
        bands.append([2])
        start_index = 1
    else:
        start_index = 0

    # Bande successive: blocchi di band_size sulla sequenza canonica.
    for idx in range(start_index, len(all_primes), band_size):
        chunk = all_primes[idx : idx + band_size]
        band = [p for p in chunk if p in basis_set]
        if band:
            bands.append(band)

    return bands


# ---------------------------------------------------------------------------
# Dinamica H (stub) e classificazione delle bande
# ---------------------------------------------------------------------------


def _run_dynamics_stub(
    a0: set[int], *, dyn_name: str, dyn_params: Mapping[str, Any] | None, max_steps: int
) -> list[set[int]]:
    """Esegue la dinamica sugli insiemi A_n (stub).

    Per ora implementiamo solo:
        dyn_name = "H-identity" → A_n = A0 per tutti gli n.
    """
    if dyn_params is None:
        dyn_params = {}

    if dyn_name == "H-identity":
        return [set(a0) for _ in range(max_steps + 1)]

    msg = f"dinamica cluster non supportata: {dyn_name!r}"
    raise ValueError(msg)


def _classify_band_states_b0(masks: list[int]) -> int:
    """Classifica la banda 0 (solo primo 2).

    Stati possibili: {0, 1}

    - S0 = 0 → la dinamica visita almeno due stati distinti (0 e 1).
    - S0 = 1 → la dinamica resta bloccata su un solo stato.
    """
    distinct = set(masks)
    if len(distinct) >= 2:
        return 0
    return 1


def _classify_band_states(masks: list[int]) -> int:
    """Classifica la banda k >= 1 in S_k ∈ {0, 1, 2, 3}.

    Convenzione:

    - u = numero di stati distinti visitati:
      * u == 1 → punto fisso:
          - se #primi attivi == 2 → S_k = 2;
          - altrimenti (#attivi in {0,1,3}) → S_k = 3.
      * u == 2 → 2-cycle → S_k = 1.
      * u > 2 → orbita ricca → S_k = 0.
    """
    if not masks:
        # niente informazione → trattiamolo come fississimo/degenerato.
        return 3

    distinct = set(masks)
    u = len(distinct)

    if u == 1:
        m = next(iter(distinct))
        active = bin(m).count("1")
        if active == 2:
            return 2
        return 3

    if u == 2:
        return 1

    return 0


def _compute_cluster_vector_from_dynamics(
    a0: set[int],
    bands: Sequence[Sequence[int]],
    *,
    dyn_name: str,
    dyn_params: Mapping[str, Any] | None,
    max_steps: int,
) -> list[int]:
    """Calcola CV_n = (S0, ..., S_n) a partire da A0, bande e dinamica H."""
    a_sequence = _run_dynamics_stub(
        a0, dyn_name=dyn_name, dyn_params=dyn_params, max_steps=max_steps
    )
    cluster_vector: list[int] = []

    for k, band in enumerate(bands):
        if not band:
            # banda vuota: nessun primo in quella fascia → S_k = 3 (rigidissima).
            cluster_vector.append(3)
            continue

        masks = [_band_state_mask(a_n, band) for a_n in a_sequence]

        if k == 0:
            s_k = _classify_band_states_b0(masks)
        else:
            s_k = _classify_band_states(masks)

        cluster_vector.append(s_k)

    return cluster_vector


# ---------------------------------------------------------------------------
# Oggetto ClusterSignature + funzione principale
# ---------------------------------------------------------------------------


@dataclass
class ClusterSignature:
    """Rappresentazione ad alto livello della Cluster Signature."""

    version: str
    band_mode: str
    max_band_index: int
    bands: list[dict[str, Any]]
    cluster_vector: list[int]
    code: int
    params: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "band_mode": self.band_mode,
            "max_band_index": self.max_band_index,
            "bands": self.bands,
            "cluster_vector": list(self.cluster_vector),
            "code": int(self.code),
            "params": dict(self.params),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ClusterSignature:
        return cls(
            version=str(data.get("version", "cluster-v1")),
            band_mode=str(data.get("band_mode", "canonical")),
            max_band_index=int(data.get("max_band_index", -1)),
            bands=list(data.get("bands", [])),
            cluster_vector=list(data.get("cluster_vector", [])),
            code=int(data.get("code", 0)),
            params=dict(data.get("params", {})),
        )


def compute_cluster_signature(
    cip: Mapping[str, Any],
    *,
    mode: str = "canonical",
    max_band: int | None = None,
    dyn_name: str = "H-identity",
    dyn_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Costruisce il dict `cluster_signature` a partire da una CIP."""

    primes = cip.get("primes", [])
    primes_list = [int(p) for p in primes]

    if dyn_params is None:
        dyn_params = {}

    max_iter = int(dyn_params.get("max_iter", 32))

    bands_full = build_bands(primes_list, mode=mode)
    if max_band is not None:
        bands = bands_full[: max_band + 1]
    else:
        bands = bands_full

    a0 = make_A0_from_cip(cip)

    cluster_vector = _compute_cluster_vector_from_dynamics(
        a0, bands, dyn_name=dyn_name, dyn_params=dyn_params, max_steps=max_iter
    )

    code = encode_cluster_vector(cluster_vector)
    max_band_index = len(cluster_vector) - 1

    bands_meta = [{"k": k, "primes": list(band)} for k, band in enumerate(bands)]

    cs = ClusterSignature(
        version="cluster-v1",
        band_mode=mode,
        max_band_index=max_band_index,
        bands=bands_meta,
        cluster_vector=cluster_vector,
        code=code,
        params={"dyn": dyn_name, "max_iter": max_iter, "dyn_params": dict(dyn_params)},
    )
    return cs.to_dict()
