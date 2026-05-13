# Portify — Simulateur de Portefeuille Passif

**M2 MIAGE — Université Paris-Saclay | 2025–2026**

> Application web de simulation et d'analyse de stratégies d'investissement passif, construite avec Streamlit et PostgreSQL.

🌐 **Application déployée** : [portify.streamlit.app](https://projetdata-z3a5fdaxttbgvemfcyogkb.streamlit.app)

---

## Prérequis

- Python 3.11+
- PostgreSQL (local ou Railway)
- Git

---

## Installation locale

### 1. Cloner le repository

```bash
git clone https://github.com/yanis-aggoun2/projet_data.git
cd projet_data
```

### 2. Créer un environnement virtuel

```bash
# Linux / Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créez un fichier `.env` à la racine du projet (en vous basant sur `.env.example`) :

```bash
cp .env.example .env
```

Remplissez les variables dans `.env` :

```dotenv
DATABASE_URL=postgresql://user:password@host:port/database
```

### 5. Initialiser la base de données

Dans pgAdmin ou via psql, exécutez le script SQL suivant :

```sql
CREATE TABLE etf (
    id              SERIAL PRIMARY KEY,
    isin            VARCHAR(12) UNIQUE NOT NULL,
    ticker          VARCHAR(12) UNIQUE NOT NULL,
    nom             VARCHAR(200),
    indice_replique VARCHAR(200),
    gestionnaire    VARCHAR(200),
    ter             NUMERIC(6,4),
    eligible_pea    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(10) DEFAULT 'user',
    created_at    TIMESTAMP DEFAULT NOW(),
    is_active     BOOLEAN DEFAULT TRUE
);
```

### 6. Créer le premier compte admin

```bash
python -c "
import sys
sys.path.append('.')
from utils.auth import create_user
create_user('admin@portify.com', 'VotreMotDePasse', 'admin')
print('Admin créé !')
"
```

### 7. Lancer l'application

```bash
streamlit run main.py
```

L'application est accessible sur : http://localhost:8501


---

## Déploiement

### Streamlit Cloud (CD automatique)

1. Pusher le code sur GitHub sur la branche `main`
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repo GitHub
4. Main file path : `main.py`
5. Dans **Advanced settings → Secrets**, ajouter :

```toml
DATABASE_URL = "postgresql://user:password@host:port/database"
```

6. Cliquer **Deploy** → URL publique disponible en ~2 minutes

Streamlit Cloud redéploie automatiquement à chaque push sur `main`.

### Base de données — Railway

La base PostgreSQL est hébergée sur [Railway](https://railway.app).  
Le proxy public est accessible via `shuttle.proxy.rlwy.net`.

---

## Pipeline CI/CD

Le projet utilise **GitHub Actions** pour l'intégration continue.

À chaque push ou Pull Request sur `main` :

1. Installation de Python 3.11
2. Installation des dépendances (`pip install -r requirements.txt`)
3. Exécution des tests unitaires (`pytest tests/ -v`)

Si les tests échouent → le merge est bloqué.

---

## Lancer les tests

```bash
pytest tests/ -v
```

Tests couverts :
- `test_capital_initial_zero` — simulation avec capital initial = 0
- `test_ter_zero` — simulation sans frais TER
- `test_periode_un_mois` — simulation sur une seule période

---

## Modules

### Module A — Explorateur d'ETF
- Fiche descriptive : nom, ISIN, indice, gestionnaire, TER, éligibilité PEA
- Graphique interactif du cours sur 1, 3, 5 et 10 ans (données yfinance via ISIN)
- Comparaison normalisée base 100 de deux ETF côte à côte

### Module B — Simulateur DCA
- Algorithme DCA mois par mois avec déduction TER mensualisé
- 4 courbes : portefeuille avec TER / sans TER / capital investi / Livret A
- Métriques : CAGR, gain net, frais cumulés, valeur finale
- Tableau détaillé mois par mois

### Module C — Régression Linéaire
- Régression OLS via scikit-learn + scipy + statsmodels
- Métriques : R², β₀, β₁, p-value, intervalles de confiance 95%
- Graphique résidus avec bandes ±2σ
- Test de Durbin-Watson
- Projection 12 mois (illustrative)
- Section d'interprétation critique complète

### Panel Admin
- Gestion des utilisateurs (créer, supprimer, roles)
- Import automatique d'ETFs depuis JustETF (pipeline ETL)
- Gestion manuelle des ETFs (ajouter, supprimer, modifier PEA)

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | Streamlit 1.35+ |
| Données historiques | yfinance (via ISIN) |
| Pipeline ETL | justetf-scraping |
| Modèle statistique | scikit-learn, scipy, statsmodels |
| Base de données | PostgreSQL (Railway) |
| Authentification | bcrypt |
| Graphiques | Plotly |
| Tests | pytest |
| CI/CD | GitHub Actions + Streamlit Cloud |
| Versioning | Git + GitHub |

---

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | URL de connexion PostgreSQL |


---

## Auteurs

Projet réalisé dans le cadre de l'UE **Projet DATA**  
M2 MIAGE — Université Paris-Saclay | 2025–2025 6
