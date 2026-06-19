# Gestionale ONLUS — Associazione Aurora

Gestionale per associazioni del terzo settore, costruito con **Streamlit** e
**database SQLite** (i dati restano salvati sul tuo computer tra una sessione e
l'altra). Nessun server esterno, nessun account: gira tutto in locale.

## Moduli

- **Dashboard** — KPI, andamento donazioni, prossimi eventi, quote in scadenza
- **Soci e volontari** — anagrafica con inserimento, modifica ed eliminazione
- **Donazioni** — registro donazioni con collegamento ai soci e ricevute
- **Tesseramenti** — stato quote e registrazione pagamenti, storico per socio
- **Eventi** — calendario attività con creazione ed eliminazione
- **Report** — statistiche economiche e composizione della base associativa

---

## Come si avvia

Serve **Python 3.9 o superiore** installato sul computer.

### 1. Apri il terminale nella cartella del progetto

```bash
cd gestionale-streamlit
```

### 2. (Consigliato) Crea un ambiente virtuale

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Avvia il gestionale

```bash
streamlit run app.py
```

Si aprirà automaticamente nel browser (di solito su http://localhost:8501).

---

## Il database

- Al primo avvio viene creato il file **`gestionale.db`** con alcuni dati di
  esempio (soci, donazioni, eventi, quote).
- Ogni inserimento, modifica o eliminazione viene **salvato subito** nel file.
- Per ripartire da zero: chiudi l'app, elimina `gestionale.db`, riavvia.
- Per fare un backup: copia il file `gestionale.db`.

## Struttura dei file

```
gestionale-streamlit/
├── app.py                  # Dashboard (pagina iniziale)
├── database.py             # Schema, dati di esempio e funzioni sul DB
├── requirements.txt        # Dipendenze Python
├── .streamlit/config.toml  # Tema e impostazioni
└── pages/
    ├── 1_Soci.py
    ├── 2_Donazioni.py
    ├── 3_Tesseramenti.py
    ├── 4_Eventi.py
    └── 5_Report.py
```

## Note

- È un'applicazione **monoutente in locale**. Per un uso multiutente in rete
  servirebbe un database condiviso (es. PostgreSQL) e un'autenticazione: si può
  aggiungere in un secondo momento partendo da questa base.
- I dati di esempio sono fittizi e servono solo a mostrare il funzionamento.
