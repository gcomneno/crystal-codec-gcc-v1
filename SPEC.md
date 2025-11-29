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
