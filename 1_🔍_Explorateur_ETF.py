import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data, format_currency, format_percent

st.set_page_config(page_title="Explorateur d'ETF", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
.etf-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}
.stat-row { display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap; }
.stat-box {
    flex: 1; min-width: 100px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
}
.stat-box .lbl { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.stat-box .val { font-size: 1.3rem; font-weight: 700; color: #0f172a; font-family: 'DM Serif Display', serif; }
.info-box { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #1e3a8a; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔍 Explorateur d'ETF")
st.markdown("Recherchez un ETF, comparez ses caractéristiques et visualisez ses performances.")

# ── Sélection ETF ──────────────────────────────────────────────────────────
col_sel, col_per = st.columns([2, 1])

with col_sel:
    ticker = st.selectbox(
        "Sélectionner un ETF",
        options=list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )

with col_per:
    periode = st.selectbox("Période", ["1 an", "3 ans", "5 ans", "10 ans"], index=1)

etf = ETF_CATALOG[ticker]
periode_map = {"1 an": 365, "3 ans": 365*3, "5 ans": 365*5, "10 ans": 365*10}
jours = periode_map[periode]
date_debut = (datetime.today() - timedelta(days=jours)).strftime("%Y-%m-%d")

# ── Fiche ETF ───────────────────────────────────────────────────────────────
st.markdown("---")
col_info, col_graph = st.columns([1, 2])

with col_info:
    pea_badge = '<span style="background:#dcfce7;color:#15803d;font-size:0.75rem;font-weight:600;padding:0.2rem 0.7rem;border-radius:999px;">✅ Éligible PEA</span>' if etf["pea"] else '<span style="background:#fee2e2;color:#b91c1c;font-size:0.75rem;font-weight:600;padding:0.2rem 0.7rem;border-radius:999px;">❌ Non éligible PEA</span>'

    st.markdown(f"""
    <div class="etf-card">
        <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div style="font-size:2rem; font-weight:800; color:#0f172a; font-family:'DM Serif Display',serif;">{ticker}</div>
                <div style="font-size:1rem; color:#475569; margin-top:0.2rem;">{etf['nom']}</div>
            </div>
            <div>{pea_badge}</div>
        </div>
        <div style="margin-top:1rem; font-size:0.9rem; color:#64748b; line-height:1.6;">{etf['description']}</div>
        <div class="stat-row">
            <div class="stat-box">
                <div class="lbl">Indice répliqué</div>
                <div class="val" style="font-size:0.95rem;">{etf['indice']}</div>
            </div>
            <div class="stat-box">
                <div class="lbl">Gestionnaire</div>
                <div class="val" style="font-size:0.95rem;">{etf['gestionnaire']}</div>
            </div>
        </div>
        <div class="stat-row">
            <div class="stat-box">
                <div class="lbl">TER annuel</div>
                <div class="val" style="color:#dc2626;">{etf['ter']*100:.2f}%</div>
            </div>
            <div class="stat-box">
                <div class="lbl">TER mensuel</div>
                <div class="val" style="color:#dc2626;">{etf['ter']/12*100:.4f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_graph:
    with st.spinner("Chargement des données..."):
        df = get_historical_data(etf["ticker_yf"], date_debut)

    if not df.empty:
        prix_debut = float(df["prix_cloture"].iloc[0])
        prix_fin = float(df["prix_cloture"].iloc[-1])
        variation = (prix_fin - prix_debut) / prix_debut * 100
        couleur = "#16a34a" if variation >= 0 else "#dc2626"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["prix_cloture"],
            mode="lines",
            name=ticker,
            line=dict(color=couleur, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({'22,163,74' if variation >= 0 else '220,38,38'},0.06)"
        ))
        fig.update_layout(
            title=f"{etf['nom']} — {periode}",
            xaxis_title="Date",
            yaxis_title="Prix de clôture (€)",
            height=360,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="DM Sans"),
            showlegend=False,
            hovermode="x unified"
        )
        fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Prix actuel", f"{prix_fin:.2f} €")
        c2.metric("Prix de départ", f"{prix_debut:.2f} €")
        c3.metric(f"Performance {periode}", f"{variation:+.2f}%", delta_color="normal")
    else:
        st.warning("Impossible de charger les données pour cet ETF. Vérifiez votre connexion.")

# ── Comparaison deux ETF ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Comparer deux ETF")

col_a, col_b = st.columns(2)
with col_a:
    etf_a = st.selectbox("ETF A", list(ETF_CATALOG.keys()), index=0, key="comp_a",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_b:
    etf_b = st.selectbox("ETF B", list(ETF_CATALOG.keys()), index=1, key="comp_b",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")

periode_comp = st.selectbox("Période de comparaison", ["1 an", "3 ans", "5 ans", "10 ans"], index=2, key="comp_per")
jours_comp = periode_map[periode_comp]
date_comp = (datetime.today() - timedelta(days=jours_comp)).strftime("%Y-%m-%d")

if st.button("📊 Lancer la comparaison", type="primary"):
    with st.spinner("Chargement des données..."):
        df_a = get_historical_data(ETF_CATALOG[etf_a]["ticker_yf"], date_comp)
        df_b = get_historical_data(ETF_CATALOG[etf_b]["ticker_yf"], date_comp)

    if not df_a.empty and not df_b.empty:
        # Normalisation base 100
        perf_a = (df_a["prix_cloture"] / df_a["prix_cloture"].iloc[0]) * 100
        perf_b = (df_b["prix_cloture"] / df_b["prix_cloture"].iloc[0]) * 100

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(x=perf_a.index, y=perf_a, name=etf_a,
                                       line=dict(color="#3b82f6", width=2)))
        fig_comp.add_trace(go.Scatter(x=perf_b.index, y=perf_b, name=etf_b,
                                       line=dict(color="#f59e0b", width=2)))
        fig_comp.add_hline(y=100, line_dash="dash", line_color="#cbd5e1", line_width=1)
        fig_comp.update_layout(
            title=f"Performance normalisée base 100 — {periode_comp}",
            yaxis_title="Base 100",
            xaxis_title="Date",
            height=380,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="DM Sans"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_comp.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig_comp.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_comp, use_container_width=True)

        # Tableau comparatif
        def stats_etf(df, info, ticker_name):
            perf = (df["prix_cloture"].iloc[-1] / df["prix_cloture"].iloc[0] - 1) * 100
            vol = df["prix_cloture"].pct_change().std() * (252 ** 0.5) * 100
            return {
                "ETF": ticker_name,
                "Nom": info["nom"],
                "TER (%)": f"{info['ter']*100:.2f}%",
                "Performance": f"{perf:+.2f}%",
                "Volatilité ann.": f"{vol:.2f}%",
                "PEA": "✅" if info["pea"] else "❌"
            }

        comp_df = pd.DataFrame([
            stats_etf(df_a, ETF_CATALOG[etf_a], etf_a),
            stats_etf(df_b, ETF_CATALOG[etf_b], etf_b)
        ])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class="info-box">
            La performance normalisée base 100 permet de comparer des ETF avec des prix absolus différents. 
            La volatilité annualisée (écart-type des rendements quotidiens × √252) mesure le risque. 
            Un TER plus bas signifie moins de frais prélevés chaque année.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Impossible de charger les données pour un ou les deux ETF sélectionnés.")
