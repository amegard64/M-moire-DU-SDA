"""
Régression event-study : effets fixes unité + année, interaction
traité×année (2014 = année de référence omise), erreurs standard
clusterisées au niveau commune (voir carnet sections 19, 22, 25).

Deux spécifications :
- Modèle de base (panel_regression.csv) : traité×année seul.
- Modèle avec contrôle logement social (panel_regression_v2.csv) :
  ajoute logement_social_z×année en plus de traité×année (voir carnet
  section 25 — le logement social explique une partie du signal mais pas
  la totalité).

Produit aussi les moyennes agrégées QPV vs contrôle par année (lecture
descriptive complémentaire, ne remplace pas la régression — voir carnet
section 19).

Entrées : data/processed/{panel_regression,panel_regression_v2}.csv
Sorties : data/processed/event_study_resultats.json
          data/processed/event_study_resultats_v2.json
          data/processed/tendance_complete_2012_2021.csv
"""
import json

import pandas as pd
from linearmodels.panel import PanelOLS

ANNEE_REFERENCE = 2014
ANNEES_INTERACTION = [2012, 2013, 2016, 2017, 2018, 2019, 2021]


def estimer_event_study(panel, outcome, colonnes_traite, colonnes_controle=None):
    """Régression à effets fixes unité+année, erreurs clusterisées par commune.
    Retourne la liste [{annee, coef, ci_low, ci_high}] incluant l'année de
    référence (coefficient normalisé à 0 par construction)."""
    colonnes_controle = colonnes_controle or []
    p = panel.set_index(['unit_id', 'annee'])
    exog = p[colonnes_traite + colonnes_controle]
    modele = PanelOLS(p[outcome], exog, entity_effects=True, time_effects=True)
    res = modele.fit(cov_type='clustered', clusters=p['commune_cluster'])

    ci = res.conf_int()
    resultats = [{'annee': ANNEE_REFERENCE, 'coef': 0.0, 'ci_low': 0.0, 'ci_high': 0.0}]
    for annee, col in zip(ANNEES_INTERACTION, colonnes_traite):
        resultats.append({
            'annee': annee,
            'coef': float(res.params[col]),
            'ci_low': float(ci.loc[col, 'lower']),
            'ci_high': float(ci.loc[col, 'upper']),
        })
    return sorted(resultats, key=lambda r: r['annee'])


def construire_tendance(panel):
    g = panel.groupby(['annee', 'traite']).agg(
        revenu_median=('revenu_median', 'mean'),
        taux_pauvrete=('taux_pauvrete', 'mean')).reset_index()
    piv = g.pivot(index='annee', columns='traite')
    piv.columns = ['revenu_median_controle', 'revenu_median_qpv',
                   'taux_pauvrete_controle', 'taux_pauvrete_qpv']
    return piv.reset_index()[['annee', 'revenu_median_qpv', 'taux_pauvrete_qpv',
                               'revenu_median_controle', 'taux_pauvrete_controle']]


if __name__ == '__main__':
    dossier = 'data/processed'
    traite_cols = [f'traite_x_{a}' for a in ANNEES_INTERACTION]
    logsoc_cols = [f'logsoc_x_{a}' for a in ANNEES_INTERACTION]

    panel_brut = pd.read_csv(f'{dossier}/panel_regression.csv', dtype={'commune_cluster': str})

    # Régression : restreinte aux lignes avec taux de pauvreté observé
    # (secret statistique), pour que les deux régressions (revenu,
    # pauvreté) portent sur le même échantillon.
    panel = panel_brut[panel_brut['taux_pauvrete'].notna()].copy()
    for a in ANNEES_INTERACTION:
        panel[f'traite_x_{a}'] = panel['traite'] * (panel['annee'] == a).astype(int)
    resultats = {
        'revenu': estimer_event_study(panel, 'log_revenu', traite_cols),
        'pauvrete': estimer_event_study(panel, 'taux_pauvrete', traite_cols),
    }
    with open(f'{dossier}/event_study_resultats.json', 'w') as f:
        json.dump(resultats, f)

    # Modèle avec contrôle logement social
    panel_v2 = pd.read_csv(f'{dossier}/panel_regression_v2.csv', dtype={'commune_cluster': str})
    resultats_v2 = {
        'revenu': estimer_event_study(panel_v2, 'log_revenu', traite_cols, logsoc_cols),
        'pauvrete': estimer_event_study(panel_v2, 'taux_pauvrete', traite_cols, logsoc_cols),
    }
    with open(f'{dossier}/event_study_resultats_v2.json', 'w') as f:
        json.dump(resultats_v2, f)

    # Tendances descriptives (moyennes brutes QPV vs contrôle, échantillon
    # complet non restreint à la pauvreté observée, cf. carnet section 19)
    tendance = construire_tendance(panel_brut)
    tendance.to_csv(f'{dossier}/tendance_complete_2012_2021.csv', index=False)

    print("Modèle de base (pauvreté) :")
    for r in resultats['pauvrete']:
        print(f"  {r['annee']}: {r['coef']:+.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]")
    print("Modèle avec logement social (pauvreté) :")
    for r in resultats_v2['pauvrete']:
        print(f"  {r['annee']}: {r['coef']:+.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]")
