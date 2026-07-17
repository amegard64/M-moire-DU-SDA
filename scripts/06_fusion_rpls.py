"""
Ajout du contrôle logement social (RPLS 2022) au panel de régression, et
construction des interactions traité×année et logement_social×année pour
la régression event-study (voir carnet sections 24-25).

Étapes :
1. Repartir de panel_regression.csv et retirer les lignes sans taux de
   pauvreté observé (secret statistique) — la variable dépendante doit
   être non manquante pour qu'une ligne soit utilisable en régression.
2. Fusionner nbLsPls (nombre de logements sociaux) depuis les fichiers
   RPLS nettoyés (qpv_rpls_clean.csv / iris_rpls_clean.csv), sur le code
   QPV ou le code IRIS selon le type d'unité.
3. Standardiser (z-score) sur l'ensemble du panel fusionné ; les quelques
   unités sans donnée RPLS (hors du champ RPLS, ou disparues entre le
   millésime RPLS 2022 et le panel) reçoivent logement_social_z = 0
   (imputation à la moyenne) plutôt que d'être exclues de la régression.
   **Limite à documenter** : cette imputation à 0 traite l'absence de
   donnée RPLS comme "logement social dans la moyenne", ce qui n'est
   qu'une approximation commode pour ne pas perdre ces observations.
4. Construire les indicatrices traite×année et logement_social_z×année
   pour chaque année sauf 2014 (année de référence omise).

Entrées : data/processed/{panel_regression,qpv_rpls_clean,iris_rpls_clean}.csv
Sortie : data/processed/panel_regression_v2.csv
"""
import pandas as pd

ANNEES_INTERACTION = [2012, 2013, 2016, 2017, 2018, 2019, 2021]  # 2014 = référence


def fusionner_rpls(dossier='data/processed'):
    panel = pd.read_csv(f'{dossier}/panel_regression.csv', dtype={'commune_cluster': str})
    panel = panel[panel['taux_pauvrete'].notna()].copy()

    qpv_rpls = pd.read_csv(f'{dossier}/qpv_rpls_clean.csv', dtype={'CodGeo': str})[['CodGeo', 'nbLsPls']]
    iris_rpls = pd.read_csv(f'{dossier}/iris_rpls_clean.csv', dtype={'CodGeo': str})[['CodGeo', 'nbLsPls']]
    rpls = pd.concat([qpv_rpls, iris_rpls], ignore_index=True).rename(
        columns={'CodGeo': 'code', 'nbLsPls': 'logement_social'})

    panel['code'] = panel['unit_id'].str.replace(r'^(QPV_|IRIS_)', '', regex=True)
    panel = panel.merge(rpls, on='code', how='left').drop(columns='code')

    mean = panel['logement_social'].mean()
    std = panel['logement_social'].std()
    panel['logement_social_z'] = ((panel['logement_social'] - mean) / std).fillna(0.0)

    for annee in ANNEES_INTERACTION:
        est_annee = (panel['annee'] == annee).astype(int)
        panel[f'traite_x_{annee}'] = panel['traite'] * est_annee
        panel[f'logsoc_x_{annee}'] = panel['logement_social_z'] * est_annee

    return panel


if __name__ == '__main__':
    panel = fusionner_rpls()
    panel.to_csv('data/processed/panel_regression_v2.csv', index=False)
    print(f"Panel de régression v2 : {len(panel)} lignes, "
          f"{panel['logement_social'].isna().sum()} sans donnée RPLS (imputées à 0 après standardisation)")
