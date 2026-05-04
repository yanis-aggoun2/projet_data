import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data

st.set_page_config(page_title="Explorateur ETF", page_icon="🔍", layout="wide")

st.title("🔍 Explorateur d'ETF")
st.markdown("---")

# Sélection ETF et période
col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.selectbox(
        "Choisir un ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
with col2:
    periode = st.selectbox("Période", ["1 an", "3 ans", "5 ans", "10 ans"], index=1)

etf = ETF_CATALOG[ticker]
jours = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode]
date_debut = (datetime.today() - timedelta(days=jours)).strftime("%Y-%m-%d")

# Fiche ETF
st.markdown("---")
col_info, col_graph = st.columns([1, 2])

with col_info:
    st.markdown(f"### {ticker}")
    st.markdown(f"**{etf['nom']}**")
    st.markdown(f"- **Indice :** {etf['indice']}")
    st.markdown(f"- **Gestionnaire :** {etf['gestionnaire']}")
    st.markdown(f"- **TER annuel :** {etf['ter']*100:.2f}%")
    st.markdown(f"- **TER mensuel :** {etf['ter']/12*100:.4f}%")
    st.markdown(f"- **Eligible PEA :** {'✅ Oui' if etf['pea'] else '❌ Non'}")
    st.markdown(f"_{etf['description']}_")

with col_graph:
    with st.spinner("Chargement des données..."):
        df = get_historical_data(etf["ticker_yf"], date_debut)

    if not df.empty:
        prix_debut = float(df["prix_cloture"].iloc[0])
        prix_fin = float(df["prix_cloture"].iloc[-1])
        variation = (prix_fin - prix_debut) / prix_debut * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["prix_cloture"],
            mode="lines",
            line=dict(color="#2563eb", width=2),
            fill="tozeroy",
            fillcolor="rgba(37,99,235,0.07)"
        ))
        fig.update_layout(
            title=f"{etf['nom']} — {periode}",
            xaxis_title="Date",
            yaxis_title="Prix (€)",
            height=350,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified"
        )
        fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Prix actuel", f"{prix_fin:.2f} €")
        c2.metric("Prix de départ", f"{prix_debut:.2f} €")
        c3.metric(f"Performance {periode}", f"{variation:+.2f}%")
    else:
        st.warning("Données indisponibles pour cet ETF.")

# Comparaison deux ETF
st.markdown("---")
st.markdown("### Comparer deux ETF")

col_a, col_b = st.columns(2)
with col_a:
    etf_a = st.selectbox("ETF A", list(ETF_CATALOG.keys()), index=0, key="a",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_b:
    etf_b = st.selectbox("ETF B", list(ETF_CATALOG.keys()), index=1, key="b",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")

periode_comp = st.selectbox("Période", ["1 an", "3 ans", "5 ans", "10 ans"], index=2, key="pc")
jours_comp = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode_comp]
date_comp = (datetime.today() - timedelta(days=jours_comp)).strftime("%Y-%m-%d")

if st.button("Lancer la comparaison"):
    df_a = get_historical_data(ETF_CATALOG[etf_a]["ticker_yf"], date_comp)
    df_b = get_historical_data(ETF_CATALOG[etf_b]["ticker_yf"], date_comp)

    if not df_a.empty and not df_b.empty:
        perf_a = df_a["prix_cloture"] / df_a["prix_cloture"].iloc[0] * 100
        perf_b = df_b["prix_cloture"] / df_b["prix_cloture"].iloc[0] * 100

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=perf_a.index, y=perf_a, name=etf_a, line=dict(color="#2563eb", width=2)))
        fig2.add_trace(go.Scatter(x=perf_b.index, y=perf_b, name=etf_b, line=dict(color="#f59e0b", width=2)))
        fig2.add_hline(y=100, line_dash="dash", line_color="#94a3b8")
        fig2.update_layout(
            title="Performance normalisée base 100",
            height=380,
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        fig2.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig2.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig2, use_container_width=True)

        def stats(df, info, t):
            perf = (df["prix_cloture"].iloc[-1] / df["prix_cloture"].iloc[0] - 1) * 100
            vol = df["prix_cloture"].pct_change().std() * (252 ** 0.5) * 100
            return {"ETF": t, "Nom": info["nom"], "TER": f"{info['ter']*100:.2f}%",
                    "Performance": f"{perf:+.2f}%", "Volatilité ann.": f"{vol:.2f}%",
                    "PEA": "✅" if info["pea"] else "❌"}

        st.dataframe(pd.DataFrame([
            stats(df_a, ETF_CATALOG[etf_a], etf_a),
            stats(df_b, ETF_CATALOG[etf_b], etf_b)
        ]), use_container_width=True, hide_index=True)
    else:
        st.error("Impossible de charger les données.")
