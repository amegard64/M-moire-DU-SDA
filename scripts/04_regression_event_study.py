"""
Construction du panel de régression (QPV traités + IRIS de contrôle appariés)
et estimation de la régression event-study à effets fixes.

Modèle estimé :
    Y_it = alpha_i + lambda_t + sum_k beta_k * (Traite_i x Annee_k) + epsilon_it

- alpha_i : effet fixe individuel (estimateur *within*, absorbe le niveau propre
  à chaque unité, y compris la variable Traite elle-même puisqu'elle ne varie
  jamais dans le temps pour une unité donnée)
- lambda_t : effet fixe année (absorbe tout ce qui touche également traités et
  contrôles une année donnée)
- beta_k : coefficient d'intérêt, un par année (sauf année(s) de référence)

Deux options de référence :
- reference='2014' : une seule année pré-traitement comme référence
- reference='pooled' : 2012+2013+2014 poolés comme référence (recommandé,
  plus robuste au bruit d'une seule année)

Deux options de panel :
- balanced=False : toutes les unités disponibles chaque année (peut créer un
  effet de composition changeante si le masquage varie par année)
- balanced=True : seulement les unités présentes SANS EXCEPTION sur toutes
  les années (recommandé pour la version finale)
"""
import pandas as pd
import numpy as np
from linearmodels import PanelOLS


def construire_panel_regression(chemin_appariement, chemin_panel_qpv, chemin_panel_iris,
                                  chemin_qpv_info, chemin_logement_social=None):
    """Empile QPV traités et IRIS de contrôle appariés en un panel long,
    avec la variable 'traite' (1/0), le cluster commune, et éventuellement
    le logement social (RPLS) par unité."""
    app = pd.read_csv(chemin_appariement)
    qpv_matches = app['code_qpv'].unique()
    iris_matches = app['iris_controle'].unique()

    qpv_info = pd.read_csv(chemin_qpv_info, dtype={'insee_com': str})
    panel_qpv = pd.read_csv(chemin_panel_qpv)
    panel_iris = pd.read_csv(chemin_panel_iris, dtype={'com': str})

    qpv_panel = panel_qpv[panel_qpv['code'].isin(qpv_matches)].copy()
    qpv_panel = qpv_panel.merge(qpv_info[['code', 'insee_com']], on='code', how='left')
    qpv_panel['unit_id'] = 'QPV_' + qpv_panel['code']
    qpv_panel['traite'] = 1
    qpv_panel['commune_cluster'] = qpv_panel['insee_com']

    iris_panel = panel_iris[panel_iris['iris'].isin(iris_matches)].copy()
    iris_panel['unit_id'] = 'IRIS_' + iris_panel['iris'].astype(str)
    iris_panel['traite'] = 0
    iris_panel['commune_cluster'] = iris_panel['com']

    cols = ['unit_id', 'annee', 'traite', 'commune_cluster', 'revenu_median', 'taux_pauvrete']
    reg_data = pd.concat([qpv_panel[cols], iris_panel[cols]], ignore_index=True)
    reg_data['log_revenu'] = np.log(reg_data['revenu_median'])

    if chemin_logement_social:
        ls = pd.read_csv(chemin_logement_social)  # colonnes attendues : unit_id, nbLsPls
        m, s = ls['nbLsPls'].mean(), ls['nbLsPls'].std()
        ls['ls_z'] = (ls['nbLsPls'] - m) / s
        reg_data = reg_data.merge(ls[['unit_id', 'ls_z']], on='unit_id', how='left')
        reg_data['ls_z'] = reg_data['ls_z'].fillna(0)

    return reg_data


def restreindre_panel_equilibre(reg_data, variable='taux_pauvrete'):
    """Ne garde que les unités présentes sans exception sur toutes les années
    (évite qu'une composition d'échantillon changeante ne crée un faux signal)."""
    pivot = reg_data.pivot_table(index='unit_id', columns='annee', values=variable, aggfunc='first')
    unites_completes = pivot[pivot.notna().all(axis=1)].index
    return reg_data[reg_data['unit_id'].isin(unites_completes)].copy()


def estimer_event_study(reg_data, outcome, reference='pooled', avec_logement_social=False):
    """Estime le modèle event-study et retourne les résultats (coef, se, p-value)
    pour chaque interaction traite x annee.

    reference='2014' : garde 2012 et 2013 comme coefficients estimés (référence = 2014 seule)
    reference='pooled' : omet 2012 et 2013 (référence = leur moyenne implicite)
    """
    data = reg_data.dropna(subset=[outcome]).copy()
    annees = sorted(data['annee'].unique())

    if reference == 'pooled':
        annees_interaction = [a for a in annees if a not in (2012, 2013, 2014)]
    else:
        annees_interaction = [a for a in annees if a != 2014]

    interaction_cols = []
    for a in annees_interaction:
        col = f'traite_x_{a}'
        data[col] = data['traite'] * (data['annee'] == a).astype(int)
        interaction_cols.append(col)

    if avec_logement_social:
        for a in annees_interaction:
            col = f'logsoc_x_{a}'
            data[col] = data['ls_z'] * (data['annee'] == a).astype(int)
            interaction_cols.append(col)

    data_idx = data.set_index(['unit_id', 'annee'])
    mod = PanelOLS(data_idx[outcome], data_idx[interaction_cols],
                    entity_effects=True, time_effects=True)
    res = mod.fit(cov_type='clustered', clusters=data_idx['commune_cluster'])

    cols_traite = [c for c in interaction_cols if c.startswith('traite_x_')]
    ci = res.conf_int()
    resultat = pd.DataFrame({
        'coef': res.params[cols_traite],
        'se': res.std_errors[cols_traite],
        'p_value': res.pvalues[cols_traite],
        'ci_low': ci.loc[cols_traite, 'lower'],
        'ci_high': ci.loc[cols_traite, 'upper'],
    })
    return resultat, res


if __name__ == '__main__':
    reg_data = construire_panel_regression(
        'data/processed/appariement_qpv_iris_v2.csv',
        'data/processed/panel_qpv_complet_v2.csv',
        'data/processed/panel_iris_complet_v2.csv',
        'data/processed/qpv_info_nom_commune.csv',
    )
    reg_data_equilibre = restreindre_panel_equilibre(reg_data)

    for outcome in ['log_revenu', 'taux_pauvrete']:
        resultat, _ = estimer_event_study(reg_data_equilibre, outcome, reference='pooled')
        print(f"\n=== {outcome} (panel équilibré, référence poolée 2012-2014) ===")
        print(resultat.round(4))
