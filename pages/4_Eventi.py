"""Modulo Eventi — calendario attività con inserimento ed eliminazione."""
from datetime import date
import pandas as pd
import streamlit as st
import database as db

st.title("Eventi")
st.caption("Calendario attività e iniziative")

TIPI = ["Assemblea", "Formazione", "Raccolta fondi", "Attività"]

df = db.eventi_df()
oggi = date.today()

futuri = df[df["data"] >= oggi.isoformat()]
passati = df[df["data"] < oggi.isoformat()]

c1, c2, c3 = st.columns(3)
c1.metric("In programma", len(futuri))
c2.metric("Iscritti totali (futuri)", int(futuri["partecipanti"].sum()) if not futuri.empty else 0)
c3.metric("Eventi svolti", len(passati))

st.divider()

# --- Prossimi eventi ------------------------------------------------------
st.subheader("In programma")
if futuri.empty:
    st.info("Nessun evento in programma.")
for _, e in futuri.iterrows():
    with st.container(border=True):
        a, b = st.columns([3, 1])
        a.markdown(f"**{e['titolo']}**  \n:grey[{e['descrizione'] or ''}]")
        a.caption(f"📅 {db.data_it(e['data'])} · 🕒 {e['ora']} · 📍 {e['luogo']} · 👥 {e['partecipanti']} iscritti")
        b.markdown(f":blue-background[{e['tipo']}]")

with st.expander("Mostra eventi passati"):
    if passati.empty:
        st.write("Nessun evento passato.")
    else:
        p = passati.copy()
        p["Data"] = p["data"].map(db.data_it)
        st.dataframe(
            p[["Data", "titolo", "tipo", "luogo", "partecipanti"]].rename(
                columns={"titolo": "Titolo", "tipo": "Tipo", "luogo": "Luogo", "partecipanti": "Iscritti"}
            ),
            hide_index=True, use_container_width=True,
        )

st.divider()

# --- Nuovo evento ---------------------------------------------------------
st.subheader("Crea evento")
with st.form("form_evento", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        titolo = st.text_input("Titolo *")
        data_ev = st.date_input("Data", value=oggi)
        ora = st.time_input("Ora")
    with col2:
        tipo = st.selectbox("Tipo", TIPI)
        luogo = st.text_input("Luogo")
        partecipanti = st.number_input("Iscritti previsti", min_value=0, step=1)
    descrizione = st.text_area("Descrizione")
    crea = st.form_submit_button("➕ Crea evento", type="primary")

if crea:
    if not titolo.strip():
        st.error("Il titolo è obbligatorio.")
    else:
        db.add_evento(titolo.strip(), data_ev.isoformat(), ora.strftime("%H:%M"),
                      luogo.strip(), tipo, partecipanti, descrizione.strip() or None)
        st.success(f"Evento creato: {titolo}")
        st.rerun()

# --- Eliminazione ---------------------------------------------------------
if not df.empty:
    with st.expander("🗑️ Elimina un evento"):
        mappa = {int(r.id): f"{db.data_it(r.data)} · {r.titolo}" for r in df.itertuples()}
        sel = st.selectbox("Evento", options=list(mappa.keys()), format_func=lambda x: mappa[x])
        if st.button("Elimina", type="secondary"):
            db.delete_evento(sel)
            st.success("Evento eliminato.")
            st.rerun()
