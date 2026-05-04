import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


def run_regression(df_prices: pd.DataFrame) -> dict:
    """
    Régression linéaire OLS : prix_cloture ~ jours_trading

    Variables :
        X : numéro du jour de trading (0, 1, 2, ..., N)
        Y : prix de clôture ajusté

    Returns dict avec tous les résultats analytiques.
    """
    if df_prices.empty or len(df_prices) < 30:
        return {}

    Y = df_prices["prix_cloture"].values.astype(float)
    X = np.arange(len(Y), dtype=float)

    # Régression via scipy (pour p-value)
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
    r2 = r_value ** 2

    # Valeurs prédites
    Y_pred = intercept + slope * X
    residus = Y - Y_pred

    # Intervalle de confiance à 95 % (statsmodels)
    X_sm = sm.add_constant(X)
    model = sm.OLS(Y, X_sm).fit()
    predictions = model.get_prediction(X_sm)
    frame = predictions.summary_frame(alpha=0.05)
    ci_lower = frame["mean_ci_lower"].values
    ci_upper = frame["mean_ci_upper"].values

    # Pente annualisée : on suppose ~252 jours de trading/an
    jours_trading_par_an = 252
    prix_moyen_debut = float(np.mean(Y[:20]))
    pente_annuelle_pct = (slope * jours_trading_par_an / prix_moyen_debut) * 100

    # Test de Durbin-Watson (autocorrélation des résidus)
    dw_stat = durbin_watson(residus)

    # Projection 12 mois futurs
    n = len(X)
    n_proj = jours_trading_par_an
    X_futur = np.arange(n, n + n_proj, dtype=float)
    Y_futur = intercept + slope * X_futur

    X_futur_sm = sm.add_constant(X_futur)
    pred_futur = model.get_prediction(X_futur_sm)
    frame_futur = pred_futur.summary_frame(alpha=0.05)

    return {
        "beta0": intercept,
        "beta1": slope,
        "r2": r2,
        "p_value": p_value,
        "std_err": std_err,
        "pente_eur_jour": slope,
        "pente_annuelle_pct": pente_annuelle_pct,
        "Y": Y,
        "X": X,
        "Y_pred": Y_pred,
        "residus": residus,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "dates": df_prices.index,
        "X_futur": X_futur,
        "Y_futur": Y_futur,
        "ci_futur_lower": frame_futur["mean_ci_lower"].values,
        "ci_futur_upper": frame_futur["mean_ci_upper"].values,
        "dw_stat": dw_stat,
        "n_obs": len(Y),
    }


def durbin_watson(residus: np.ndarray) -> float:
    """Calcul du test de Durbin-Watson pour l'autocorrélation des résidus."""
    diff = np.diff(residus)
    dw = np.sum(diff ** 2) / np.sum(residus ** 2)
    return round(float(dw), 4)


def interprete_dw(dw: float) -> tuple[str, str]:
    """Interprète la statistique de Durbin-Watson."""
    if dw < 1.5:
        return "Autocorrélation positive forte", "warning"
    elif dw > 2.5:
        return "Autocorrélation négative forte", "warning"
    elif 1.5 <= dw <= 2.5:
        return "Pas d'autocorrélation significative", "success"
    return "Indéterminé", "info"


def interprete_r2(r2: float) -> str:
    """Interprétation pédagogique du R²."""
    pct = round(r2 * 100, 1)
    if r2 > 0.85:
        return (
            f"R² = {pct}% — La droite explique {pct}% de la variance du prix. "
            "Ce R² élevé confirme une tendance haussière forte sur longue période. "
            "Attention cependant : sur des séries temporelles croissantes, un R² élevé "
            "est quasi-automatique (régression fallacieuse). Cela ne signifie pas "
            "que le modèle peut prédire les cours futurs."
        )
    elif r2 > 0.6:
        return (
            f"R² = {pct}% — La tendance linéaire explique {pct}% de la variance. "
            "La relation est significative mais des facteurs non-linéaires jouent un rôle important."
        )
    else:
        return (
            f"R² = {pct}% — La tendance linéaire n'explique qu'une faible part de la variance. "
            "L'ETF présente une trajectoire très volatile ou non-linéaire."
        )
