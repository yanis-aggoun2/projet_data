import pandas as pd
import numpy as np
from datetime import datetime


def run_dca_simulation(
    df_prices: pd.DataFrame,
    capital_initial: float,
    versement_mensuel: float,
    ter_annuel: float,
    date_debut: str,
    date_fin: str
) -> pd.DataFrame:
    """
    Simule une stratégie DCA mois par mois.

    Algorithme :
    1. Récupérer le prix du premier jour de trading du mois
    2. Calculer parts achetées = versement / prix
    3. Ajouter parts au cumul
    4. Déduire TER mensualisé
    5. Calculer valeur totale = parts × prix

    Returns DataFrame avec colonnes :
        date, prix, parts_achetees, parts_cumulees,
        valeur_portefeuille, capital_investi, frais_cumules
    """
    df = df_prices.loc[date_debut:date_fin].copy()
    if df.empty:
        return pd.DataFrame()

    # Premier jour de chaque mois
    df["annee_mois"] = df.index.to_period("M")
    premiers_jours = df.groupby("annee_mois").first().reset_index()
    premiers_jours["date"] = premiers_jours["annee_mois"].dt.to_timestamp()

    results = []
    parts_cumulees = 0.0
    capital_investi = 0.0
    frais_cumules = 0.0
    ter_mensuel = ter_annuel / 12

    for i, row in premiers_jours.iterrows():
        prix = float(row["prix_cloture"])

        # Mois 0 : capital initial + premier versement
        if i == 0:
            versement = capital_initial + versement_mensuel
        else:
            versement = versement_mensuel

        # Achat de parts
        parts_achetees = versement / prix
        parts_cumulees += parts_achetees
        capital_investi += versement

        # Valeur avant frais
        valeur_avant_frais = parts_cumulees * prix

        # Déduction frais TER mensualisé
        frais_mois = valeur_avant_frais * ter_mensuel
        frais_cumules += frais_mois

        # Ajustement des parts pour simuler l'effet du TER
        facteur_ter = 1 - ter_mensuel
        parts_cumulees *= facteur_ter

        valeur_portefeuille = parts_cumulees * prix

        results.append({
            "date": row["date"],
            "prix": prix,
            "parts_achetees": parts_achetees,
            "parts_cumulees": parts_cumulees,
            "valeur_portefeuille": valeur_portefeuille,
            "capital_investi": capital_investi,
            "frais_cumules": frais_cumules,
        })

    return pd.DataFrame(results)


def run_dca_sans_frais(
    df_prices: pd.DataFrame,
    capital_initial: float,
    versement_mensuel: float,
    date_debut: str,
    date_fin: str
) -> pd.DataFrame:
    """Même simulation mais sans TER (pour comparaison)."""
    return run_dca_simulation(
        df_prices, capital_initial, versement_mensuel,
        0.0, date_debut, date_fin
    )


def calcul_livret_a(
    capital_initial: float,
    versement_mensuel: float,
    taux_annuel: float,
    n_mois: int
) -> pd.Series:
    """
    Calcule l'évolution d'un Livret A avec versements mensuels.
    Taux mensuel = taux_annuel / 12 (capitalisation mensuelle simplifiée).
    """
    taux_mensuel = taux_annuel / 12
    valeurs = []
    valeur = capital_initial
    for m in range(n_mois):
        valeur = (valeur + versement_mensuel) * (1 + taux_mensuel)
        valeurs.append(valeur)
    return pd.Series(valeurs)


def calcul_cagr(valeur_finale: float, capital_total: float, n_annees: float) -> float:
    """Calcul du CAGR (rendement annualisé composé)."""
    if capital_total <= 0 or n_annees <= 0:
        return 0.0
    return (valeur_finale / capital_total) ** (1 / n_annees) - 1


def calcul_metriques(df_sim: pd.DataFrame, n_annees: float) -> dict:
    """Calcule les métriques clés d'une simulation DCA."""
    if df_sim.empty:
        return {}
    valeur_finale = df_sim["valeur_portefeuille"].iloc[-1]
    capital_total = df_sim["capital_investi"].iloc[-1]
    gain_net = valeur_finale - capital_total
    frais_totaux = df_sim["frais_cumules"].iloc[-1]
    cagr = calcul_cagr(valeur_finale, capital_total, n_annees)
    return {
        "valeur_finale": valeur_finale,
        "capital_total": capital_total,
        "gain_net": gain_net,
        "gain_pct": (gain_net / capital_total * 100) if capital_total > 0 else 0,
        "frais_totaux": frais_totaux,
        "cagr": cagr * 100,
    }
