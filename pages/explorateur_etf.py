import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data

st.set_page_config(page_title="Explorateur ETF", page_icon="🔍", layout="wide")

# ── Dark theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp { background-color: #060e1c !important; font-family: 'Inter', sans-serif !important; }
.main .block-container { padding-top: 2rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; max-width: 1400px !important; }
[data-testid="stSidebar"] { background-color: #08111f !important; border-right: 1px solid #162035 !important; }
[data-testid="stSidebar"] * { color: #7a90a8 !important; }
h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; }
p, li, .stMarkdown p { color: #94a3b8 !important; }
hr, [data-testid="stDivider"] { border-color: #162035 !important; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #0c1928, #0d2040) !important;
    border: 1px solid #1a2e48 !important; border-radius: 14px !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0c1928, #0e2038) !important;
    border: 1px solid #1a2e48 !important; border-radius: 12px !important;
    padding: 20px 24px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.45) !important;
}
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; font-size: 24px !important; }
[data-testid="stMetricLabel"] { color: #3f5470 !important; font-size: 10px !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-weight: 600 !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border: 1px solid #3b82f6 !important; color: #fff !important;
    font-weight: 600 !important; border-radius: 8px !important;
}
.stDataFrame { border: 1px solid #1a2e48 !important; border-radius: 12px !important; overflow: hidden !important; }
[data-testid="stAlert"] { border-radius: 10px !important; }
[data-testid="stSelectbox"] > div > div { background-color: #0c1928 !important; border-color: #1a2e48 !important; color: #c5d4e8 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes graphique sombre ───────────────────────────────────────────────
_BG    = "#0c1928"
_PAPER = "#060e1c"
_GRID  = "#162035"
_TICK  = "#3f5470"

def dark_layout(title="", height=400):
    return dict(
        title=dict(text=title, font=dict(color="#c5d4e8", size=14), x=0.01),
        plot_bgcolor=_BG, paper_bgcolor=_PAPER,
        font=dict(color=_TICK, family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        legend=dict(bgcolor="rgba(12,25,40,0.95)", bordercolor=_GRID, borderwidth=1,
                    font=dict(color="#7a90a8", size=12)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0e2038", bordercolor=_GRID, font=dict(color="#f1f5f9")),
        height=height, margin=dict(l=0, r=0, t=44, b=0),
    )

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Explorateur d'ETF")
st.caption("Module A — Analyse et comparaison d'ETF sur données historiques")
st.divider()

# ── Sélecteurs ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    ticker = st.selectbox(
        "Sélectionner un ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
with col2:
    periode = st.selectbox("Période d'analyse", ["1 an", "3 ans", "5 ans", "10 ans"], index=1)

etf   = ETF_CATALOG[ticker]
jours = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode]
date_debut = (datetime.today() - timedelta(days=jours)).strftime("%Y-%m-%d")

# ── Fiche ETF + Graphique ─────────────────────────────────────────────────────
st.divider()
col_info, col_graph = st.columns([1, 2], gap="large")

with col_info:
    with st.container(border=True):
        st.markdown(f"### {ticker}")
        st.markdown(f"**{etf['nom']}**")
        st.divider()
        st.markdown(f"**Indice répliqué** — {etf['indice']}")
        st.markdown(f"**Gestionnaire** — {etf['gestionnaire']}")
        st.markdown(f"**TER annuel** — `{etf['ter']*100:.2f}%`")
        st.markdown(f"**TER mensuel** — `{etf['ter']/12*100:.4f}%`")
        pea = "✅ Éligible PEA" if etf["pea"] else "❌ Non éligible PEA"
        st.markdown(f"**{pea}**")
        st.divider()
        st.caption(etf["description"])

with col_graph:
    with st.spinner("Chargement des données…"):
        df = get_historical_data(etf["ticker_yf"], date_debut)

    if not df.empty:
        prix_debut = float(df["prix_cloture"].iloc[0])
        prix_fin   = float(df["prix_cloture"].iloc[-1])
        variation  = (prix_fin - prix_debut) / prix_debut * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["prix_cloture"],
            mode="lines",
            line=dict(color="#3b82f6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
            name="Prix de clôture",
            hovertemplate="%{y:.2f} €<extra></extra>",
        ))
        layout = dark_layout(title=f"{etf['nom']} — {periode}", height=360)
        layout["yaxis"]["title"] = dict(text="Prix (€)", font=dict(color=_TICK))
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Prix actuel",              f"{prix_fin:.2f} €")
        c2.metric("Prix de départ",           f"{prix_debut:.2f} €")
        c3.metric(f"Performance ({periode})", f"{variation:+.2f}%")
    else:
        st.warning("Données indisponibles pour cet ETF.")

# ── Comparaison deux ETF ──────────────────────────────────────────────────────
st.divider()
st.markdown("### Comparer deux ETF")

col_a, col_b, col_p = st.columns([2, 2, 1])
with col_a:
    etf_a = st.selectbox("ETF A", list(ETF_CATALOG.keys()), index=0, key="a",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_b:
    etf_b = st.selectbox("ETF B", list(ETF_CATALOG.keys()), index=1, key="b",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_p:
    periode_comp = st.selectbox("Période", ["1 an", "3 ans", "5 ans", "10 ans"], index=2, key="pc")

jours_comp = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode_comp]
date_comp  = (datetime.today() - timedelta(days=jours_comp)).strftime("%Y-%m-%d")

if st.button("Lancer la comparaison", type="primary"):
    df_a = get_historical_data(ETF_CATALOG[etf_a]["ticker_yf"], date_comp)
    df_b = get_historical_data(ETF_CATALOG[etf_b]["ticker_yf"], date_comp)

    if not df_a.empty and not df_b.empty:
        perf_a = df_a["prix_cloture"] / df_a["prix_cloture"].iloc[0] * 100
        perf_b = df_b["prix_cloture"] / df_b["prix_cloture"].iloc[0] * 100

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=perf_a.index, y=perf_a,
            name=f"{etf_a} — {ETF_CATALOG[etf_a]['nom']}",
            line=dict(color="#3b82f6", width=2.5),
            hovertemplate="%{y:.1f}<extra>" + etf_a + "</extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=perf_b.index, y=perf_b,
            name=f"{etf_b} — {ETF_CATALOG[etf_b]['nom']}",
            line=dict(color="#f59e0b", width=2.5),
            hovertemplate="%{y:.1f}<extra>" + etf_b + "</extra>",
        ))
        fig2.add_hline(y=100, line_dash="dash", line_color="#1a2e48", line_width=1.5,
                       annotation_text="Base 100", annotation_font_color=_TICK)
        layout2 = dark_layout(title=f"Performance normalisée base 100 — {periode_comp}", height=420)
        layout2["yaxis"]["title"] = dict(text="Base 100", font=dict(color=_TICK))
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

        def stats(df, info, t):
            perf = (df["prix_cloture"].iloc[-1] / df["prix_cloture"].iloc[0] - 1) * 100
            vol  = df["prix_cloture"].pct_change().std() * (252 ** 0.5) * 100
            return {
                "ETF": t, "Nom": info["nom"],
                "Performance": f"{perf:+.2f}%",
                "Volatilité ann.": f"{vol:.2f}%",
                "TER annuel": f"{info['ter']*100:.2f}%",
                "PEA": "✅ Oui" if info["pea"] else "❌ Non",
            }

        st.dataframe(
            pd.DataFrame([stats(df_a, ETF_CATALOG[etf_a], etf_a),
                          stats(df_b, ETF_CATALOG[etf_b], etf_b)]),
            use_container_width=True, hide_index=True,
        )
    else:
        st.error("Impossible de charger les données pour un ou plusieurs ETF.")

# Ajouter un nouvel ETF
st.markdown("---")
st.markdown("### ➕ Ajouter un nouvel ETF")

with st.expander("Formulaire d'ajout"):
    st.info("Le ticker Yahoo Finance est utilisé pour récupérer les données. Exemple : CW8.PA, IWDA.AS, SP5.PA")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        new_code = st.text_input("Code (ex: IWDA)", max_chars=10).strip().upper()
        new_nom = st.text_input("Nom complet (ex: iShares Core MSCI World)")
        new_indice = st.text_input("Indice répliqué (ex: MSCI World)")
        new_ticker_yf = st.text_input("Ticker Yahoo Finance (ex: IWDA.AS)")
    with col_f2:
        new_gestionnaire = st.text_input("Gestionnaire (ex: BlackRock)")
        new_ter = st.number_input("TER annuel (%)", min_value=0.0, max_value=5.0,
                                   value=0.20, step=0.01, format="%.2f")
        new_pea = st.selectbox("Eligible PEA", ["Non", "Oui"]) == "Oui"
        new_description = st.text_area("Description", height=80)

    if st.button("💾 Enregistrer l'ETF", type="primary"):
        if not new_code or not new_nom or not new_ticker_yf:
            st.error("Les champs Code, Nom et Ticker Yahoo Finance sont obligatoires.")
        elif new_code in ETF_CATALOG:
            st.error(f"L'ETF '{new_code}' existe déjà dans la base.")
        else:
            with st.spinner("Vérification du ticker Yahoo Finance..."):
                df_test = get_historical_data(
                    new_ticker_yf,
                    (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
                )
            if df_test.empty:
                st.error(f"Le ticker '{new_ticker_yf}' est introuvable sur Yahoo Finance. Vérifiez et réessayez.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO etf (code, nom, indice, gestionnaire, ter, pea, ticker_yf, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (new_code, new_nom, new_indice, new_gestionnaire,
                          new_ter / 100, new_pea, new_ticker_yf, new_description))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ ETF '{new_code} — {new_nom}' ajouté ! Rechargez la page pour le voir dans la liste.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erreur lors de l'insertion : {e}")