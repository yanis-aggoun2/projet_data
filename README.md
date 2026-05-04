# 📈 Simulateur de Portefeuille Passif

Application Streamlit — M2 MIAGE, Université Paris-Saclay (2024–2025)

## Structure du projet

```
portfolio_passif/
├── app.py                          # Page d'accueil
├── pages/
│   ├── 1_🔍_Explorateur_ETF.py    # Module A
│   ├── 2_📊_Simulateur_DCA.py     # Module B
│   └── 3_📉_Régression_Linéaire.py # Module C
├── data/
│   └── etf_data.py                 # Catalogue ETF + yfinance
├── utils/
│   ├── dca_engine.py               # Algorithme DCA + CAGR
│   └── regression_engine.py        # OLS + Durbin-Watson
├── .streamlit/
│   └── config.toml                 # Thème Streamlit
└── requirements.txt
```

## Installation locale

```bash
# Cloner le repo
git clone <url-du-repo>
cd portfolio_passif

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

## Déploiement Streamlit Cloud

1. Pusher le code sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repo GitHub
4. Sélectionner `app.py` comme point d'entrée
5. Cliquer Deploy → URL publique disponible en ~2 minutes

## ETF disponibles

| Ticker | Nom | TER | PEA |
|--------|-----|-----|-----|
| CW8 | Amundi MSCI World | 0.38% | ✅ |
| PS20 | Amundi S&P 500 | 0.15% | ✅ |
| ESE | iShares MSCI Europe | 0.12% | ❌ |
| OBLI | Lyxor Obligations d'État Euro | 0.17% | ❌ |

## Modules

### Module A — Explorateur d'ETF
- Fiche descriptive complète (nom, indice, gestionnaire, TER, PEA)
- Graphique interactif du cours sur 1/3/5/10 ans
- Comparaison normalisée base 100 de deux ETF

### Module B — Simulateur DCA
- Algorithme DCA mois par mois avec déduction TER mensualisé
- Courbe valeur portefeuille vs capital investi vs Livret A
- Comparaison avec/sans frais TER
- Calcul CAGR, gain net, frais totaux

### Module C — Régression Linéaire
- OLS via scipy/statsmodels
- R², pente β₁, p-value, intervalles de confiance 95%
- Graphique résidus avec bandes ±2σ
- Test de Durbin-Watson
- Projection 12 mois (illustrative)
- Section d'interprétation critique complète
