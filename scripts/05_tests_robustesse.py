"""
Tests de robustesse de la régression event-study :
1. Test de Wald conjoint sur les coefficients pré-traitement (valide ou non
   la tendance parallèle formellement, plutôt qu'un coup d'oeil visuel)
2. Sous-échantillon à appariement serré (distance de pauvreté pré-traitement <= seuil)
3. Hétérogénéité selon l'évolution de population du QPV (test de l'hypothèse
   "fuite des ménages qui s'enrichissent" / mobilité résidentielle)
"""
import pandas as pd
import numpy as np
from scipy import stats
from linearmodels import PanelOLS

from importlib import import_module
reg_mod = import_module('04_regression_event_study')


def test_wald_pretraitement(reg_data, outcome):
    """H0 : les coefficients traite x 2012 ET traite x 2013 sont conjointement
    nuls (référence = 2014 seule). Rejet de H0 = tendance parallèle mise en doute."""
    data = reg_data.dropna(subset=[outcome]).copy()
    annees = sorted(data['annee'].unique())
    for a in annees:
        if a != 2014:
            data[f'traite_x_{a}'] = data['traite'] * (data['annee'] == a).astype(int)
    interaction_cols = [f'traite_x_{a}' for a in annees if a != 2014]
    data_idx = data.set_index(['unit_id', 'annee'])

    mod = PanelOLS(data_idx[outcome], data_idx[interaction_cols],
                    entity_effects=True, time_effects=True)
    res = mod.fit(cov_type='clustered', clusters=data_idx['commune_cluster'])

    params, cov = res.params, res.cov
    idx_2012 = list(params.index).index('traite_x_2012')
    idx_2013 = list(params.index).index('traite_x_2013')
    R = np.zeros((2, len(params)))
    R[0, idx_2012] = 1
    R[1, idx_2013] = 1
    Rb = R @ params.values
    RVR = R @ cov.values @ R.T
    wald_stat = Rb.T @ np.linalg.inv(RVR) @ Rb
    p_value = 1 - stats.chi2.cdf(wald_stat, df=2)
    return {'wald_stat': wald_stat, 'p_value': p_value,
            'conclusion': 'H0 rejetée (tendance parallèle suspecte)' if p_value < 0.05
                          else 'H0 non rejetée (cohérent avec tendance parallèle)'}


def sous_echantillon_appariement_serre(appariement_df, seuil_distance=10):
    """Retourne la liste des codes QPV dont la distance moyenne d'appariement
    (sur la pauvreté pré-traitement) est en dessous du seuil."""
    dist_par_qpv = appariement_df.groupby('code_qpv')['distance_pauvrete'].mean()
    return dist_par_qpv[dist_par_qpv <= seuil_distance].index.tolist()


def test_heterogeneite_evolution_population(reg_data, appariement_df, qpv_evolution_df,
                                              outcome='taux_pauvrete'):
    """Scinde l'échantillon en deux (médiane de l'évolution de population du QPV
    2013-2018) et réestime l'event-study séparément dans chaque groupe.
    Chaque IRIS de contrôle hérite du groupe de SON QPV apparié."""
    mediane = qpv_evolution_df['evol_pop_pct'].median()
    qpv_evolution_df = qpv_evolution_df.copy()
    qpv_evolution_df['groupe_pop'] = qpv_evolution_df['evol_pop_pct'].apply(
        lambda x: 'baisse_forte' if x < mediane else 'stable_hausse')
    qpv_vers_groupe = qpv_evolution_df.set_index('code')['groupe_pop'].to_dict()

    iris_vers_groupe = {}
    for _, row in appariement_df.iterrows():
        if row['code_qpv'] in qpv_vers_groupe:
            iris_vers_groupe[f"IRIS_{row['iris_controle']}"] = qpv_vers_groupe[row['code_qpv']]

    data = reg_data.copy()
    data['groupe_pop'] = data['unit_id'].apply(
        lambda u: qpv_vers_groupe.get(u.replace('QPV_', '')) if u.startswith('QPV_')
        else iris_vers_groupe.get(u))

    resultats = {}
    for groupe in ['baisse_forte', 'stable_hausse']:
        sous = data[data['groupe_pop'] == groupe]
        res, _ = reg_mod.estimer_event_study(sous, outcome, reference='pooled')
        resultats[groupe] = res
    return resultats, mediane


if __name__ == '__main__':
    reg_data = reg_mod.construire_panel_regression(
        'data/processed/appariement_qpv_iris_v2.csv',
        'data/processed/panel_qpv_complet_v2.csv',
        'data/processed/panel_iris_complet_v2.csv',
        'data/processed/qpv_info_nom_commune.csv',
    )
    reg_data_eq = reg_mod.restreindre_panel_equilibre(reg_data)

    print("=== Test de Wald conjoint (pré-traitement) ===")
    for outcome in ['log_revenu', 'taux_pauvrete']:
        print(outcome, ':', test_wald_pretraitement(reg_data_eq, outcome))

    print("\n=== Hétérogénéité selon évolution de population ===")
    appariement = pd.read_csv('data/processed/appariement_qpv_iris_v2.csv')
    qpv_evol = pd.read_csv('data/processed/qpv_evolution_population.csv')
    resultats, mediane = test_heterogeneite_evolution_population(reg_data_eq, appariement, qpv_evol)
    print(f"Médiane évolution population QPV : {mediane:.2f}%")
    for groupe, res in resultats.items():
        print(f"\n--- {groupe} ---")
        print(res.round(4))
