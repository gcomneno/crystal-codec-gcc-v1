from __future__ import annotations

from gcc_v1 import encode_block, kernel_2310_from_digits, state_to_prism_signature_2310
from gcc_v1.cluster import decode_cluster_code


def factorize(n: int) -> list[int]:
    """Fattorizzazione ingenua (trial division) per numeri medio-piccoli.

    Ritorna la lista dei fattori primi con molteplicità.
    Esempio: 600 = 2^3 * 3 * 5^2 → [2, 2, 2, 3, 5, 5]
    """
    if n <= 1:
        return []
    factors: list[int] = []
    d = 2
    m = n
    while d * d <= m:
        while m % d == 0:
            factors.append(d)
            m //= d
        d = d + 1 if d == 2 else d + 2  # dopo 2, prova solo dispari
    if m > 1:
        factors.append(m)
    return factors


def make_block_from_factors(factors: list[int]) -> bytes:
    """Costruisce un blocco di byte a partire dalla lista di fattori primi.

    Richiede che tutti i fattori siano nell'intervallo 1..255.
    """
    for p in factors:
        if p <= 0 or p > 255:
            msg = f"fattore fuori range byte: {p}"
            raise ValueError(msg)
    return bytes(factors)


def show_kernel_2310(n: int) -> None:
    """Mostra la firma modulo 2310 (prisma pentagonale dei primi 2,3,5,7,11).

    Gestisce entrambe le API possibili:
    - kernel_2310_from_digits → int (state),
    - kernel_2310_from_digits → firma già strutturata (dataclass/dict).
    """
    digits = list(str(n))
    sig_or_state = kernel_2310_from_digits(digits)

    print(">> Kernel 2310")

    # Caso 1: vecchia API → ritorna uno stato intero
    if isinstance(sig_or_state, int):
        s = sig_or_state
        sig = state_to_prism_signature_2310(s)
        print("  n mod 2310 =", s)
        print("  firma prisma pentagonale (mod 2,3,5,7,11):", sig)
        return

    # Caso 2: nuova API → ritorna direttamente una firma
    sig = sig_or_state

    # Proviamo a estrarre n mod 2310 se esiste come campo
    state_val = None
    for key in ("state", "n_mod_2310", "value"):
        if hasattr(sig, key):
            state_val = getattr(sig, key)
            break
        if isinstance(sig, dict) and key in sig:
            state_val = sig[key]
            break

    if state_val is not None:
        print("  n mod 2310 =", state_val)

    print("  firma prisma pentagonale:", sig)


def main() -> None:
    # Puoi cambiare qui il "mostro" da analizzare.
    N = 2**4 * 3**2 * 5 * 7**3 * 11

    print("=== NUMERO MONSTER ===")
    print("N =", N)

    factors = factorize(N)
    print("fattori primi (con molteplicità):", factors)

    block = make_block_from_factors(factors)
    print("blocchetto di byte per GCC v1:", list(block))

    # 1) Vista kernel 2310 (solo come assaggio "pentagonale")
    print()
    show_kernel_2310(N)

    # 2) Passaggio nel prisma cristallografico + cluster dynamics
    print("\n=== GCC v1 – CRYSTAL + CLUSTER (H-monster-v1) ===")

    obj = encode_block(
        block,
        max_prime=31,
        with_cluster=True,
        cluster_mode="canonical",
        cluster_dyn="H-monster-v1",
        cluster_params={"max_iter": 16},
    )

    header = obj["header"]
    invariants = obj["invariants"]

    print("\n>> Header GCC")
    print("  magic:", header["magic"])
    print("  length (bytes, derived):", len(block))
    print("  header keys:", sorted(header.keys()))

    # CIP = carta d'identità prismatica
    cip = invariants["cip"]
    print("\n>> CIP (Prismatic Identity)")
    print("  H_total:", cip["H_total"])
    print("  total_mass:", cip["total_mass"])
    print("  primes (base):", cip["primes"])
    print("  col_mass (per primo):", cip["col_mass"])
    print("  row_mass (per profondità):", cip["row_mass"])
    print("  logic_mode:", cip["logic_signature"]["logic_mode"])
    print("  matrix_fingerprint (SHA-256):", cip["matrix_fingerprint"])

    print("\n  Per-prime CIDs (p, H_p, Mass_p, Supp_p):")
    for p, cid in cip["per_prime"].items():
        print(
            f"    p={p}: "
            f"H_p={cid['H_p']}, "
            f"Mass_p={cid['Mass_p']}, "
            f"Supp_p={cid['Supp_p']}"
        )

    # Cluster Signature
    cs = header["cluster_signature"]
    print("\n>> Cluster Signature")
    print("  band_mode:", cs["band_mode"])
    print("  bands:", cs["bands"])
    print("  cluster_vector:", cs["cluster_vector"])
    print("  code:", cs["code"])
    print("  dyn:", cs["params"]["dyn"], "max_iter:", cs["params"]["max_iter"])

    decoded = decode_cluster_code(cs["code"], cs["max_band_index"])
    print("  roundtrip decode_cluster_code:", decoded)


if __name__ == "__main__":
    main()
