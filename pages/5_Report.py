"""Modulo Report — statistiche economiche e associative."""
from datetime import date
import pandas as pd
import streamlit as st
import database as db

st.title("Report e statistiche")
st.caption("Andamento economico e composizione della base associativa")

don = db.donazioni_df()
soci = db.soci_df()
oggi = date.today()

# --- KPI ------------------------------------------------------------------
raccolto_anno = float(don[don["data"].str.startswith(str(oggi.year))]["importo"].sum())
n_donatori = don["donatore"].nunique()
media = float(don["importo"].mean()) if not don.empty else 0
cinquemille = float(don[don["causale"] == "5x1000"]["importo"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Raccolto {oggi.year}", db.euro(raccolto_anno))
c2.metric("Donatori distinti", n_donatori)
c3.metric("Donazione media", db.euro(media))
c4.metric("5x1000", db.euro(cinquemille))

st.divider()

# --- Andamento mensile ----------------------------------------------------
st.subheader("Andamento donazioni per mese")
if not don.empty:
    d = don.copy()
    d["mese"] = pd.to_datetime(d["data"]).dt.to_period("M").astype(str)
    mensile = d.groupby("mese")["importo"].sum().reset_index().sort_values("mese").set_index("mese")
    st.bar_chart(mensile, height=260, color="#2f5fa8")

col_a, col_b = st.columns(2)

# --- Donazioni per causale ------------------------------------------------
with col_a:
    st.subheader("Donazioni per causale")
    if not don.empty:
        per_causale = don.groupby("causale")["importo"].sum().sort_values(ascending=False)
        st.bar_chart(per_causale, height=300, color="#2f8f6b", horizontal=True)

# --- Composizione base associativa ----------------------------------------
with col_b:
    st.subheader("Composizione base associativa")
    if not soci.empty:
        per_tipo = soci.groupby("tipo")["id"].count().rename("Soci")
        st.bar_chart(per_tipo, height=300, color="#c8861a")
        st.caption(f"Totale: {len(soci)} soci · {int((soci['stato']=='Attivo').sum())} attivi")

st.divider()

# --- Principali donatori ---------------------------------------------------
st.subheader("Principali donatori")
if not don.empty:
    top = (
        don.groupby("donatore")
        .agg(totale=("importo", "sum"), donazioni=("id", "count"))
        .sort_values("totale", ascending=False)
        .head(10)
        .reset_index()
    )
    top["Totale"] = top["totale"].map(db.euro)
    st.dataframe(
        top[["donatore", "donazioni", "Totale"]].rename(
            columns={"donatore": "Donatore", "donazioni": "N. donazioni"}
        ),
        hide_index=True, use_container_width=True,
    )
