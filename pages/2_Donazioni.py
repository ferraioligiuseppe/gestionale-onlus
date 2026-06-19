"""Modulo Donazioni — registro con inserimento ed eliminazione."""
from datetime import date
import streamlit as st
import database as db

st.title("Donazioni")
st.caption("Registro delle donazioni ricevute")

CAUSALI = ["Donazione libera", "5x1000", "Progetto Scuole Aperte", "Emergenza alluvione",
           "Sostegno a distanza", "Quota associativa", "Raccolta fondi Natale"]
METODI = ["Bonifico", "Carta", "PayPal", "Contanti", "Satispay"]

# --- KPI ------------------------------------------------------------------
tutte = db.donazioni_df()
oggi = date.today()
tot_mese = float(tutte[tutte["data"].str.startswith(oggi.strftime("%Y-%m"))]["importo"].sum())
tot_anno = float(tutte[tutte["data"].str.startswith(str(oggi.year))]["importo"].sum())
ricorrenti = int((tutte["tipo"] == "Ricorrente").sum())

c1, c2, c3 = st.columns(3)
c1.metric(f"Totale {db.mese_nome(oggi).capitalize()}", db.euro(tot_mese))
c2.metric(f"Totale {oggi.year}", db.euro(tot_anno))
c3.metric("Donazioni ricorrenti", ricorrenti)

st.divider()

# --- Filtro + tabella -----------------------------------------------------
filtro = st.radio("Mostra", ["Tutte", "Singola", "Ricorrente"], horizontal=True)
df = db.donazioni_df(filtro)

vista = df.copy()
if not vista.empty:
    vista["Data"] = vista["data"].map(db.data_it)
    vista["Importo"] = vista["importo"].map(db.euro)
    vista["Ricevuta"] = vista["ricevuta"].map(lambda x: "Emessa" if x else "In attesa")
    st.dataframe(
        vista[["Data", "donatore", "causale", "metodo", "tipo", "Importo", "Ricevuta"]].rename(
            columns={"donatore": "Donatore", "causale": "Causale", "metodo": "Metodo", "tipo": "Tipo"}
        ),
        hide_index=True, use_container_width=True,
    )
else:
    st.info("Nessuna donazione registrata.")

st.divider()

# --- Nuova donazione ------------------------------------------------------
st.subheader("Registra donazione")

opzioni = db.soci_options()
with st.form("form_donazione", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        socio_sel = st.selectbox(
            "Collega a un socio (opzionale)",
            options=[None] + list(opzioni.keys()),
            format_func=lambda x: "— Donatore esterno —" if x is None else opzioni[x],
        )
        donatore_manuale = st.text_input("Nome donatore", placeholder="Se esterno o anonimo")
        importo = st.number_input("Importo (€)", min_value=0.0, step=10.0, format="%.2f")
        data_don = st.date_input("Data", value=oggi)
    with col2:
        causale = st.selectbox("Causale", CAUSALI)
        metodo = st.selectbox("Metodo", METODI)
        tipo = st.radio("Tipo", ["Singola", "Ricorrente"], horizontal=True)
        ricevuta = st.checkbox("Emetti ricevuta", value=True)
    note = st.text_input("Note (opzionale)")
    salva = st.form_submit_button("💾 Salva donazione", type="primary")

if salva:
    if socio_sel is not None:
        donatore = opzioni[socio_sel].split(" (")[0]
    else:
        donatore = donatore_manuale.strip() or "Donatore anonimo"
    if importo <= 0:
        st.error("Inserisci un importo maggiore di zero.")
    else:
        db.add_donazione(
            data_don.isoformat(), donatore, importo, causale, metodo, tipo,
            ricevuta, socio_id=socio_sel, note=note.strip() or None,
        )
        st.success(f"Donazione registrata: {donatore} — {db.euro(importo)}")
        st.rerun()

# --- Eliminazione ---------------------------------------------------------
if not df.empty:
    with st.expander("🗑️ Elimina una donazione"):
        mappa = {int(r.id): f"{db.data_it(r.data)} · {r.donatore} · {db.euro(r.importo)}" for r in df.itertuples()}
        sel = st.selectbox("Donazione", options=list(mappa.keys()), format_func=lambda x: mappa[x])
        if st.button("Elimina", type="secondary"):
            db.delete_donazione(sel)
            st.success("Donazione eliminata.")
            st.rerun()
