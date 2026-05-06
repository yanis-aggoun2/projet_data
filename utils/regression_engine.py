import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression  # ← ajouter
# contient toute la logique statistique

#  calcul OLS complet
def run_regression(df_prices):
    if df_prices.empty or len(df_prices) < 30:
        return {}

    Y = df_prices["prix_cloture"].values.astype(float)
    X = np.arange(len(Y), dtype=float)

    # ── sklearn ──────────────────────────────
    model_sk = LinearRegression()
    model_sk.fit(X.reshape(-1, 1), Y)
    beta1_sk = float(model_sk.coef_[0])
    beta0_sk = float(model_sk.intercept_)
    r2_sk    = model_sk.score(X.reshape(-1, 1), Y)

    # ── scipy (pour la p-value) ──────────────────────────────────
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)

    # ── Valeurs prédites et résidus ──────────────────────────────
    Y_pred = intercept + slope * X
    residus = Y - Y_pred

    # ── statsmodels (pour les intervalles de confiance) ──────────
    X_sm  = sm.add_constant(X)
    model_sm = sm.OLS(Y, X_sm).fit()
    frame = model_sm.get_prediction(X_sm).summary_frame(alpha=0.05)

    prix_moyen_debut   = float(np.mean(Y[:20]))
    pente_annuelle_pct = (slope * 252 / prix_moyen_debut) * 100

    diff    = np.diff(residus)
    dw_stat = round(float(np.sum(diff ** 2) / np.sum(residus ** 2)), 4)

    n       = len(X)
    X_futur = np.arange(n, n + 252, dtype=float)
    Y_futur = intercept + slope * X_futur
    frame_futur = model_sm.get_prediction(
        sm.add_constant(X_futur)
    ).summary_frame(alpha=0.05)

    return {
        "beta0":    beta0_sk,
        "beta1":    beta1_sk,
        "r2":       r2_sk,
        "p_value":  p_value,
        "pente_annuelle_pct": pente_annuelle_pct,
        "Y":        Y,
        "X":        X,
        "Y_pred":   Y_pred,
        "residus":  residus,
        "ci_lower": frame["mean_ci_lower"].values,
        "ci_upper": frame["mean_ci_upper"].values,
        "dates":         df_prices.index,
        "X_futur":       X_futur,
        "Y_futur":       Y_futur,
        "ci_futur_lower": frame_futur["mean_ci_lower"].values,
        "ci_futur_upper": frame_futur["mean_ci_upper"].values,
        # Durbin-Watson
        "dw_stat": dw_stat,
        "n_obs":   len(Y),
    }