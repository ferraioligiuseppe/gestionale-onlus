"""
Livello dati del Gestionale ONLUS.
Database SQLite locale (file gestionale.db) — nessun server richiesto.
Crea le tabelle al primo avvio e inserisce dati di esempio.
"""
import sqlite3
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "gestionale.db"


# --------------------------------------------------------------------------
# Connessione (riusata tra i rerun di Streamlit)
# --------------------------------------------------------------------------
@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _init_schema(conn)
    _seed(conn)
    return conn


def _init_schema(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS soci (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tessera TEXT UNIQUE,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            tipo TEXT,
            email TEXT,
            telefono TEXT,
            citta TEXT,
            indirizzo TEXT,
            cf TEXT,
            nascita TEXT,
            iscritto TEXT,
            quota_stato TEXT,
            stato TEXT,
            ruolo TEXT,
            note TEXT
        );

        CREATE TABLE IF NOT EXISTS donazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            donatore TEXT NOT NULL,
            importo REAL NOT NULL,
            causale TEXT,
            metodo TEXT,
            tipo TEXT,
            ricevuta INTEGER DEFAULT 0,
            socio_id INTEGER,
            note TEXT,
            FOREIGN KEY (socio_id) REFERENCES soci(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS eventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT NOT NULL,
            data TEXT NOT NULL,
            ora TEXT,
            luogo TEXT,
            tipo TEXT,
            partecipanti INTEGER DEFAULT 0,
            descrizione TEXT
        );

        CREATE TABLE IF NOT EXISTS quote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            anno INTEGER NOT NULL,
            importo REAL,
            data_pagamento TEXT,
            stato TEXT,
            FOREIGN KEY (socio_id) REFERENCES soci(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


# --------------------------------------------------------------------------
# Dati di esempio
# --------------------------------------------------------------------------
_SOCI_SEED = [
    ("AUR-0142", "Maria Teresa", "Conti", "Socio sostenitore", "mt.conti@email.it", "+39 340 118 4421", "Torino", "Via Po 14, Torino", "CNTMTR62R45L219K", "1962-10-05", "2018-03-14", "In regola", "Attivo", "Socio", "Donatrice storica. Attiva nelle raccolte fondi natalizie."),
    ("AUR-0098", "Luca", "Ferraro", "Volontario", "luca.ferraro@email.it", "+39 333 902 7710", "Settimo T.se", "Via Roma 8, Settimo T.se", "FRRLCU88M12L219R", "1988-08-12", "2020-09-22", "In regola", "Attivo", "Volontario", "Referente logistica eventi. Disponibile nei weekend."),
    ("AUR-0203", "Giulia", "Marchetti", "Socio ordinario", "giulia.marchetti@email.it", "+39 348 551 2093", "Torino", "Corso Francia 102, Torino", "MRCGLI95T58L219W", "1995-12-18", "2022-01-03", "Da rinnovare", "Attivo", "Socio", "Quota in scadenza. Inviato sollecito via email."),
    ("AUR-0007", "Roberto", "Esposito", "Socio sostenitore", "r.esposito@email.it", "+39 335 770 4412", "Chivasso", "Via Torino 5, Chivasso", "SPSRRT70A01L219Y", "1970-01-01", "2015-05-11", "In regola", "Attivo", "Consigliere", "Membro del consiglio direttivo dal 2019."),
    ("AUR-0176", "Francesca", "Lombardi", "Volontaria", "f.lombardi@email.it", "+39 347 220 8856", "Torino", "Via Garibaldi 33, Torino", "LMBFNC91P52L219H", "1991-09-12", "2021-06-18", "Scaduta", "Sospeso", "Volontaria", "Tesseramento scaduto a marzo 2026. Da ricontattare."),
    ("AUR-0231", "Paolo", "Greco", "Socio ordinario", "paolo.greco@email.it", "+39 320 445 1129", "Moncalieri", "Via Vittorio 21, Moncalieri", "GRCPLA83H22L219T", "1983-06-22", "2023-02-07", "In regola", "Attivo", "Socio", "Interessato al progetto Scuole Aperte."),
    ("AUR-0119", "Elena", "Costa", "Volontaria", "elena.costa@email.it", "+39 349 663 2200", "Rivoli", "Via Piave 9, Rivoli", "CSTLNE93D44L219P", "1993-04-04", "2019-10-30", "Da rinnovare", "Attivo", "Volontaria", "Coordina il gruppo doposcuola."),
    ("AUR-0250", "Marco", "Ricci", "Socio ordinario", "marco.ricci@email.it", "+39 331 008 9912", "Torino", "Via Nizza 47, Torino", "RCCMRC90L15L219S", "1990-07-15", "2024-04-15", "In regola", "Attivo", "Socio", "Nuovo socio 2024."),
    ("AUR-0064", "Anna", "Bruno", "Socio sostenitore", "anna.bruno@email.it", "+39 338 112 7745", "Collegno", "Via Martiri 12, Collegno", "BRNNNA75E48L219N", "1975-05-08", "2017-07-09", "In regola", "Attivo", "Tesoriere", "Tesoriere dell'associazione. Gestisce la contabilità."),
    ("AUR-0188", "Davide", "Moretti", "Volontario", "d.moretti@email.it", "+39 342 559 0034", "Nichelino", "Via Torino 88, Nichelino", "MRTDVD89C30L219M", "1989-03-30", "2021-11-25", "Scaduta", "Sospeso", "Volontario", "Sospeso per mancato rinnovo. Era attivo nei trasporti."),
]

# (data, donatore, importo, causale, metodo, tipo, ricevuta)
_DONAZIONI_SEED = [
    ("2026-06-18", "Maria Teresa Conti", 150, "Sostegno a distanza", "Bonifico", "Ricorrente", 1),
    ("2026-06-17", "Luca Ferraro", 50, "Donazione libera", "Satispay", "Singola", 1),
    ("2026-06-16", "Donatore anonimo", 500, "Emergenza alluvione", "Bonifico", "Singola", 0),
    ("2026-06-15", "Studio Bianchi & Rossi", 1000, "Progetto Scuole Aperte", "Bonifico", "Singola", 1),
    ("2026-06-14", "Giulia Marchetti", 30, "Donazione libera", "Carta", "Ricorrente", 1),
    ("2026-06-12", "Fondazione Cariplo", 15000, "Progetto Scuole Aperte", "Bonifico", "Singola", 1),
    ("2026-06-10", "Paolo Greco", 100, "Donazione libera", "PayPal", "Singola", 1),
    ("2026-06-08", "Francesca Lombardi", 75, "Sostegno a distanza", "Carta", "Ricorrente", 1),
    ("2026-06-05", "Gruppo Edilcasa S.r.l.", 2000, "Emergenza alluvione", "Bonifico", "Singola", 0),
    ("2026-06-03", "Donatore anonimo", 20, "Donazione libera", "Contanti", "Singola", 0),
    ("2026-06-01", "Roberto Esposito", 250, "Progetto Scuole Aperte", "Bonifico", "Ricorrente", 1),
    ("2026-05-28", "Maria Teresa Conti", 150, "Sostegno a distanza", "Bonifico", "Ricorrente", 1),
    ("2026-05-25", "Elena Costa", 40, "Donazione libera", "PayPal", "Singola", 1),
    ("2026-05-20", "Comune di Verolengo", 5000, "Progetto Scuole Aperte", "Bonifico", "Singola", 1),
    ("2026-04-15", "Fondazione Cariplo", 10000, "Progetto Scuole Aperte", "Bonifico", "Singola", 1),
    ("2026-03-22", "Anna Bruno", 300, "Donazione libera", "Bonifico", "Ricorrente", 1),
    ("2026-02-10", "Maria Teresa Conti", 150, "Sostegno a distanza", "Bonifico", "Ricorrente", 1),
    ("2026-01-30", "Donatore anonimo", 1200, "5x1000", "Bonifico", "Singola", 0),
]

# (titolo, data, ora, luogo, tipo, partecipanti, descrizione)
_EVENTI_SEED = [
    ("Assemblea dei soci", "2026-06-05", "18:00", "Sede operativa", "Assemblea", 42, "Approvazione bilancio e programma attività."),
    ("Riunione direttivo", "2026-06-09", "21:00", "Online", "Assemblea", 7, "Coordinamento progetti in corso."),
    ("Corso volontari - primo soccorso", "2026-06-12", "09:30", "Aula formazione", "Formazione", 18, "Formazione base per nuovi volontari."),
    ("Banchetto raccolta fondi", "2026-06-18", "10:00", "Piazza Garibaldi", "Raccolta fondi", 12, "Banchetto informativo e raccolta fondi."),
    ("Doposcuola Scuole Aperte", "2026-06-20", "15:00", "Centro civico", "Attività", 24, "Attività di supporto allo studio."),
    ("Cena di solidarietà", "2026-06-27", "20:00", "Oratorio S. Maria", "Raccolta fondi", 80, "Cena benefica a sostegno dei progetti."),
    ("Festa dei volontari", "2026-07-05", "19:00", "Parco del Valentino", "Attività", 60, "Momento conviviale di ringraziamento."),
]


def _seed(conn):
    cur = conn.cursor()
    if cur.execute("SELECT COUNT(*) FROM soci").fetchone()[0] == 0:
        cur.executemany(
            """INSERT INTO soci (tessera,nome,cognome,tipo,email,telefono,citta,indirizzo,cf,nascita,iscritto,quota_stato,stato,ruolo,note)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            _SOCI_SEED,
        )
        # quote storiche per ogni socio
        soci = cur.execute("SELECT id, quota_stato, stato FROM soci").fetchall()
        for s in soci:
            for i, anno in enumerate((2026, 2025, 2024)):
                if i == 0:
                    stato = s["quota_stato"]
                    data_pag = None if stato != "In regola" else f"{anno}-01-12"
                else:
                    stato = "Scaduta" if (s["stato"] == "Sospeso" and i == 1) else "Pagata"
                    data_pag = None if stato == "Scaduta" else f"{anno}-02-15"
                cur.execute(
                    "INSERT INTO quote (socio_id,anno,importo,data_pagamento,stato) VALUES (?,?,?,?,?)",
                    (s["id"], anno, 30, data_pag, stato),
                )

    if cur.execute("SELECT COUNT(*) FROM donazioni").fetchone()[0] == 0:
        for d in _DONAZIONI_SEED:
            nome_completo = d[1]
            row = cur.execute(
                "SELECT id FROM soci WHERE (nome || ' ' || cognome) = ?", (nome_completo,)
            ).fetchone()
            socio_id = row["id"] if row else None
            cur.execute(
                """INSERT INTO donazioni (data,donatore,importo,causale,metodo,tipo,ricevuta,socio_id,note)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (*d, socio_id, None),
            )

    if cur.execute("SELECT COUNT(*) FROM eventi").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO eventi (titolo,data,ora,luogo,tipo,partecipanti,descrizione) VALUES (?,?,?,?,?,?,?)",
            _EVENTI_SEED,
        )
    conn.commit()


# --------------------------------------------------------------------------
# Utilità di formattazione
# --------------------------------------------------------------------------
def euro(x):
    try:
        return "€ " + f"{float(x):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "€ 0"


_MESI = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
         "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def mese_nome(d):
    """Nome del mese in italiano, senza dipendere dal locale di sistema."""
    return _MESI[d.month]


def data_it(iso):
    if not iso:
        return "—"
    try:
        y, m, d = str(iso)[:10].split("-")
        return f"{d}/{m}/{y}"
    except ValueError:
        return str(iso)


# --------------------------------------------------------------------------
# SOCI
# --------------------------------------------------------------------------
def soci_df(search=""):
    conn = get_conn()
    sql = "SELECT * FROM soci"
    params = ()
    if search:
        like = f"%{search.lower()}%"
        sql += (" WHERE lower(nome||' '||cognome||' '||tessera||' '||citta||' '||IFNULL(email,'')) LIKE ?")
        params = (like,)
    sql += " ORDER BY cognome, nome"
    return pd.read_sql_query(sql, conn, params=params)


def soci_options():
    df = soci_df()
    return {int(r.id): f"{r.nome} {r.cognome} ({r.tessera})" for r in df.itertuples()}


def get_socio(socio_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM soci WHERE id = ?", (socio_id,)).fetchone()
    return dict(row) if row else None


def next_tessera():
    conn = get_conn()
    rows = conn.execute("SELECT tessera FROM soci WHERE tessera LIKE 'AUR-%'").fetchall()
    nums = [int(r["tessera"].split("-")[1]) for r in rows if r["tessera"] and r["tessera"].split("-")[1].isdigit()]
    n = (max(nums) + 1) if nums else 1
    return f"AUR-{n:04d}"


def upsert_socio(data, socio_id=None):
    conn = get_conn()
    cur = conn.cursor()
    if socio_id:
        cols = ", ".join(f"{k} = ?" for k in data)
        cur.execute(f"UPDATE soci SET {cols} WHERE id = ?", (*data.values(), socio_id))
    else:
        cols = ", ".join(data.keys())
        ph = ", ".join("?" for _ in data)
        cur.execute(f"INSERT INTO soci ({cols}) VALUES ({ph})", tuple(data.values()))
        socio_id = cur.lastrowid
    conn.commit()
    return socio_id


def delete_socio(socio_id):
    conn = get_conn()
    conn.execute("DELETE FROM soci WHERE id = ?", (socio_id,))
    conn.commit()


# --------------------------------------------------------------------------
# DONAZIONI
# --------------------------------------------------------------------------
def donazioni_df(tipo="Tutte"):
    conn = get_conn()
    sql = "SELECT * FROM donazioni"
    params = ()
    if tipo in ("Singola", "Ricorrente"):
        sql += " WHERE tipo = ?"
        params = (tipo,)
    sql += " ORDER BY data DESC, id DESC"
    return pd.read_sql_query(sql, conn, params=params)


def add_donazione(data, donatore, importo, causale, metodo, tipo, ricevuta, socio_id=None, note=None):
    conn = get_conn()
    conn.execute(
        """INSERT INTO donazioni (data,donatore,importo,causale,metodo,tipo,ricevuta,socio_id,note)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (data, donatore, importo, causale, metodo, tipo, int(ricevuta), socio_id, note),
    )
    conn.commit()


def delete_donazione(don_id):
    conn = get_conn()
    conn.execute("DELETE FROM donazioni WHERE id = ?", (don_id,))
    conn.commit()


# --------------------------------------------------------------------------
# EVENTI
# --------------------------------------------------------------------------
def eventi_df():
    conn = get_conn()
    return pd.read_sql_query("SELECT * FROM eventi ORDER BY data", conn)


def add_evento(titolo, data, ora, luogo, tipo, partecipanti, descrizione=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO eventi (titolo,data,ora,luogo,tipo,partecipanti,descrizione) VALUES (?,?,?,?,?,?,?)",
        (titolo, data, ora, luogo, tipo, int(partecipanti or 0), descrizione),
    )
    conn.commit()


def delete_evento(ev_id):
    conn = get_conn()
    conn.execute("DELETE FROM eventi WHERE id = ?", (ev_id,))
    conn.commit()


# --------------------------------------------------------------------------
# QUOTE / TESSERAMENTI
# --------------------------------------------------------------------------
def quote_df(socio_id):
    conn = get_conn()
    return pd.read_sql_query(
        "SELECT * FROM quote WHERE socio_id = ? ORDER BY anno DESC", conn, params=(socio_id,)
    )


def registra_quota(socio_id, anno, importo, data_pagamento):
    conn = get_conn()
    cur = conn.cursor()
    esiste = cur.execute(
        "SELECT id FROM quote WHERE socio_id = ? AND anno = ?", (socio_id, anno)
    ).fetchone()
    if esiste:
        cur.execute(
            "UPDATE quote SET importo=?, data_pagamento=?, stato=? WHERE id=?",
            (importo, data_pagamento, "Pagata", esiste["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO quote (socio_id,anno,importo,data_pagamento,stato) VALUES (?,?,?,?,?)",
            (socio_id, anno, importo, data_pagamento, "Pagata"),
        )
    # se è l'anno corrente, il socio torna "In regola"
    if anno == date.today().year:
        cur.execute("UPDATE soci SET quota_stato='In regola' WHERE id=?", (socio_id,))
    conn.commit()
