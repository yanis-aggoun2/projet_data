import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data
from utils.regression_engine import (
    run_regression, interprete_r2, interprete_dw, durbin_watson
)

st.set_page_config(page_title="Régression Linéaire", page_icon="📉", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
.result-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1.3rem 1.5rem; margin-bottom: 1rem;
}
.info-box { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #1e3a8a; margin: 1rem 0; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #78350f; margin: 1rem 0; }
.danger-box { background: #fef2f2; border-left: 4px solid #ef4444; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #991b1b; margin: 1rem 0; }
.success-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #15803d; margin: 1rem 0; }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin: 1rem 0; }
.stat-item { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem; text-align: center; }
.stat-item .lbl { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.stat-item .val { font-size: 1.5rem; font-weight: 700; color: #0f172a; font-family: 'DM Serif Display', serif; margin-top: 0.2rem; }
.interp-section { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.8rem; margin-top: 1.5rem; }
.interp-section h3 { font-family: 'DM Serif Display', serif; font-size: 1.3rem; margin-bottom: 1rem; }
.interp-point { display: flex; align-items: flex-start; gap: 0.8rem; margin-bottom: 1rem; padding: 0.8rem 1rem; border-radius: 8px; background: #f8fafc; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📉 Régression Linéaire & Analyse de Tendance")
st.markdown("Modélisez la tendance long terme d'un ETF et comprenez les limites de la prédiction financière.")

# ── Configuration ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    ticker = st.selectbox(
        "ETF à analyser",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    fenetre = st.slider("Fenêtre d'analyse (années)", min_value=3, max_value=15, value=10)
    afficher_projection = st.checkbox("Afficher la projection 12 mois", value=True)
    lancer = st.button("📈 Lancer la régression", type="primary", use_container_width=True)

etf = ETF_CATALOG[ticker]

if lancer:
    date_debut = (datetime.today() - timedelta(days=fenetre * 365)).strftime("%Y-%m-%d")

    with st.spinner("Téléchargement et calcul de la régression..."):
        df_prix = get_historical_data(etf["ticker_yf"], date_debut)

    if df_prix.empty or len(df_prix) < 60:
        st.error("Données insuffisantes pour effectuer la régression.")
        st.stop()

    res = run_regression(df_prix)
    if not res:
        st.error("Erreur lors du calcul de la régression.")
        st.stop()

    # ── Tableau de synthèse ─────────────────────────────────────────────────
    st.markdown("### Métriques de la régression")

    p_value_fmt = f"{res['p_value']:.2e}" if res['p_value'] < 0.001 else f"{res['p_value']:.4f}"
    sig_label = "✅ Très significatif (p < 0.001)" if res['p_value'] < 0.001 else ("⚠️ Significatif" if res['p_value'] < 0.05 else "❌ Non significatif")

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-item">
            <div class="lbl">R²</div>
            <div class="val">{res['r2']:.4f}</div>
        </div>
        <div class="stat-item">
            <div class="lbl">Pente β₁ (€/jour)</div>
            <div class="val">{res['beta1']:+.4f}</div>
        </div>
        <div class="stat-item">
            <div class="lbl">Pente annualisée</div>
            <div class="val">{res['pente_annuelle_pct']:+.2f}%</div>
        </div>
        <div class="stat-item">
            <div class="lbl">P-value</div>
            <div class="val" style="font-size:1rem;">{p_value_fmt}</div>
        </div>
        <div class="stat-item">
            <div class="lbl">Durbin-Watson</div>
            <div class="val">{res['dw_stat']:.4f}</div>
        </div>
        <div class="stat-item">
            <div class="lbl">Observations</div>
            <div class="val">{res['n_obs']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"Significativité de la pente : {sig_label}")

    # ── Graphique 1 : cours + droite + IC ──────────────────────────────────
    st.markdown("### Cours historique avec droite de régression")

    dates = pd.to_datetime(res["dates"])
    fig1 = go.Figure()

    # Bande de confiance 95%
    fig1.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(res["ci_upper"]) + list(res["ci_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(148,163,184,0.2)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Intervalle confiance 95%",
        showlegend=True
    ))

    # Cours réel
    fig1.add_trace(go.Scatter(
        x=dates, y=res["Y"],
        name="Cours réel",
        line=dict(color="#3b82f6", width=1.5),
        opacity=0.8
    ))

    # Droite de régression
    fig1.add_trace(go.Scatter(
        x=dates, y=res["Y_pred"],
        name="Droite de régression OLS",
        line=dict(color="#f97316", width=2.5)
    ))

    # Projection 12 mois
    if afficher_projection:
        last_date = dates[-1]
        dates_proj = pd.date_range(start=last_date, periods=len(res["X_futur"]) + 1, freq="B")[1:]
        n_proj = min(len(dates_proj), len(res["Y_futur"]))

        fig1.add_trace(go.Scatter(
            x=list(dates_proj[:n_proj]) + list(dates_proj[:n_proj][::-1]),
            y=list(res["ci_futur_upper"][:n_proj]) + list(res["ci_futur_lower"][:n_proj][::-1]),
            fill="toself",
            fillcolor="rgba(249,115,22,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="IC 95% projection",
            showlegend=True
        ))
        fig1.add_trace(go.Scatter(
            x=dates_proj[:n_proj], y=res["Y_futur"][:n_proj],
            name="Projection 12 mois (illustratif)",
            line=dict(color="#f97316", width=2, dash="dash"),
        ))
        fig1.add_vline(x=str(last_date.date()), line_dash="dot",
                       line_color="#94a3b8", line_width=1,
                       annotation_text="Aujourd'hui", annotation_position="top right")

    fig1.update_layout(
        height=480, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans"), hovermode="x unified",
        yaxis_title="Prix de clôture (€)", xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig1.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig1.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig1, use_container_width=True)

    if afficher_projection:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ À propos de la projection</strong> — La droite en pointillés est une extrapolation 
            mécanique de la régression. L'intervalle de confiance s'élargit dans le futur : 
            la prédiction est de moins en moins fiable. Cette projection est illustrative uniquement.
        </div>
        """, unsafe_allow_html=True)

    # ── Graphique 2 : résidus ───────────────────────────────────────────────
    st.markdown("### Graphique des résidus")

    fig2 = go.Figure()
    fig2.add_hline(y=0, line_color="#e2e8f0", line_width=1.5)
    fig2.add_trace(go.Scatter(
        x=dates, y=res["residus"],
        name="Résidus",
        line=dict(color="#8b5cf6", width=1.2),
        opacity=0.9
    ))
    fig2.add_trace(go.Scatter(
        x=dates, y=[np.std(res["residus"]) * 2] * len(dates),
        name="+2σ", line=dict(color="#f87171", width=1, dash="dot"), opacity=0.6
    ))
    fig2.add_trace(go.Scatter(
        x=dates, y=[-np.std(res["residus"]) * 2] * len(dates),
        name="-2σ", line=dict(color="#f87171", width=1, dash="dot"), opacity=0.6
    ))
    fig2.update_layout(
        height=320, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans"), hovermode="x unified",
        yaxis_title="Résidu (€)", xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    fig2.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig2.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig2, use_container_width=True)

    # ── Interprétation critique ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧠 Interprétation critique")

    dw_label, dw_type = interprete_dw(res["dw_stat"])
    r2_interp = interprete_r2(res["r2"])

    st.markdown(f"""
    <div class="interp-section">
        <h3>Analyse des résultats — {ticker} sur {fenetre} ans</h3>

        <div class="interp-point">
            <div style="font-size:1.3rem;">📐</div>
            <div>
                <strong>R² = {res['r2']:.4f} — Que signifie vraiment ce chiffre ?</strong><br>
                <span style="color:#475569;">{r2_interp}</span>
            </div>
        </div>

        <div class="interp-point">
            <div style="font-size:1.3rem;">📉</div>
            <div>
                <strong>Les résidus ne sont pas aléatoires</strong><br>
                <span style="color:#475569;">
                Le graphique des résidus montre des cycles, des crises (résidus très négatifs) et 
                des bulles (résidus très positifs). Ces patterns sont la signature d'un marché 
                <em>efficient mais non-prédictible à court terme</em> : les prix intègrent rapidement 
                toute l'information disponible.
                </span>
            </div>
        </div>

        <div class="interp-point">
            <div style="font-size:1.3rem;">📏</div>
            <div>
                <strong>Test de Durbin-Watson : {res['dw_stat']:.4f} — {dw_label}</strong><br>
                <span style="color:#475569;">
                La statistique DW mesure l'autocorrélation des résidus (entre 0 et 4, idéal ≈ 2). 
                Une valeur proche de 2 indique l'absence d'autocorrélation — les résidus successifs 
                sont indépendants. Une valeur éloignée de 2 révèle des patterns persistants dans les erreurs.
                </span>
            </div>
        </div>

        <div class="interp-point">
            <div style="font-size:1.3rem;">⚠️</div>
            <div>
                <strong>Attention : régression fallacieuse (spurious regression)</strong><br>
                <span style="color:#475569;">
                Sur des séries temporelles croissantes, un R² élevé est quasi-automatique même sans 
                relation causale (Granger & Newbold, 1974). Le fait que le temps <em>explique</em> 
                le prix ne signifie pas que vous pouvez prévoir les cours futurs. Ce modèle confirme 
                une <strong>tendance</strong>, pas un <strong>timing</strong>.
                </span>
            </div>
        </div>

        <div class="interp-point">
            <div style="font-size:1.3rem;">✅</div>
            <div>
                <strong>Conclusion : pourquoi le DCA est rationnel</strong><br>
                <span style="color:#475569;">
                La régression confirme une tendance haussière statistiquement significative 
                (pente = <strong>{res['beta1']:+.4f} €/jour</strong>, soit <strong>{res['pente_annuelle_pct']:+.2f}%/an</strong> annualisé). 
                Mais les résidus montrent que le marché est imprévisible à court terme. 
                C'est précisément pourquoi le DCA — investir régulièrement plutôt que chercher 
                le "bon moment" — est une stratégie plus rationnelle que le market timing.
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tableau synthèse ────────────────────────────────────────────────────
    with st.expander("📋 Tableau de synthèse complet"):
        summary_data = {
            "Indicateur": ["R²", "β₀ (ordonnée à l'origine)", "β₁ (pente €/jour)",
                           "Pente annualisée (%/an)", "P-value sur β₁", "Durbin-Watson",
                           "Observations", "Fenêtre d'analyse"],
            "Valeur": [
                f"{res['r2']:.6f}",
                f"{res['beta0']:.4f} €",
                f"{res['beta1']:+.6f} €/jour",
                f"{res['pente_annuelle_pct']:+.2f}%/an",
                p_value_fmt,
                f"{res['dw_stat']:.4f}",
                str(res['n_obs']),
                f"{fenetre} ans"
            ],
            "Interprétation": [
                "Part de variance expliquée par le temps",
                "Prix théorique au jour 0",
                "Hausse moyenne quotidienne",
                "Rendement tendanciel annualisé",
                sig_label,
                dw_label,
                "Jours de trading inclus",
                "Données utilisées"
            ]
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #94a3b8;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📉</div>
        <div style="font-size: 1.1rem; font-weight: 500; color: #64748b;">
            Sélectionnez un ETF et une fenêtre d'analyse dans le panneau latéral,<br>
            puis cliquez sur <strong>Lancer la régression</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)
