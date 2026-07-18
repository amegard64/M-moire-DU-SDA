"""
Chantier 3 (brief limites/robustesse) : remplacer le contrôle logement social
en nombre absolu (nbLsPls, section 25/33 du carnet) par une vraie proportion
(logements sociaux / total des logements).

Dénominateurs utilisés :
- IRIS de contrôle : total logements 2022 (P22_LOG, source INSEE "IRIS -
  Logement - 2022", data/raw/IRIS - Logement - 2022.zip) — dénominateur réel,
  cohérent en type et en millésime avec le RPLS 2022 déjà utilisé.
- QPV : AUCUN produit "total logements" n'existe en géographie QPV2015
  (vérifié directement sur insee.fr/fr/statistiques/8647012 : IRIS uniquement).
  Dénominateur de repli retenu avec Alexandre : population QPV 2018 (aucune
  donnée de population QPV plus récente n'existe en géographie QPV2015 —
  vérifié également, l'INSEE redirige vers la géographie QPV2024 au-delà
  de 2018, incompatible avec le zonage QPV2015 utilisé dans tout le mémoire).

Limite structurelle assumée : le numérateur (nbLsPls) est comparable des deux
côtés, mais le DÉNOMINATEUR ne mesure pas le même concept selon le groupe
(logements côté IRIS, population côté QPV) — les deux proportions ne sont
pas strictement comparables. Une vérification de cohérence (même dénominateur
population des deux côtés) est fournie pour objectiver ce point (cf. carnet
section 42) plutôt que de présenter la comparaison brute sans recul.
"""
import pandas as pd
import numpy as np
import zipfile

from importlib import import_module
reg_mod = import_module('04_regression_event_study')
bal_mod = import_module('06_balayage_demographie')


def charger_logement_total_iris(chemin_zip, chemin_extraction):
    """Extrait et charge le total de logements 2022 par IRIS (P22_LOG).
    Le module zipfile de Python lève une erreur CRC-32 sur ce fichier précis
    alors que `unzip` en ligne de commande le lit sans problème — extraction
    donc faite via un appel système plutôt que zipfile."""
    import subprocess
    subprocess.run(['unzip', '-o', '-q', chemin_zip, '-d', chemin_extraction], check=True)
    chemin_xlsx = f'{chemin_extraction}/base-ic-logement-2022.xlsx'
    df = pd.read_excel(chemin_xlsx, sheet_name='IRIS', header=5)
    df['IRIS'] = df['IRIS'].astype(str)
    return df.set_index('IRIS')['P22_LOG']


def construire_proportion_z(chemin_rpls_qpv, chemin_rpls_iris, denom_qpv, denom_iris):
    """Construit nbLsPls / dénominateur pour QPV et IRIS avec des séries de
    dénominateur différentes selon le côté (denom_qpv, denom_iris indexées
    par code), standardise sur les valeurs finies uniquement (un dénominateur
    nul dans le fichier source produit une proportion infinie à exclure du
    calcul de moyenne/écart-type, pas seulement des NaN)."""
    rpls_qpv = pd.read_csv(chemin_rpls_qpv, dtype={'CodGeo': str})
    rpls_iris = pd.read_csv(chemin_rpls_iris, dtype={'CodGeo': str})

    qpv = rpls_qpv[['CodGeo', 'nbLsPls']].copy()
    qpv['unit_id'] = 'QPV_' + qpv['CodGeo']
    qpv['proportion'] = qpv['nbLsPls'] / qpv['CodGeo'].map(denom_qpv)

    iris = rpls_iris[['CodGeo', 'nbLsPls']].copy()
    iris['unit_id'] = 'IRIS_' + iris['CodGeo']
    iris['proportion'] = iris['nbLsPls'] / iris['CodGeo'].map(denom_iris)

    combine = pd.concat([qpv[['unit_id', 'proportion']], iris[['unit_id', 'proportion']]], ignore_index=True)
    combine['proportion'] = combine['proportion'].replace([np.inf, -np.inf], np.nan)
    m, s = combine['proportion'].mean(), combine['proportion'].std()
    combine['prop_z'] = (combine['proportion'] - m) / s
    return combine[['unit_id', 'prop_z']]


if __name__ == '__main__':
    reg_data = reg_mod.construire_panel_regression(
        'data/processed/appariement_qpv_iris_v2.csv',
        'data/processed/panel_qpv_complet_v2.csv',
        'data/processed/panel_iris_complet_v2.csv',
        'data/processed/qpv_info_nom_commune.csv',
    )
    ls_z = bal_mod.construire_logement_social_z('data/processed/rpls_qpv.csv', 'data/processed/rpls_iris.csv')
    reg_data = reg_data.merge(ls_z, on='unit_id', how='left')
    reg_data['ls_z'] = reg_data['ls_z'].fillna(0)

    log_total_iris = charger_logement_total_iris(
        'data/raw/IRIS - Logement - 2022.zip',
        '/tmp/claude-1000/-workspaces-M-moire-DU-SDA/e7e7888b-2926-4580-91e3-fb8cdab5ccae/scratchpad')
    pop_qpv_2018 = pd.read_csv('data/processed/qpv_evolution_population.csv', dtype={'code': str}) \
        .set_index('code')['pop_2018']
    pop_iris_2018 = pd.read_csv('data/processed/iris_evolution_population.csv', dtype={'IRIS': str}) \
        .set_index('IRIS')['pop_2018']

    # Version demandée : dénominateur réel (logements) côté IRIS, repli (population) côté QPV
    prop_mixte = construire_proportion_z('data/processed/rpls_qpv.csv', 'data/processed/rpls_iris.csv',
                                          denom_qpv=pop_qpv_2018, denom_iris=log_total_iris)
    reg_data = reg_data.merge(prop_mixte.rename(columns={'prop_z': 'prop_mixte_z'}), on='unit_id', how='left')
    reg_data['prop_mixte_z'] = reg_data['prop_mixte_z'].fillna(0)

    # Vérification de cohérence : même dénominateur (population 2018) des deux côtés
    prop_homogene = construire_proportion_z('data/processed/rpls_qpv.csv', 'data/processed/rpls_iris.csv',
                                             denom_qpv=pop_qpv_2018, denom_iris=pop_iris_2018)
    reg_data = reg_data.merge(prop_homogene.rename(columns={'prop_z': 'prop_homogene_z'}), on='unit_id', how='left')
    reg_data['prop_homogene_z'] = reg_data['prop_homogene_z'].fillna(0)

    reg_data_eq = reg_mod.restreindre_panel_equilibre(reg_data)
    unites = reg_data_eq.drop_duplicates('unit_id')
    print("Moyenne par groupe (traite=1 QPV, traite=0 IRIS) :")
    print(unites.groupby('traite')[['ls_z', 'prop_mixte_z', 'prop_homogene_z']].mean().round(3))

    print("\n=== Sans aucun contrôle logement ===")
    res_sans, _ = bal_mod.estimer_avec_controles(reg_data_eq, 'taux_pauvrete', [])
    print(res_sans.round(4))

    print("\n=== Contrôle ABSOLU (nbLsPls standardisé, référence section 33) ===")
    res_abs, _ = bal_mod.estimer_avec_controles(reg_data_eq, 'taux_pauvrete', ['ls_z'])
    print(res_abs.round(4))

    print("\n=== Contrôle en PROPORTION MIXTE (logements IRIS / population QPV 2018) ===")
    res_mixte, _ = bal_mod.estimer_avec_controles(reg_data_eq, 'taux_pauvrete', ['prop_mixte_z'])
    print(res_mixte.round(4))

    print("\n=== Contrôle en proportion, dénominateur HOMOGÈNE (population 2018 des deux côtés) — diagnostic ===")
    res_homogene, _ = bal_mod.estimer_avec_controles(reg_data_eq, 'taux_pauvrete', ['prop_homogene_z'])
    print(res_homogene.round(4))
