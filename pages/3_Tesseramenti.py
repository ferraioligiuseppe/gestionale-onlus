"""Modulo Tesseramenti — stato quote e registrazione pagamenti."""
from datetime import date
import streamlit as st
import database as db

st.title("Tesseramenti")
st.caption("Quote associative, rinnovi e storico pagamenti")

soci = db.soci_df()

# --- Riepilogo ------------------------------------------------------------
in_regola = int((soci["quota_stato"] == "In regola").sum())
da_rinnovare = int((soci["quota_stato"] == "Da rinnovare").sum())
scadute = int((soci["quota_stato"] == "Scaduta").sum())

c1, c2, c3 = st.columns(3)
c1.metric("In regola", in_regola)
c2.metric("Da rinnovare", da_rinnovare)
c3.metric("Scadute", scadute)

st.divider()

# --- Elenco con stato quota ----------------------------------------------
st.subheader("Stato quote soci")
vista = soci.copy()
vista["Nome"] = vista["nome"] + " " + vista["cognome"]
st.dataframe(
    vista[["tessera", "Nome", "tipo", "quota_stato", "stato"]].rename(
        columns={"tessera": "Tessera", "tipo": "Tipo", "quota_stato": "Quota", "stato": "Stato socio"}
    ),
    hide_index=True, use_container_width=True,
)

st.divider()

# --- Storico e registrazione pagamento -----------------------------------
st.subheader("Dettaglio socio")
opzioni = db.soci_options()
if opzioni:
    socio_id = st.selectbox("Seleziona socio", options=list(opzioni.keys()), format_func=lambda x: opzioni[x])
    socio = db.get_socio(socio_id)

    st.markdown(f"**{socio['nome']} {socio['cognome']}** · {socio['tessera']} · stato quota: **{socio['quota_stato']}**")

    quote = db.quote_df(socio_id)
    if not quote.empty:
        q = quote.copy()
        q["Importo"] = q["importo"].map(db.euro)
        q["Pagamento"] = q["data_pagamento"].map(db.data_it)
        st.dataframe(
            q[["anno", "Importo", "Pagamento", "stato"]].rename(
                columns={"anno": "Anno", "stato": "Stato"}
            ),
            hide_index=True, use_container_width=True,
        )

    with st.form("form_quota", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        anno = col1.number_input("Anno", min_value=2015, max_value=2035, value=date.today().year, step=1)
        importo = col2.number_input("Importo (€)", min_value=0.0, value=30.0, step=5.0)
        data_pag = col3.date_input("Data pagamento", value=date.today())
        registra = st.form_submit_button("✅ Registra quota pagata", type="primary")

    if registra:
        db.registra_quota(int(socio_id), int(anno), float(importo), data_pag.isoformat())
        st.success(f"Quota {anno} registrata per {socio['nome']} {socio['cognome']}.")
        st.rerun()
