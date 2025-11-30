---
# GCC v1 – GiadaWare Crystal Codec
# **Versione:** 0.1.0 (prototype)
# **Autore:** Giancarlo Cicellyn Comneno
---

## 0. Scopo di questo documento
Questo SPEC descrive la versione prototipale del **GiadaWare Crystal Codec (GCC v1)**, un codec sperimentale che rappresenta i dati come un **prisma di noduli (cristalli) p-adici**.

Obiettivi:
- Definire in modo **chiaro e formale**:
  - cos’è il **lattice** e cos’è la **basis** nel GCC;
  - i **due sistemi di coordinate** (spazio dati vs spazio cristallino);
  - la struttura del **prisma**, delle **CIDs** (Carte d’Identità Cristalline) e della **CIP** (Carta d’Identità Prismatica);
  - il **core logico** (operatori su “fasci di luce”);
  - il kernel **decimale 2310** (prisma pentagonale sui primi 2,3,5,7,11).
- Fissare la struttura logica dell’oggetto `GCC_v1_Block` usato da `encode_block` e `decode_block`.

Non-obiettivi (per ora):
- Non è ancora un codec di compressione “serio”: il modello di residuo è `identity`.
- Non cerca performance, ma **chiarezza concettuale**.
- Non fissa in pietra il modo “definitivo” di costruire la matrice degli esponenti: è un modello giocattolo.

---

## 1. Terminologia base

- **Blocco dati**: sequenza finita di byte (0..255) o cifre decimali (0..9).
- **Primo** \\(p\\): elemento dell’insieme di primi considerati (es. tutti i primi ≤ `max_prime`, oppure [2,3,5,7,11]).
- **Valutazione p-adica** \\(v_p(n)\\): massimo intero \\(e \ge 0\\) tale che \\(p^e\\) divide \\(n\\). Se \\(n = 0\\), convenzionalmente \\(v_p(0)=0\\).
- **Nodulo p-adico**: una cella del reticolo con esponente > 0. È il “cristallo elementare”.
- **Prisma**: il reticolo (2D o 3D) di tutti i noduli per i primi considerati.
- **CIDₚ**: *Carta d’Identità Cristallina* per il primo p (invarianti monoprimo).
- **CIP**: *Carta d’Identità Prismatica* del prisma intero (invarianti globali).
- **LogicOp**: operatore logico astratto che dice come un nodulo modifica un bit di luce.
- **Tₚ**: funzione unaria \\(\{0,1\} → \{0,1\}\\) associata alla colonna del primo p (risposta del prisma su quel canale).

---

## 2. Lattice + Basis nel GCC

### 2.1 Lattice teorico completo

Concettualmente, il prisma vive su un lattice discreto 3D:
- asse **h**: profondità / livello (0,1,2,…)
- asse **n**: posizione nel blocco (0..N−1)
- asse **j**: indice del primo \\(p_j\\) (1..k)

Lattice teorico infinito:

\\[
\mathcal{L}_\infty = \{ (h,n,j) \mid h,n \in \mathbb{Z},\ 1 \le j \le k \}
\\]

Su questo lattice definiremmo un campo di esponenti:

\\[
E(h,n,j) \in \mathbb{N},\quad \text{esponente dei noduli p-adici}
\\]

- **Nodulo** = tripla \\((h,n,j)\\) con \\(E(h,n,j) > 0\\).

Nella pratica lavoriamo su una **finestra finita**:

\\[
\mathcal{W} = \{0,\dots,H-1\} \times \{0,\dots,N-1\} \times \{1,\dots,k\}
\\]

---

### 2.2 Lattice effettivo GCC v1 (aggregato in n)

Per semplificare il prototipo, si *collassa* la dimensione n:

\\[
M[h,j] = \sum_{n=0}^{N-1} E(h,n,j)
\\]

Quindi il lattice effettivo GCC v1 è 2D:

\\[
\mathcal{L}_{\text{v1}} = \{ (h,j) \mid 0 \le h < H,\ 1 \le j \le k \}
\\]

dove:

- \\(H\\) = profondità del prisma (numero di livelli),
- \\(k\\) = numero di primi considerati.

La matrice:

\\[
M \in \mathbb{N}^{H \times k},\quad M[h,j] \ge 0
\\]

è il nostro **prisma aggregato**.

---

### 2.3 Basis nel GCC

Nella cristallografia classica:

> Crystal = Lattice + Basis.

Nel GCC:

- **Lattice** = la griglia \\(\mathcal{L}_{\text{v1}}\\) (h × j).
- **Basis** = pattern di noduli all’interno della **unit cell** osservata.

Per GCC v1, l’intera finestra osservata viene trattata come **una unit cell**:

\\[
\mathcal{U}_{\text{v1}} = \mathcal{L}_{\text{v1}} = \{(h,j)\}
\\]

La basis è:

\\[
B(h,j) = M[h,j]
\\]

- Per ogni primo p_j, la colonna:
  \\[
  B_p(h) = M[h,j]
  \\]
  è la “basis monoprimo”.

Le **CIDₚ** sono una **descrizione compatta** della basis lungo l’asse h per ciascun primo p.
La **CIP** è una descrizione compatta della basis dell’intero prisma.

---

## 3. Sistemi di coordinate

Distinguiamo due “spazi”:

- **DF** (Data Frame): spazio del dato grezzo.
- **CF** (Crystal Frame): spazio cristallino del prisma.

### 3.1 Spazio dati (DF)

#### 3.1.1 Kernel byte-oriented (prototipo M)

- Input: sequenza di byte/integri:

  \\[
  b_0, b_1, \dots, b_{L-1},\quad b_i \in \{0,\dots,255\}
  \\]

- coordinate DF: \\(n \in \{0,\dots,L-1\}\\).

#### 3.1.2 Kernel decimale mod 2310 (prisma pentagonale)

- Input: cifre decimali:

  \\[
  d_0, d_1, \dots, d_{K-1},\quad d_i \in \{0,\dots,9\}
  \\]

- Stato interno:

  \\[
  s_t = n_t \bmod 2310
  \\]

  aggiornato iterativamente:

  \\[
  s_{t+1} = (10 s_t + d_{t+1}) \bmod 2310,\quad s_0 = 0
  \\]

- DF = indici delle cifre + valore corrente di s.

---

### 3.2 Spazio cristallino (CF)

#### 3.2.1 CF del prisma aggregato (M)

- CF = coppie \\((h,j)\\) con:
  - \\(0 \le h < H\\),
  - \\(1 \le j \le k\\).

- Valore in CF: \\(M[h,j]\\).

#### 3.2.2 CF del kernel 2310

Alla fine della lettura:

- stato `s_mod = n mod 2310`.
- residui:

  \\[
  r_2 = s \bmod 2,\ r_3 = s \bmod 3,\ r_5 = s \bmod 5,\ r_7 = s \bmod 7,\ r_{11} = s \bmod 11
  \\]

- vettore firma:

  \\[
  \text{firma\_prisma} = (r_2, r_3, r_5, r_7, r_{11})
  \\]

Questa è una coordinata CF compatta nel **prisma pentagonale** sui primi (2,3,5,7,11).

---

### 3.3 Trasformazione DF → CF (overview)

#### 3.3.1 Byte → Prisma M

1. Da DF (byte) a valutazioni p-adiche:

   \\[
   e_{n,p} = v_p(b_n)
   \\]

2. Aggregazione per p (modello toy):

   \\[
   E_p = \sum_n e_{n,p}
   \\]

3. Decomposizione di \\(E_p\\) sui livelli h (toy: decomposizione binaria):

   - sia `E_max = max_p E_p`;
   - profondità:
     \\[
     H = \text{bit\_length}(E_{\max})
     \\]
   - per ciascun \\(p_j\\) e livello h:

     \\[
     M[h,j] =
       \begin{cases}
       2^h, & \text{se il bit }h\text{ di }E_p\text{ è 1} \\
       0,   & \text{altrimenti}
       \end{cases}
     \\]

   In questo modo:

   \\[
   E_p = \sum_{h=0}^{H-1} M[h,j]
   \\]

4. Risultato: DF → CF (M[h,j]).

#### 3.3.2 Cifre → Firma 2310

1. DF (cifre) → `s_mod` via kernel 2310.
2. `s_mod` → (r2,r3,r5,r7,r11).
3. La firma può essere memorizzata nel header come **invariante addizionale** o usata in future versioni per generare un prisma coerente.

---

## 4. CIDₚ – Carta d’Identità Cristallina (per primo p)

Dato il prisma M:

- numero di livelli effettivi = `H_total = len(M)`
- `primes = [p_1, ..., p_k]`
- colonna per p_j:

  \\[
  c_p(h) = M[h,j],\quad h = 0,\dots,H_{\text{total}}-1
  \\]

### 4.1 Invarianti obbligatori (v1)

1. **Hₚ (altezza effettiva)**

   Ultimo livello dove p compare:

   \\[
   H_p =
   \begin{cases}
   \max\{ h : c_p(h) \neq 0 \} + 1, & \text{se colonna non nulla} \\
   0, & \text{se colonna nulla}
   \end{cases}
   \\]

2. **Massₚ (massa totale)**

   \\[
   \text{Mass}_p = \sum_{h=0}^{H_p-1} c_p(h)
   \\]

3. **Suppₚ (supporto non nullo)**

   \\[
   \text{Supp}_p = |\{ h \mid 0 \le h < H_p,\ c_p(h) \neq 0 \}|
   \\]

### 4.2 Invarianti di forma (v1)

Se `Mass_p > 0` e `H_p > 1`:

1. **Centro di massa lungo h: μₚ**

   \\[
   \mu_p = \frac{1}{\text{Mass}_p} \sum_{h=0}^{H_p-1} h \cdot c_p(h)
   \\]

   Normalizzazione (in [0,1]):

   \\[
   \mu_{p,\text{norm}} = \frac{\mu_p}{H_p - 1}
   \\]

   Quantizzazione su 16 bit:

   \\[
   \mu_{p,q} = \text{round}(\mu_{p,\text{norm}} \cdot 65535)
   \\]

2. **Spread (deviazione standard) lungo h: σₚ**

   \\[
   \sigma_p^2 = \frac{1}{\text{Mass}_p} \sum_{h=0}^{H_p-1} (h - \mu_p)^2 c_p(h)
   \\]
   \\[
   \sigma_p = \sqrt{\sigma_p^2}
   \\]
   Normalizzazione:

   \\[
   \sigma_{p,\text{norm}} = \frac{\sigma_p}{H_p - 1}
   \\]
   \\[
   \sigma_{p,q} = \text{round}(\sigma_{p,\text{norm}} \cdot 65535)
   \\]

Se `Mass_p == 0` o `H_p <= 1`, poniamo `mu_p_q = 0`, `sigma_p_q = 0`.

### 4.3 Struttura logica del CIDₚ

```json
CID_p = {
  "p":        int,
  "H_p":      int,
  "Mass_p":   int,
  "Supp_p":   int,
  "mu_p_q":   int,
  "sigma_p_q": int
}
```

---

## 5. Core logico (LogicOp) e Tₚ

### 5.1 LogicOp astratto

Un **LogicOp** è una funzione che, dato:

- `bit_in` ∈ {0,1}
- `exponent` = M[h,j] (esponente del nodulo)
- contesto: `p` (primo), `h` (livello)

restituisce:

- `bit_out` ∈ {0,1}

Firma astratta:

```python
bit_out = LOGIC_OP(bit_in, exponent, p=p, h=h)
```

Nel prototipo: interfaccia `LogicOp` (Protocol) + implementazione `XorLogicOp`.

---

### 5.2 Tₚ: funzione di trasferimento di colonna

Per un primo p e la relativa colonna `col = [M[h,j] for h in range(H_total)]`, definiamo:

```python
def apply_column(col, bit_in, p, op):
    s = bit_in
    for h, e in enumerate(col):
        if e != 0:
            s = op.apply(s, e, p=p, h=h)
    return s
```

Allora:

- `T_p(0) = apply_column(col, 0, p, op)`
- `T_p(1) = apply_column(col, 1, p, op)`

Tₚ è una funzione unaria `{0,1} → {0,1}` che rappresenta l’effetto della colonna p su un fascio di luce (bit) che la attraversa.

---

### 5.3 Logic signature

La **logic signature** è il riassunto per-primo di queste funzioni:

```json
logic_signature = {
  "logic_mode": "xor-v1",
  "per_prime": {
    "p": {
      "T0": 0 or 1,
      "T1": 0 or 1
    },
    ...
  }
}
```

Note:

- `logic_mode` documenta **come** sono stati calcolati Tₚ (es. XOR vs altro).
- In futuro altri LogicOp (es. NOT.XOR, ecc.) potranno cambiare Tₚ senza cambiare la struttura della CIP.

---

### 5.4 Filtri (luce nera, luce bianca, multi-filtro)

Un **filtro** è un vettore di bit:

\\[
F[p] \in \{0,1\} \quad \text{per ogni primo } p
\\]

Dato F e la logic_signature, l’uscita logica per ogni p è:

```python
out[p] = T_p(0) if F[p] == 0 else T_p(1)
```

Casi notevoli:

- **Luce nera**: `F_black[p] = 0` per tutti i p → `out_black[p] = T_p(0)`.
- **Luce bianca**: `F_white[p] = 1` per tutti i p → `out_white[p] = T_p(1)`.

La struttura della CIP è **indipendente** dal tipo di filtro; i filtri si applicano in post-process usando soltanto Tₚ.

---

## 6. CIP – Carta d’Identità Prismatica

La CIP riassume l’intero prisma M + logica associata (LogicOp).

Dati:

- M[h][j], `H_total_raw = len(M)`
- `primes = [p_1, ..., p_k]`
- CIDs per ogni p
- logic_signature

### 6.1 Parametri globali

1. **H_total**

   Altezza effettiva del prisma:

   \\[
   H_{\text{total}} = \max_p H_p
   \\]

   (se nessun CID, `H_total = 0`).

2. **k**

   Numero di primi: `k = len(primes)`.

3. **Masse**

   - `col_mass[j] = CID_p.Mass_p` per p in `primes`.
   - `total_mass = sum(col_mass)`.

4. **Row mass**

   Per livello h:

   \\[
   \text{row\_mass}[h] = \sum_j M[h,j]
   \\]

   Considerati solo i primi `H_total` livelli (taglio delle righe vuote in fondo).

---

### 6.2 Per-prime (dump dei CIDₚ)

```json
"per_prime": {
  "p": {
    "p":        int,
    "H_p":      int,
    "Mass_p":   int,
    "Supp_p":   int,
    "mu_p_q":   int,
    "sigma_p_q": int
  },
  ...
}
```

Questo è un mirror diretto dei CIDₚ.

---

### 6.3 Logic signature

Inclusa direttamente:

```json
"logic_signature": {
  "logic_mode": "xor-v1",
  "per_prime": {
    "p": {"T0": 0 or 1, "T1": 0 or 1},
    ...
  }
}
```

---

### 6.4 Defects (slot concettuale)

Per GCC v1:

```json
"defects": {
  "model": "none",
  "params": {}
}
```

In GCC v2+ si potranno introdurre:

- `model: "site" | "line" | "plane" | "custom-xxx"`
- `params`: parametri del difetto (quale p, quali livelli, quale delta, ecc.).

---

### 6.5 Matrix fingerprint

`matrix_fingerprint` è una firma SHA-256 del prisma (M, primes, logic_signature).

Serializzazione concettuale:

1. Scrivi dimensioni H_total_raw e k.
2. Scrivi la lista dei primi.
3. Scrivi tutti gli M[h][j] come interi (es. 4 byte big-endian).
4. Scrivi `logic_mode`.
5. Scrivi Tₚ(0), Tₚ(1) per ogni p in ordine `primes`.

Poi:

```text
matrix_fingerprint = SHA256(serialize(...)).hexdigest()
```

---

### 6.6 Struttura logica completa della CIP

```json
CIP = {
  "version": 1,
  "H_total": int,
  "k": int,
  "primes": [int, ...],
  "total_mass": int,
  "col_mass": [int, ...],
  "row_mass": [int, ...],
  "per_prime": { "p": CID_p, ... },
  "logic_signature": {
    "logic_mode": "xor-v1",
    "per_prime": {
      "p": {"T0": 0 or 1, "T1": 0 or 1}
    }
  },
  "defects": {
    "model": "none",
    "params": {}
  },
  "matrix_fingerprint": "hex-string"
}
```

---

## 5. Cluster Signature Layer (CSL)

### 5.1. Posizionamento nell’architettura GCC v1

Il GCC v1 ha ora tre strati logici:

1. **Prisma p-adico degli esponenti**
   - matrice M[h][j] + lista di primi `primes[j]`.

2. **Invarianti cristallini (CID / CIP)**
   - per-prime CID_p, più la CIP globale con fingerprint del prisma.

3. **Cluster Signature Layer (CSL)** – *nuovo strato dinamico*
   - costruito **a partire dalla CIP**, senza guardare il valore del numero N;
   - descrive il comportamento “per bande di primi” sotto una dinamica discreta H;
   - compresso in un vettore di cluster `CV = (S₀, S₁, …, Sₙ)` e in un intero `code`.

La Cluster Signature è un **metadato additivo**, indipendente dalla decodifica:

- vive nell’`header.cluster_signature`,
- la Crystal Signature (CIP) resta in `invariants.cip` e in `header.cip`.


### 5.2. Input dal CIP

Si assume una CIP del tipo (vedi sezione precedente):

```json
"cip": {
  "version": 1,
  "H_total": ...,
  "k": ...,
  "primes": [p0, p1, ..., p_{k-1}],
  "total_mass": ...,
  "col_mass": [m0, m1, ..., m_{k-1}],
  "row_mass": [...],
  "per_prime": {...},
  "logic_signature": {...},
  "defects": {...},
  "matrix_fingerprint": "..."
}
```

Usiamo in particolare:
    primes: lista di primi in ordine di colonna;
    col_mass: massa cristallina per colonna.

### 5.3. Insieme iniziale A₀

Definiamo l’insieme iniziale di primi “attivi”:
    se col_mass è una lista con stessa lunghezza di primes:
    A0={ pj∣col_mass[j]>0 }
    A0​={pj​∣col_mass[j]>0}

    altrimenti (fallback):
    A0={ pj∣pj∈primes }
    A0​={pj​∣pj​∈primes}

In pseudo-codice:
```python
def make_A0_from_cip(cip) -> set[int]:
    primes = list(cip.get("primes", []))
    col_mass = cip.get("col_mass")
    a0 = set()

    if isinstance(col_mass, (list, tuple)) and len(col_mass) == len(primes):
        for p, mass in zip(primes, col_mass):
            if mass:
                a0.add(int(p))

    if not a0:
        for p in primes:
            a0.add(int(p))

    return a0
```

### 5.4. Bande di primi Bₖ
Dal set primes definiamo una famiglia ordinata di bande B_k (k = 0,…,n).

#### 5.4.1. Mode "canonical"

    basis = sorted(set(primes))
    all_primes = tutti i primi ≤ max(basis)

    Se 2 ∈ basis:
        B₀ = {2}
        le bande successive sono blocchi di band_size (default 3) nella lista all_primes, intersecati con basis.

    Se 2 ∉ basis:
        non c’è banda 0 speciale,
        tutte le bande sono blocchi sulla lista canonica, intersecati con basis.

Esempio (base GCC = {2,3,5,7,11,13,17,19,23}):

    B₀ = {2}
    B₁ = {3,5,7}
    B₂ = {11,13,17}
    B₃ = {19,23}

#### 5.4.2. Mode "by-basis"
    basis = sorted(set(primes))
    B₀ = {basis[0]}
    rest = basis[1:]
    B₁, B₂, … = blocchi consecutivi di band_size elementi presi da rest.

Esempio (base GCC = {3,5,7,11,13,17}):

    B₀ = {3}
    B₁ = {5,7,11}
    B₂ = {13,17}

### 5.5. Dinamica discreta sugli insiemi Aₙ
Definiamo una dinamica:
An+1=H(An;dyn_params)
An+1​=H(An​;dyn_params)

dove:
    H è una mappa sugli insiemi di primi,
    dyn_name seleziona la versione di H,
    dyn_params contiene i parametri (es. {"max_iter": 32}).

#### 5.5.1. Implementazione v0: H-identity

Per dyn_name = "H-identity":
An=A0∀n∈[0,max_iter]
An​=A0​∀n∈[0,max_iter]

cioè la dinamica è piatta, ma l’interfaccia è già pronta per sostituire H con la dinamica reale (es. I ⊕ (I ⊗ I) sugli indici di banda).

In codice:
```python
def _run_dynamics_stub(a0: set[int], dyn_name: str, dyn_params: dict, max_steps: int):
    if dyn_name == "H-identity":
        return [set(a0) for _ in range(max_steps + 1)]
    raise ValueError(f"dinamica cluster non supportata: {dyn_name}")
```

#### 5.5.2. Dinamica `H-band-quadratic` (monster-like per banda)

Oltre alla dinamica piatta `H-identity`, il layer cluster supporta una dinamica
“quadratica” locale definita **per banda**:

- la dinamica agisce sulle **maschere di banda** `s_k(n)` invece che direttamente
  su Aₙ;
- per ogni banda `B_k` (con `m_k` primi) consideriamo:

  - `s_k(n) ∈ {0, …, 2^{m_k} - 1}` maschera dei primi attivi della banda al passo n,
  - i singoli bit indicano la presenza/assenza del corrispondente primo in `A_n`.

La dinamica `H-band-quadratic` è definita da:

\[
s_{k, n+1}
= s_{k, n} \oplus \Bigl(s_{k, n} \;\&\; \operatorname{rotl}\bigl(s_{k, n}, 1\bigr)\Bigr)
\]

dove:

- `⊕` è XOR bit-a-bit,
- `&` è AND bit-a-bit,
- `rotl(s, 1)` è la rotazione a sinistra di 1 bit **all’interno della banda**
  (con wrapping modulo `m_k`).

Interpretazione:

- \( s_{k,n} \) descrive quali noduli della banda sono attivi;
- \( s_{k,n} \& \operatorname{rotl}(s_{k,n}, 1) \) è un termine “quadratico”:
  interazione tra bit adiacenti della stessa banda;
- il passo successivo è dato da:

  \[
  s_{k,n+1} = s_{k,n} \oplus (s_{k,n} \otimes s_{k,n})
  \]

  con \( s_{k,n} \otimes s_{k,n} := s_{k,n} \& \operatorname{rotl}(s_{k,n}, 1) \),

  che è l’analogo combinatorio della dinamica
  \( I_{n+1} = I_n \oplus (I_n \otimes I_n) \) sul pattern di attivazione locale.

#### 5.5.3. Dinamica `H-monster-v1` sugli indici globali

Oltre alle dinamiche locali per banda, il layer cluster supporta una dinamica
“pura” sugli **indici globali** della base dei primi, pensata come modello
semplificato di:

\[
I_{n+1} = I_n \oplus (I_n \otimes I_n)
\]

dove gli insiemi \(I_n\) sono rappresentati come vettori di bit sugli indici dei
primi.

##### Rappresentazione di stato

Sia:

- `basis_list = sorted(B)` l’insieme di tutti i primi presenti nelle bande,
- `K = len(basis_list)` la dimensione della base.

Ogni stato Aₙ (insieme di primi attivi) viene rappresentato come:

- vettore binario \( x \in \{0,1\}^K \),

con:

- \( x_i = 1 \) se `basis_list[i] ∈ A_n`,
- \( x_i = 0 \) altrimenti.

##### Definizione di `H-monster-v1`

Per ogni indice \( i \in \{0, \dotsc, K-1\} \) definiamo:

1. termine “quadratico”:

   \[
   q_i = \bigoplus_{j=0}^{K-1} \bigl( x_j \land x_{(i-j) \bmod K} \bigr)
   \]

   dove:

   - `⊕` è XOR (somma mod 2),
   - `∧` è AND logico,
   - l’indice \( (i - j) \bmod K \) è preso modulo K (con wrapping).

2. aggiornamento del bit:

   \[
   y_i = x_i \oplus q_i.
   \]

La dinamica completa è quindi:

- \( x^{(n+1)} = H_{\text{monster}}(x^{(n)}) \) con la regola precedente,
- Aₙ viene ricostruito come:

  \[
  A_n = \{\, \text{basis\_list}[i] \mid x_i^{(n)} = 1 \,\}.
  \]

La scelta di usare tutti i primi presenti nelle bande garantisce che la dinamica
sia definita su uno stato globale coerente con la struttura del prisma GCC.

##### Sequenza e classificazione

Dato A₀ (costruito dal CIP) e i parametri della dinamica:

- `dyn = "H-monster-v1"`,
- `max_iter = N`,

viene generata la sequenza:

\[
A_0, A_1, \dotsc, A_N
\]

dove ogni passo è:

- conversione Aₙ → vettore x,
- applicazione di `H-monster-v1` sugli indici,
- ricostruzione \( A_{n+1} \) dai bit attivi.

A partire da questa sequenza:

- per ogni banda \(B_k\) si calcolano le maschere locali
  \( \pi_k(A_n) \) come in 5.4,
- si ottiene una sequenza di maschere `mask_k(n)`,
- si applicano le stesse regole di classificazione viste in 5.5.1–5.5.2:

  - `S0 ∈ {0,1}` per la banda 0 (presenza del 2),
  - `S_k ∈ {0,1,2,3}` per k ≥ 1 in base a:
    - numero di stati distinti visitati dalla banda,
    - cardinalità degli stati fissi (0, 1, 2 o 3 primi attivi).

Si ottiene così un vettore di cluster:

\[
\mathrm{CV}_N = (S_0, S_1, \dotsc, S_N)
\]

che viene compresso nel codice intero `code_N` tramite il codec binario descritto
nella sezione 5.3.

##### Parametri e riproducibilità

L’oggetto `cluster_signature` risultante include:

```json
"cluster_signature": {
  "version": "cluster-v1",
  "band_mode": "...",
  "max_band_index": ...,
  "bands": [...],
  "cluster_vector": [...],
  "code": ...,
  "params": {
    "dyn": "H-monster-v1",
    "max_iter": N,
    "dyn_params": { ... }
  }
}
```

A parità di:

blocco di input,
CIP sottostante,
schema di bande (band_mode),
dinamica (dyn = "H-monster-v1"),
orizzonte temporale (max_iter),

la cluster_signature è riproducibile e funge da invariante strutturale
specifica per il modello “monster” sugli indici globali.

##### Dettagli di implementazione

Per ogni banda `B_k`:

- se `len(B_k) <= 0`:
  - la maschera è sempre 0;
- se `len(B_k) == 1`:
  - la rotazione è identica, quindi:

    \[
    s' = s \oplus (s \& s) = s \oplus s = 0
    \]

  - la banda collassa sempre verso uno stato fisso banale;
- se `len(B_k) >= 2`:
  - sia `width = len(B_k)`,
  - `full = (1 << width) - 1` maschera di tutti 1,
  - la dinamica si implementa come:

    ```python
    full = (1 << width) - 1
    rot = ((s << 1) | (s >> (width - 1))) & full
    quad = s & rot
    s_next = (s ^ quad) & full
    ```

La sequenza completa delle maschere:

\[
\{ s_k(n) \mid n = 0, \dotsc, \text{max\_iter} \}
\]

viene poi tradotta in:

- una sequenza di insiemi Aₙ (ricostruiti a partire dalle maschere),
- una sequenza di maschere di banda `mask_k(n)` per ciascuna banda `B_k`.

Su queste maschere si applicano le regole di classificazione per ottenere:

- `S₀` tramite `_classify_band_states_b0`,
- `S_k (k ≥ 1)` tramite `_classify_band_states`.

Il resto del processo (costruzione di `cluster_vector`, compressione in `code`,
struttura JSON `cluster_signature`) è identico al caso `H-identity`.

##### Uso da API

La dinamica si seleziona tramite il parametro:

```python
obj = encode_block(
    block,
    max_prime=31,
    with_cluster=True,
    cluster_mode="canonical",
    cluster_dyn="H-band-quadratic",
    cluster_params={"max_iter": 32},
)
```

Nel JSON risultante:
```json
"cluster_signature": {
  "version": "cluster-v1",
  "band_mode": "canonical",
  "max_band_index": ...,
  "bands": [...],
  "cluster_vector": [...],
  "code": ...,
  "params": {
    "dyn": "H-band-quadratic",
    "max_iter": 32,
    "dyn_params": {}
  }
}
```

La cluster_signature ottenuta in questo modo è un’invariante strutturale
dipendente da:

    CIP di partenza,
    schema di bande,
    scelta di dinamica (dyn="H-band-quadratic"),
    orizzonte temporale (max_iter).

A parità di questi elementi, la firma è riproducibile per lo stesso blocco.

### 5.6. Proiezione locale su ciascuna banda

Per ogni banda B_k e ad ogni passo n:

    proiettiamo:
    πk(n)=An∩Bk
    πk​(n)=An​∩Bk​

    la traduciamo in una maschera di bit locale mask_k(n):

        len(B_k) = m,
        mask_k(n) ∈ {0, …, 2^m - 1},
        il bit i-esimo indica se il i-esimo primo della banda è presente in A_n.

La dinamica globale A_n genera quindi, per ogni banda B_k, una sequenza finita di maschere:
{ maskk(n)∣n=0,…,max_iter }
{maskk​(n)∣n=0,…,max_iter}

### 5.7. Classificazione locale: S₀, S₁, …, Sₙ

Dalla sequenza di maschere per la banda B_k:

    distinct = set(mask_k(n))
    u = len(distinct) = numero di stati distinti visitati dalla banda.

#### 5.7.1. Banda 0 (prime {2})

Per k = 0 (banda monosimbolo 2, se presente):

    stati possibili: {0,1};

    regola:
        S₀ = 0 → la dinamica visita almeno due stati distinti (0 e 1);
        S₀ = 1 → la banda resta bloccata su un solo stato (0 fisso o 1 fisso).

#### 5.7.2. Bande successive (k ≥ 1)

Per k ≥ 1:
    u = #stati distinti,
    m* = maschera singola nel caso u = 1,
    active = popcount(m*) = numero di primi attivi nella banda.

Regole:

    se u == 1 (punto fisso):
        se active == 2 → Sₖ = 2
        (banda congelata con 2 primi attivi);

        altrimenti (active in {0,1} oppure >2) → Sₖ = 3
        (banda rigidissima / degenerata).

    se u == 2 → Sₖ = 1
    (oscillazione fra due soli stati, 2-cycle).

    se u > 2 → Sₖ = 0
    (orbita più “ricca”, esplora 3+ stati).

#### 5.7.3. Vettore di cluster

Il vettore di cluster è:
CV=(S0,S1,…,Sn)
CV=(S0​,S1​,…,Sn​)

dove n = numero_di_bande − 1 (dopo eventuale taglio a max_band).

Nel JSON:
    cluster_vector = lista [S0, S1, ..., Sn],
    max_band_index = n.

### 5.8. Codec binario per il vettore CV
Il vettore CV = (S₀, …, Sₙ) viene compresso in un intero senza segno code_n.

#### 5.8.1. Convenzione di codifica

Data una lunghezza n+1:
    S₀ usa 1 bit (bit di peso massimo, posizione 2n),
    ogni Sₖ per k ≥ 1 usa 2 bit.

Schema:
    S0 → (S0 & 1) << (2n)

    per k ∈ {1,…,n}:
        S_k → (S_k & 3) << (2*(n-k))

Formula compatta:
coden=(S0&1)≪(2n)  ∣  ∑k=1n((Sk&3)≪2(n−k))
coden​=(S0​&1)≪(2n)
​k=1∑n​((Sk​&3)≪2(n−k))

In codice:
```python
def encode_cluster_vector(cluster_vector: Sequence[int]) -> int:
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
```

### 5.8.2. Decodifica

Data code_n e max_band_index = n:

    S₀:
    S0=(coden≫2n)&1
    S0​=(coden​≫2n)&1

    per k = 1,…,n:
    Sk=(coden≫2(n−k))&3
    Sk​=(coden​≫2(n−k))&3

In codice:
```python
def decode_cluster_code(code: int, max_band_index: int) -> list[int]:
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
```

### 5.9. Schema JSON della cluster_signature

Nel blocco GCC v1, se lo strato cluster è attivo:
```json
"header": {
  "magic": "GCC1",
  "version": "0.1.0",
  "block_len": 123,
  "primes": [2,3,5,7,11,13,17,19,23],
  "cip": { ... },
  "cluster_signature": {
    "version": "cluster-v1",
    "band_mode": "canonical",
    "max_band_index": 3,
    "bands": [
      { "k": 0, "primes": [2] },
      { "k": 1, "primes": [3,5,7] },
      { "k": 2, "primes": [11,13,17] },
      { "k": 3, "primes": [19,23] }
    ],
    "cluster_vector": [1, 0, 2, 3],
    "code": 42,
    "params": {
      "dyn": "H-identity",
      "max_iter": 32,
      "dyn_params": {}
    }
  }
}
```

    La CIP resta la “Carta d’Identità Cristallina” del prisma.
    La Cluster Signature è una firma dinamico-combinatoria per bande:
        cluster_vector = (S₀, …, Sₙ),
        code = compressione binaria del vettore,
        bands documenta quali primi vivono in ogni banda,
        params descrive la dinamica usata.

Questo strato è matematicamente indipendente dal valore numerico N:
dipende solo dalla struttura cristallina (CIP) che il GCC v1 ha estratto dal blocco.

### 5.10. Esempio numerico semplificato (illustrativo)

Consideriamo un blocco di due byte:

- `block = [4, 9]`  (ad es. b"\x04\x09")
- base di primi (toy): `primes = [2, 3, 5, 7]`

Supponiamo che il prisma p-adico e la CIP risultino in:

- `cip["primes"]   = [2, 3, 5, 7]`
- `cip["col_mass"] = [4, 2, 0, 1]`

Quindi:

- colonna p=2 ha massa 4,
- colonna p=3 ha massa 2,
- colonna p=5 ha massa 0,
- colonna p=7 ha massa 1.

#### 5.10.1. Insieme iniziale A₀

Per definizione:

\[
A_0 = \{ p_j \mid \text{col\_mass}[j] > 0 \}
     = \{ 2, 3, 7 \}
\]

p=5 è escluso perché la sua massa è 0.

#### 5.10.2. Bande canoniche

Con `primes = [2,3,5,7]` e `mode = "canonical"` (`band_size = 3`), le bande sono:

- B₀ = {2}
- B₁ = {3, 5, 7}

(quindi n = 1, due bande totali: k=0 e k=1).

#### 5.10.3. Dinamica H-identity

Prendiamo:

- `dyn_name = "H-identity"`
- `max_iter = 3`

Allora:

\[
A_n = A_0 = \{2,3,7\} \quad \text{per } n = 0,1,2,3.
\]

Nessuna evoluzione: è una dinamica piatta ma già instradata nella pipeline.

#### 5.10.4. Proiezioni locali e maschere

Per ogni banda k e passo n, calcoliamo:

\[
\pi_k(n) = A_n \cap B_k
\]

e la maschera binaria locale \(\text{mask}_k(n)\).

- **Banda 0**: B₀ = {2}

  - Aₙ ∩ B₀ = {2} per ogni n,
  - maschera locale (1 bit): `mask₀(n) = 1` per tutti gli n.

  Quindi:

  \[
  \{\text{mask}_0(n)\} = \{1\}, \quad u_0 = 1
  \]

- **Banda 1**: B₁ = {3,5,7}

  Ordiniamo la banda come [3,5,7].
  Per ogni Aₙ:

  - 3 ∈ Aₙ, 5 ∉ Aₙ, 7 ∈ Aₙ → pattern [1,0,1]
  - maschera a 3 bit: `mask₁(n) = b101₂ = 5`

  Quindi:

  \[
  \{\text{mask}_1(n)\} = \{5\}, \quad u_1 = 1
  \]

#### 5.10.5. Classificazione: S₀, S₁

- **Per la banda 0** (monosimbolo 2):

  - gli stati distinti sono {1} (solo uno) → banda bloccata su un solo stato,
  - per definizione:

    - S₀ = 1 → punto fisso (la banda non cambia mai).

- **Per la banda 1**:

  - `u₁ = 1` (punto fisso),
  - `mask = 5 = b101₂` ha due bit a 1 → esattamente 2 primi attivi nella banda,
  - per la regola locale:

    - S₁ = 2 → punto fisso con **2 primi attivi**.

In conclusione, il vettore di cluster è:

\[
\text{CV} = (S_0, S_1) = (1, 2)
\]

#### 5.10.6. Codec binario per CV = (1, 2)

La lunghezza è 2, quindi:

- n = max_band_index = 1,
- S₀ usa 1 bit, S₁ usa 2 bit.

Calcolo:

- parte alta (S₀):

  \[
  S_0 = 1 \Rightarrow (S_0 \& 1) \ll (2n) = 1 \ll 2 = 4
  \]

- parte bassa (S₁, k=1):

  - shift = 2·(n − k) = 2·(1−1) = 0,
  - contributo = (S₁ & 3) << 0 = 2 << 0 = 2.

- combinando:

  \[
  \text{code}_1 = 4 \;|\; 2 = 6
  \]

Quindi, in JSON:

```json
"cluster_signature": {
  "version": "cluster-v1",
  "band_mode": "canonical",
  "max_band_index": 1,
  "bands": [
    { "k": 0, "primes": [2] },
    { "k": 1, "primes": [3, 5, 7] }
  ],
  "cluster_vector": [1, 2],
  "code": 6,
  "params": {
    "dyn": "H-identity",
    "max_iter": 3,
    "dyn_params": {}
  }
}
```

La Cluster Signature non influisce sulla decodifica del blocco (che è ancora identity), ma aggiunge una firma dinamico-combinatoria per bande di primi che può essere usata per:

- classificazione rapida di blocchi “mostro”,
- filtri cristallografici / spettrografici,
- ulteriori livelli di analisi p-adica.

---

## 7. Kernel decimale mod 2310 (prisma pentagonale)

Modulo: `gcc_v1.kernel2310`

### 7.1 Stato interno

- Modulo fisso:
  \\[
  \text{MOD} = 2310 = 2 \cdot 3 \cdot 5 \cdot 7 \cdot 11
  \\]
- Stato: `s ∈ {0,1,…,2309}`, con stato iniziale `s = 0`.

### 7.2 Update step

Dato uno stream di cifre `digits` (int 0..9 o char '0'..'9'):

```python
s = 0
for d in digits:
    s = (10 * s + d) % 2310
```

Alla fine, `s = n mod 2310`.

### 7.3 Firma prismatica pentagonale

Residui:

```python
r2  = s % 2
r3  = s % 3
r5  = s % 5
r7  = s % 7
r11 = s % 11
vector = [r2, r3, r5, r7, r11]
residues = {2: r2, 3: r3, 5: r5, 7: r7, 11: r11}
```

Struttura:

```json
PrismSignature2310 = {
  "s_mod": int,           // n mod 2310
  "residues": { "p": int },
  "vector": [int, int, int, int, int]
}
```

Uso tipico:

- Come **invariante aggiuntivo** nel header (`header["kernel_2310"]`).
- Come ingresso per futuri modelli di prisma M pianificati per GCC v2.

---

## 8. Oggetto GCC_v1_Block (encode/decode)

L’API high-level espone:

- `encode_block(block, max_prime=31, logic_op=None)`
- `decode_block(gcc_obj)`

### 8.1 Struttura logica di ritorno di `encode_block`

```json
GCC_v1_Block = {
  "header": { ... },
  "invariants": { ... },
  "residual": { ... }
}
```

#### 8.1.1 `header`

```json
"header": {
  "magic": "GCC1",
  "version": "0.1.0",
  "block_len": int,        // numero di byte del blocco
  "max_prime": int,        // limite superiore dei primi usati per M
  "primes": [int, ...],    // lista effettiva dei primi
  "cip": CIP               // struttura descritta sopra
}
```

*(In futuro: possibile campo `"kernel_2310": PrismSignature2310` se il blocco è un numero decimale.)*

#### 8.1.2 `invariants`

Dump separato delle CIDs (ridondante rispetto a CIP, ma comodo):

```json
"invariants": {
  "cid_per_prime": {
    "p": {
      "p": int,
      "H_p": int,
      "Mass_p": int,
      "Supp_p": int,
      "mu_p_q": int,
      "sigma_p_q": int
    },
    ...
  }
}
```

#### 8.1.3 `residual`

Per GCC v1:

- modello di residuo = **identity**.

```json
"residual": {
  "model_type": "identity",
  "model_params": {},
  "residual_stream": [int, int, ...]   // lista 0..255
}
```

La ricostruzione è banale:

- `decoded_bytes = bytes(residual_stream)`.

In futuro:

- `model_type` e `model_params` descriveranno modelli p-adici non banali,
- `residual_stream` conterrà gli scarti del modello, non i dati originali.

---

## 9. Decodifica (`decode_block`)

Given:

```json
gcc_obj = GCC_v1_Block
```

Per il modello `identity`:

1. Leggi:

   ```json
   residual = gcc_obj["residual"]
   model_type = residual["model_type"]
   stream = residual["residual_stream"]
   ```

2. Se `model_type != "identity"`, solleva `NotImplementedError`.
3. Se `stream` è lista di int:

   ```python
   decoded = bytes(int(x) & 0xFF for x in stream)
   ```

4. Restituisci `decoded`.

---

## 10. Collegamento con l’implementazione Python

Modulo / file principali:

- `src/gcc_v1/exponents.py`
  - `build_exponent_matrix(block, primes=None, max_prime=31)`
    → costruisce M e lista `primes` (kernel byte-oriented toy).

- `src/gcc_v1/logic.py`
  - `LogicOp` (Protocol),
  - `XorLogicOp` (implementazione predefinita),
  - `build_logic_signature(M, primes, op)` → logic_signature.

- `src/gcc_v1/invariants.py`
  - `compute_cids(M, primes)` → dict p → CID;
  - `build_cip(M, primes, cids, logic_signature)` → CIP.

- `src/gcc_v1/kernel2310.py`
  - `update_state_2310(digits)` → s_mod;
  - `state_to_prism_signature_2310(s)` → PrismSignature2310;
  - `kernel_2310_from_digits(digits)` → PrismSignature2310 (convenience).

- `src/gcc_v1/spectrum.py`
  - `build_filter_bits(primes, mode, custom_bits)` → F[p];
  - `apply_filter(primes, logic_signature, F)` → out[p];
  - `summarize_spectrum(primes, out)` → spettrografia numerica;
  - `spectral_view(primes, logic_signature, mode, custom_bits)` → (out, summary).

- `src/gcc_v1/codec.py`
  - `encode_block(block, max_prime=31, logic_op=None)` → GCC_v1_Block;
  - `decode_block(gcc_obj)` → bytes.

---

## 11. Roadmap concettuale (post v1)

Slot già previsti dallo SPEC:

- **Difetti**:
  - introdurre operatori D: site / line / plane defect;
  - estendere CIP["defects"] con modelli concreti.

- **Nuovi LogicOp**:
  - es. `NOT.XOR`, operatori dipendenti da p o h;
  - logic_signature rimane identica (Tₚ(0), Tₚ(1)).

- **Modelli di residuale**:
  - usare CIP/CIDs/logic_signature per costruire un **modello M(n)**,
  - salvare solo il residuo `r(n) = f(n) - M(n)`.

- **Kernel 2310 → Prisma M**:
  - usare la firma pentagonale (r2,r3,r5,r7,r11) per costruire pattern di noduli coerenti,
  - integrare kernel 2310 in `encode_block` come opzione ufficiale.

---
