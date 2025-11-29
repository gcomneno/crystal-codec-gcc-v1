## 1️⃣ Stato attuale GCC v1

Oggi **GCC v1** è:
- Un **pacchetto Python installabile** (`gcc_v1_crystal_codec` via `pyproject.toml`).
- Con un’API chiara di alto livello:
  * `encode_block(block, max_prime=31, logic_op=None)`
  * `decode_block(gcc_obj)`
- Che per ogni blocco:
  * costruisce un **prisma p-adico** aggregato (matrice M[h][j]),
  * calcola **CIDₚ** per ogni primo (Hₚ, Massₚ, Suppₚ, μₚ_q, σₚ_q),
  * costruisce una **CIP** completa (H_total, masse, per-prime, logic_signature, defects slot, fingerprint SHA-256),
  * salva un **residuo = identity** (lista byte originali).

Più:
- Un **kernel 2310** separato (modulo `kernel2310.py`) che fa da “prisma pentagonale” per numeri in base 10.
- Un **core logico** astratto (`LogicOp` + `XorLogicOp`) e una `logic_signature` per primo (`T_p(0), T_p(1)`).
- Un modulo **spettrografico** (`spectrum.py`) per filtri luce nera/bianca/custom.
- Un **Spectral Lab esterno** (`lab/spectral_filters.py`) con:
  * dataclass `Spectrum`,
  * pipeline `f(Spectrum_prev) -> nuovo filtro`.

In pratica: *un modello cristallino/logico completo, con residuo ancora banale*.

---

## 2️⃣ Struttura del repo e tooling (già “da vetrina”)

**Root:**
- `pyproject.toml` con:
  * metadata progetto,
  * extras `dev` (pytest, pre-commit, ruff),
  * config Ruff (lint + format).
- `README.md` pensato per lettori tecnici.
- `SPEC.md` con la formalizzazione (lattice+basis, DF/CF, CID/CIP, kernel 2310, schema JSON).
- `LICENSE` MIT.

**Codice:**
- `src/gcc_v1/__init__.py` – API esportate.
- `src/gcc_v1/codec.py` – encode/decode, oggetto `GCC_v1_Block`.
- `src/gcc_v1/exponents.py` – costruzione prisma M (modello toy).
- `src/gcc_v1/logic.py` – LogicOp, XorLogicOp, logic_signature.
- `src/gcc_v1/invariants.py` – CIDₚ, CIP, fingerprint.
- `src/gcc_v1/kernel2310.py` – n mod 2310, residui, firma vettoriale.
- `src/gcc_v1/spectrum.py` – filtri bit e spettrografia.

**Demo / Lab / Test:**
- `examples/demo_encode.py` – end-to-end, header + CIP + round-trip.
- `examples/demo_kernel_2310.py` – kernel 2310 e firma pentagonale.
- `examples/demo_spectrum.py` – luce nera/bianca con spettro numerico.
- `examples/demo_spectral_pipeline.py` – pipeline con f(Spectrum_prev).
- `lab/spectral_filters.py` – laboratorio filtri; modulare e non invasivo.
- `tests/test_basic.py` – round-trip + CIP minima.

**Qualità e CI:**
- `.pre-commit-config.yaml` – trailing whitespace, EOF, YAML/TOML, Ruff + Ruff-format.
- `.github/workflows/ci.yml` – GitHub Actions:
  * install `pre-commit` + `.[dev]`,
  * `pre-commit run --all-files --show-diff-on-failure`,
  * `pytest -q`.
- Tag **`v0.1.0`** pubblicato.

=> Dal punto di vista “ingegneristico”: **chiunque entra vede un progetto R&D ma disciplinato**.

---

## 3️⃣ Cosa è DONE e cosa è ancora APERTO (in modo esplicito)

### DONE (veri obiettivi raggiunti)
- ✅ Modellazione del prisma p-adico aggregato e dei noduli.
- ✅ Definizione chiara di **CIDₚ** e **CIP** + fingerprint SHA-256.
- ✅ Introduzione di un **core logico astratto** (LogicOp) e di `logic_signature`.
- ✅ Kernel 2310 per numeri decimali con firma pentagonale.
- ✅ Spettrografia numerica (luce nera, luce bianca, filtri custom).
- ✅ API encode/decode stabili a livello logico.
- ✅ Documentazione tecnica (SPEC) + README + esempi.
- ✅ Tooling completo (pytest, Ruff, pre-commit, CI).

### Ancora APERTO (backlog potenziale)

Qui ha senso distinguere **v1.1 “piccola”** vs **v2 “grossa”**.

#### v1.1 – miglioramenti “incrementali”
- 🔸 Aggiungere qualche **test in più** sulle invarianti (es. un prisma sintetico noto con CIDₚ/CIP attesi).
- 🔸 Migliorare la **copertura degli esempi**:
    * un esempio che salva/legge `GCC_v1_Block` su disco (JSON).
    * un esempio che confronta due blocchi tramite sola CIP/fingerprint.

#### v2 – evoluzioni di concetto
- 🚀 **Residual model ≠ identity**:
  * usare la CIP/CIDs per definire un modello p-adico del blocco,
  * memorizzare solo `residuo = f(original) - modello`.

- 🚀 **Difetti cristallini reali**:
  * implementare un modello semplice (`site defect` su un p, a un certo h),
  * farli comparire in `cip["defects"]` con semantica concreta.

- 🚀 **Nuovi LogicOp**:
  * ad es. `NotXorLogicOp`, o operatori dipendenti da p o da h,
  * comparare logic_signature e spettrografia per operatori diversi.

- 🚀 **Integrazione con altri progetti**:
  * usare Digit-Probe per analizzare gli stream di residuale,
  * loggare CIP/CIDs come “metadati numerici” in qualche pipeline di ML-Lab.

## Obiettivo

Definire e completare una micro-release **v1.1.0** di GCC v1 che non cambia la filosofia del progetto, ma ne rafforza:

- affidabilità (test migliori),
- osservabilità (JSON on-wire),
- estendibilità (primo modello di residuale non banale).

---

## Scope v1.1.0 (minimo)

- [ ] **Invarianti CID/CIP ben testate**
  - Issue: #1 (test su prisma sintetico, Hₚ, Massₚ, Suppₚ, μₚ_q, σₚ_q, H_total, row/col_mass).
- [ ] **Demo JSON I/O**
  - Issue: #2 (script examples/demo_json_io.py, round-trip via file JSON).
- [ ] **Aggiornamento README / SPEC**
  - Minima nota che cita:
    - i test invarianti,
    - la demo JSON.

---

## Fuori scope (v2+)

- Modelli di residuale avanzati (oltre al primo “toy”).
- Modelli di difetti cristallini complessi.
- Nuovi LogicOp oltre a XOR (es. NOT.XOR dipendente da p/h).

Questi temi restano nell’issue di ricerca dedicata e in eventuali milestone future (v2.0.0+).
