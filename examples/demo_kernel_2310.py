from __future__ import annotations

from gcc_v1 import kernel_2310_from_digits


def main() -> None:
    digits = "12345678901234567890"

    sig = kernel_2310_from_digits(digits)

    print("Input decimale:", digits)
    print("s_mod (n mod 2310):", sig.s_mod)
    print("Residui (p -> n mod p):", sig.residues)
    print("Vettore firma_prisma:", sig.vector)


if __name__ == "__main__":
    main()
