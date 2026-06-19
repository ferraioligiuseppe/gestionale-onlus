"""Modulo Soci e volontari — anagrafica con inserimento, modifica ed eliminazione."""
from datetime import date
import streamlit as st
import database as db

st.title("Soci e volontari")
st.caption("Anagrafica completa dell'associazione")

TIPI = ["Socio ordinario", "Socio sostenitore", "Volontario", "Volontaria", "Socio onorario"]
QUOTE = ["In regola", "Da rinnovare", "Scaduta"]
STATI = ["Attivo", "Sospeso"]

# --- Filtro + tabella -----------------------------------------------------
search = st.text_input("🔍 Cerca", placeholder="Nome, tessera, città, email...")
df = db.soci_df(search)

st.caption(f"{len(df)} soci")
vista = df.copy()
if not vista.empty:
    vista["Nome"] = vista["nome"] + " " + vista["cognome"]
    vista["Iscritto"] = vista["iscritto"].map(db.data_it)
    st.dataframe(
        vista[["tessera", "Nome", "tipo", "email", "citta", "quota_stato", "stato"]].rename(
            columns={"tessera": "Tessera", "tipo": "Tipo", "email": "Email",
                     "citta": "Città", "quota_stato": "Quota", "stato": "Stato"}
        ),
        hide_index=True, use_container_width=True,
    )
else:
    st.info("Nessun socio trovato.")

st.divider()

# --- Inserimento / modifica ----------------------------------------------
st.subheader("Inserisci o modifica socio")

opzioni = db.soci_options()
scelta = st.selectbox(
    "Socio",
    options=["➕ Nuovo socio"] + list(opzioni.keys()),
    format_func=lambda x: x if x == "➕ Nuovo socio" else opzioni[x],
)

esistente = None if scelta == "➕ Nuovo socio" else db.get_socio(scelta)

def _val(k, default=""):
    return esistente[k] if esistente and esistente.get(k) is not None else default

with st.form("form_socio", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome *", _val("nome"))
        tipo = st.selectbox("Tipo", TIPI, index=TIPI.index(_val("tipo")) if _val("tipo") in TIPI else 0)
        email = st.text_input("Email", _val("email"))
        citta = st.text_input("Città", _val("citta"))
        cf = st.text_input("Codice fiscale", _val("cf"))
        quota_stato = st.selectbox("Stato quota", QUOTE, index=QUOTE.index(_val("quota_stato")) if _val("quota_stato") in QUOTE else 0)
    with col2:
        cognome = st.text_input("Cognome *", _val("cognome"))
        ruolo = st.text_input("Ruolo", _val("ruolo", "Socio"))
        telefono = st.text_input("Telefono", _val("telefono"))
        indirizzo = st.text_input("Indirizzo", _val("indirizzo"))
        nascita = st.text_input("Data di nascita (AAAA-MM-GG)", _val("nascita"))
        stato = st.selectbox("Stato", STATI, index=STATI.index(_val("stato")) if _val("stato") in STATI else 0)
    note = st.text_area("Note", _val("note"))

    salva = st.form_submit_button("💾 Salva", type="primary")

if salva:
    if not nome.strip() or not cognome.strip():
        st.error("Nome e cognome sono obbligatori.")
    else:
        dati = dict(
            nome=nome.strip(), cognome=cognome.strip(), tipo=tipo, email=email.strip(),
            telefono=telefono.strip(), citta=citta.strip(), indirizzo=indirizzo.strip(),
            cf=cf.strip(), nascita=nascita.strip(), quota_stato=quota_stato, stato=stato,
            ruolo=ruolo.strip(), note=note.strip(),
        )
        if esistente:
            db.upsert_socio(dati, socio_id=esistente["id"])
            st.success(f"Socio aggiornato: {nome} {cognome}")
        else:
            dati["tessera"] = db.next_tessera()
            dati["iscritto"] = date.today().isoformat()
            db.upsert_socio(dati)
            st.success(f"Nuovo socio inserito: {nome} {cognome} ({dati['tessera']})")
        st.rerun()

if esistente:
    with st.expander("⚠️ Elimina socio"):
        st.write(f"Stai per eliminare **{esistente['nome']} {esistente['cognome']}** e i relativi tesseramenti.")
        if st.button("Elimina definitivamente", type="secondary"):
            db.delete_socio(esistente["id"])
            st.success("Socio eliminato.")
            st.rerun()
