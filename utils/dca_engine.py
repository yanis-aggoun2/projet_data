import pandas as pd
import numpy as np

# contient toute la logique métier du simulateur DCA

# algorithme mois par mois
def run_dca_simulation(df_prices, capital_initial, versement_mensuel, ter_annuel, date_debut, date_fin):
    df = df_prices.loc[date_debut:date_fin].copy()
    if df.empty:
        return pd.DataFrame()

    df["mois"] = df.index.to_period("M")
    premiers_jours = df.groupby("mois").first().reset_index()

    results = []
    parts_cumulees = 0.0
    capital_investi = 0.0
    frais_cumules = 0.0
    ter_mensuel = ter_annuel / 12

    for i, row in premiers_jours.iterrows():
        prix = float(row["prix_cloture"])
        versement = capital_initial + versement_mensuel if i == 0 else versement_mensuel

        parts_achetees = versement / prix
        parts_cumulees += parts_achetees
        capital_investi += versement

        frais_mois = parts_cumulees * prix * ter_mensuel
        frais_cumules += frais_mois
        parts_cumulees *= (1 - ter_mensuel)

        valeur = parts_cumulees * prix

        results.append({
            "date": row["mois"].to_timestamp(),
            "prix": prix,
            "parts_achetees": parts_achetees,
            "parts_cumulees": parts_cumulees,
            "valeur_portefeuille": valeur,
            "capital_investi": capital_investi,
            "frais_cumules": frais_cumules,
        })

    return pd.DataFrame(results)

# simulation sans TER pour comparaison
def run_dca_sans_frais(df_prices, capital_initial, versement_mensuel, date_debut, date_fin):
    return run_dca_simulation(df_prices, capital_initial, versement_mensuel, 0.0, date_debut, date_fin)

# calcul de référence épargne sans risque
def calcul_livret_a(capital_initial, versement_mensuel, taux_annuel, n_mois):
    taux_mensuel = taux_annuel / 12
    valeurs = []
    valeur = capital_initial
    for _ in range(n_mois):
        valeur = (valeur + versement_mensuel) * (1 + taux_mensuel)
        valeurs.append(valeur)
    return valeurs

# CAGR, gain net, frais totaux
def calcul_metriques(df_sim, n_annees):
    if df_sim.empty:
        return {}
    valeur_finale = df_sim["valeur_portefeuille"].iloc[-1]
    capital_total = df_sim["capital_investi"].iloc[-1]
    gain_net = valeur_finale - capital_total
    frais_totaux = df_sim["frais_cumules"].iloc[-1]
    cagr = (valeur_finale / capital_total) ** (1 / n_annees) - 1 if n_annees > 0 else 0
    return {
        "valeur_finale": valeur_finale,
        "capital_total": capital_total,
        "gain_net": gain_net,
        "gain_pct": gain_net / capital_total * 100 if capital_total > 0 else 0,
        "frais_totaux": frais_totaux,
        "cagr": cagr * 100,
    }
