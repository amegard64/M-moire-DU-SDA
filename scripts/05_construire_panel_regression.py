"""
Assemblage du panel de régression (event-study) à partir des panels QPV et
IRIS complets (2012-2014, 2016-2019, 2021 — 2015 et 2020 exclus, voir carnet
section 19) et du groupe de contrôle apparié (04_appariement_qpv_iris.py).

Structure longue à deux types d'unités :
- QPV (traite=1) : uniquement les QPV effectivement appariés à au moins un
  IRIS de contrôle (sinon pas de comparaison possible dans la régression).
- IRIS de contrôle (traite=0) : chaque IRIS retenu une seule fois, même
  s'il sert de contrôle à plusieurs QPV (pas de duplication de ligne).

`commune_cluster` (code commune) sert de niveau de clustering des erreurs
standard dans la régression event-study — la même commune peut contenir un
QPV et plusieurs IRIS de contrôle, ou plusieurs IRIS de contrôle liés à des
QPV de communes différentes (repli unité urbaine).

Entrées : data/processed/{panel_qpv_complet,panel_iris_complet,
qpv_info_nom_commune,appariement_qpv_iris_v2}.csv
Sortie : data/processed/panel_regression.csv
"""
import numpy as np
import pandas as pd


def construire_panel_regression(dossier='data/processed'):
    panel_qpv = pd.read_csv(f'{dossier}/panel_qpv_complet.csv', dtype={'code': str})
    panel_iris = pd.read_csv(f'{dossier}/panel_iris_complet.csv', dtype={'iris': str, 'com': str})
    qpv_info = pd.read_csv(f'{dossier}/qpv_info_nom_commune.csv', dtype={'code': str, 'insee_com': str})
    appariement = pd.read_csv(f'{dossier}/appariement_qpv_iris_v2.csv',
                               dtype={'code_qpv': str, 'iris_controle': str})

    qpv_apparies = set(appariement['code_qpv'])
    iris_controle = set(appariement['iris_controle'])

    qpv_long = panel_qpv[panel_qpv['code'].isin(qpv_apparies)].merge(
        qpv_info[['code', 'insee_com']], on='code', how='left')
    qpv_long = qpv_long.rename(columns={'code': 'unit_id_raw', 'insee_com': 'commune_cluster'})
    qpv_long['unit_id'] = 'QPV_' + qpv_long['unit_id_raw']
    qpv_long['traite'] = 1

    iris_long = panel_iris[panel_iris['iris'].isin(iris_controle)].rename(
        columns={'iris': 'unit_id_raw', 'com': 'commune_cluster'})
    iris_long['unit_id'] = 'IRIS_' + iris_long['unit_id_raw']
    iris_long['traite'] = 0

    cols = ['unit_id', 'annee', 'traite', 'commune_cluster', 'revenu_median', 'taux_pauvrete']
    panel = pd.concat([qpv_long[cols], iris_long[cols]], ignore_index=True)
    panel['log_revenu'] = np.log(panel['revenu_median'])
    return panel


if __name__ == '__main__':
    panel = construire_panel_regression()
    panel.to_csv('data/processed/panel_regression.csv', index=False)
    print(f"Panel de régression : {len(panel)} lignes, "
          f"{panel[panel['traite'] == 1]['unit_id'].nunique()} QPV, "
          f"{panel[panel['traite'] == 0]['unit_id'].nunique()} IRIS de contrôle")
