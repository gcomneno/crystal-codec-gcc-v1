# GiadaWare Crystal Codec (GCC v1)
GiadaWare Crystal Codec (GCC v1) – p-adic crystal/prism prototype

> **p-adic crystal/prism prototype** – un codec sperimentale che rappresenta i dati
> come un prisma di noduli (cristalli) p-adici, con invarianti cristallini e spettrografia logica.

---

## Cos'è il GCC v1

GCC v1 è un **prototipo di codec concettuale** scritto in Python che:

- prende un blocco di dati (byte);
- costruisce un **prisma di noduli p-adici** su una base di primi piccoli;
- calcola **invarianti cristallini** per ogni primo (CIDₚ);
- sintetizza una **Carta d’Identità Prismatica (CIP)** per l’intero prisma;
- definisce un **core logico** che fa passare fasci di “luce binaria”
  attraverso il reticolo, producendo una vista **spettrografica** per primo.

Non è (ancora) un codec di compressione “serio”: il modello di residuo è `identity`.
L’obiettivo è mostrare **architettura, modellazione matematica e struttura del codice**.

Per i dettagli matematici e formali: vedere [SPEC.md](SPEC.md).

---

## Installazione (sviluppo)

Richiede Python 3.10+.

```bash
git clone https://github.com/gcomneno/crystal-codec-gcc-v1.git
cd crystal-codec-gcc-v1

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e .[dev]
```

Esegui i test:

```bash
pytest -q
```

---

## Esempi veloci

### 1. Codifica e CIP

```bash
python examples/demo_encode.py
```

Mostra:

- l’`header` GCC v1 (magic, versione, lunghezza blocco, lista primi, CIP);
- la CIP completa (prisma, masse, logic_signature, fingerprint);
- verifica il round-trip `encode_block` → `decode_block`.

### 2. Kernel decimale mod 2310 (prisma pentagonale)

```bash
python examples/demo_kernel_2310.py
```

Calcola:

- `n mod 2310` per una stringa di cifre decimali;
- i residui `(n mod p)` per p = 2,3,5,7,11;
- il vettore firma pentagonale.

### 3. Spettrografia logica (luce nera / luce bianca)

```bash
python examples/demo_spectrum.py
```

Mostra, per ogni primo:

- la risposta logica con **luce nera** (input 0 su tutti i canali);
- la risposta logica con **luce bianca** (input 1 su tutti i canali);
- un piccolo riassunto numerico (quanti canali attivi/spenti).

---

## Architettura del codice

Struttura principale:

```text
src/gcc_v1/
  __init__.py        # API pubblica del pacchetto
  codec.py           # encode_block / decode_block (strato alto)
  exponents.py       # costruzione matrice degli esponenti M[h][j]
  logic.py           # LogicOp astratto + XorLogicOp + logic_signature
  invariants.py      # CIDₚ per primo + CIP globale + fingerprint
  kernel2310.py      # kernel decimale n mod 2310 (prisma pentagonale)
  spectrum.py        # filtri logici (luce nera/bianca/custom) + spettro numerico

examples/
  demo_encode.py       # esempio end-to-end
  demo_kernel_2310.py  # kernel 2310 + firma pentagonale
  demo_spectrum.py     # spettrografia logica (black/white)

tests/
  test_basic.py        # test di round-trip e CIP minima
```

---

## Spectral Lab (modulo esterno)

Nella cartella `lab/` è presente un piccolo **laboratorio spettrografico**:

- `lab/spectral_filters.py`:
  - definisce la dataclass `Spectrum` (risultato di un passaggio di filtro),
  - fornisce filtri base (`spectrum_black`, `spectrum_white`, `spectrum_custom`),
  - permette pipeline del tipo `f(Spectrum_prev) -> nuovo filtro`, senza toccare il core.

Esempio:

```bash
python examples/demo_spectral_pipeline.py
```

Mostra una pipeline minimale dove un filtro dipende dallo spettro precedente.

---

### Cluster Signature – modalità dinamiche (`dyn`)

La `cluster_signature` viene calcolata facendo evolvere gli insiemi di primi attivi
\(A_n\) sotto una dinamica discreta `H`.
La dinamica scelta è indicata in `cluster_signature["params"]["dyn"]`.

| `dyn`             | Dove agisce                      | Idea operativa                                       | Uso tipico                          |
|-------------------|----------------------------------|------------------------------------------------------|-------------------------------------|
| `H-identity`      | insiemi globali \(A_n\)          | nessuna evoluzione: \(A_n = A_0\) per tutti gli n    | baseline, debugging, confronti      |
| `H-band-quadratic`| maschere di banda \(s_k\)        | per banda: `s' = s XOR (s AND rotl(s, 1))`           | dinamica locale per banda, 2-cycle, orbite ricche |
| `H-monster-v1`    | indici globali della base primi  | \(y = x \oplus Q(x)\), con \(Q_i = ⊕_j (x_j ∧ x_{(i-j) mod K})\) | dinamica “densa” monster-like sugli indici |

In tutti i casi:

- la dinamica genera una traiettoria \(A_0, A_1, …, A_N\),
- ogni banda \(B_k\) vede solo la propria proiezione locale,
- da questa traiettoria locale si ricavano i valori \(S_k\) e quindi il
  `cluster_vector` e il relativo `code`.

#### Come scegliere `dyn`

A seconda di cosa vuoi osservare dal numero/blocco, puoi scegliere:

- `H-identity`
  Usa questa se ti interessa **solo la struttura cristallina statica**:
  stessa A₀ per tutto il cammino, la Cluster Signature fotografa “come sono fatti” i cluster, non “come si muovono”.

- `H-band-quadratic`
  Qui la dinamica è **locale per banda**: ogni banda evolve con
  `s' = s XOR (s AND rotl(s, 1))`.
  È una buona scelta se vuoi vedere **come reagiscono le bande** (2-cycle, punti fissi, orbite più ricche) mantenendo una geometria abbastanza leggibile.

- `H-monster-v1`
  Questa è la modalità **monster-like sugli indici globali**:
  lo stato viene visto come un vettore di bit su tutti i primi di base e aggiornato con una interazione quadratica densa.
  Usala quando vuoi una **firma dinamica forte e sensibile** alla struttura globale del numero/blocco, sapendo che è la più “turbolenta” delle tre.

#### Esempio: confronto fra le dinamiche

Dal repo:

```bash
python examples/demo_monster_dynamics.py
```

Output (semplificato):
```bash
=== H-identity ===
cluster_vector: [1, 3, 2, 3, 3]
code: 495

=== H-band-quadratic ===
cluster_vector: [1, 1, 1, 1, 3]
code: 343

=== H-monster-v1 ===
cluster_vector: [0, 0, 0, 0, 1]
code: 1
```

Stesso blocco, stessa base di primi, stesse bande.

Cambiando solo dyn cambiano:
    il vettore di cluster (S₀, S₁, …, Sₙ),
    il codice intero code.

Questo rende visibile a colpo d’occhio che:
    H-identity fotografa la struttura “statica” dei cluster,
    H-band-quadratic mette in gioco una dinamica locale per banda,
    H-monster-v1 applica una dinamica monster-like sugli indici globali del prisma.

---

## Stato del progetto

- **Versione:** 0.1.0 (prototype)
- **Modello di residuo:** `identity` (nessuna compressione, solo struttura cristallina)
- **LogicOp di default:** `xor-v1` (XOR iterata secondo la massa del nodulo)
- **Slot già pronti per il futuro:**
  - difetti cristallini (`defects` nella CIP),
  - operatori logici alternativi (`LogicOp` custom),
  - modelli di residuo non banali (solo scarto rispetto a un modello p-adico).

Per tutti i dettagli teorici e le formule: vedere [SPEC.md](SPEC.md).
