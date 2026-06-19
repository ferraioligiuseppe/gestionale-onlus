"""
Gestionale ONLUS — Associazione Aurora
Home / Dashboard

Avvio:  streamlit run app.py
"""
from datetime import date
import pandas as pd
import streamlit as st

import database as db

st.set_page_config(
    page_title="Gestionale ONLUS",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Piccoli ritocchi estetici
st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; max-width: 1200px;}
      [data-testid="stMetricValue"] {font-size: 1.9rem;}
      h1, h2, h3 {letter-spacing: -0.01em;}
      [data-testid="stSidebarNav"]::before {
          content: "Associazione Aurora";
          display: block; padding: 0 1rem .25rem; font-weight: 700; font-size: 1.05rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

db.get_conn()  # garantisce inizializzazione DB e seed

# -------------------------------------------------------------------------
st.title("Dashboard")
st.caption("Panoramica generale dell'associazione")

soci = db.soci_df()
don = db.donazioni_df()
eventi = db.eventi_df()

oggi = date.today()
mese_corrente = oggi.strftime("%Y-%m")

soci_attivi = int((soci["stato"] == "Attivo").sum())
don_mese = float(don[don["data"].str.startswith(mese_corrente)]["importo"].sum())
quote_rinnovo = int(soci["quota_stato"].isin(["Da rinnovare", "Scaduta"]).sum())
eventi_futuri = int((eventi["data"] >= oggi.isoformat()).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Soci attivi", soci_attivi)
c2.metric(f"Donazioni di {db.mese_nome(oggi).capitalize()}", db.euro(don_mese))
c3.metric("Quote da rinnovare", quote_rinnovo)
c4.metric("Eventi in programma", eventi_futuri)

st.divider()

left, right = st.columns([1.6, 1])

with left:
    st.subheader("Andamento donazioni")
    if not don.empty:
        d = don.copy()
        d["mese"] = pd.to_datetime(d["data"]).dt.to_period("M").astype(str)
        trend = d.groupby("mese")["importo"].sum().reset_index().sort_values("mese").tail(12)
        trend = trend.set_index("mese")
        st.bar_chart(trend, height=240, color="#2f5fa8")

    st.subheader("Donazioni recenti")
    recenti = don.head(6).copy()
    if not recenti.empty:
        recenti["Data"] = recenti["data"].map(db.data_it)
        recenti["Importo"] = recenti["importo"].map(db.euro)
        st.dataframe(
            recenti[["Data", "donatore", "causale", "metodo", "Importo"]].rename(
                columns={"donatore": "Donatore", "causale": "Causale", "metodo": "Metodo"}
            ),
            hide_index=True, use_container_width=True,
        )

with right:
    st.subheader("Prossimi eventi")
    prossimi = eventi[eventi["data"] >= oggi.isoformat()].head(5)
    if prossimi.empty:
        st.info("Nessun evento in programma.")
    for _, e in prossimi.iterrows():
        st.markdown(
            f"**{e['titolo']}**  \n"
            f":grey[{db.data_it(e['data'])} · {e['ora']} · {e['luogo']}]"
        )

    st.subheader("Quote in scadenza")
    scad = soci[soci["quota_stato"].isin(["Da rinnovare", "Scaduta"])].head(6)
    if scad.empty:
        st.success("Tutte le quote sono in regola.")
    for _, s in scad.iterrows():
        badge = "🟠" if s["quota_stato"] == "Da rinnovare" else "🔴"
        st.markdown(f"{badge} **{s['nome']} {s['cognome']}** · :grey[{s['tessera']} — {s['quota_stato']}]")

st.divider()
st.caption(
    "Gestionale ONLUS · dati salvati localmente in **gestionale.db** (SQLite). "
    "Usa il menu a sinistra per navigare i moduli."
)
