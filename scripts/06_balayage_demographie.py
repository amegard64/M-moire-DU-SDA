"""
Chantier 5 (brief limites/robustesse) : balayage systématique des variables
socio-démographiques 2010 côté QPV, en interaction avec l'année, pour voir
lesquelles absorbent le plus de signal sur le taux de pauvreté — version
automatisée et exhaustive de ce qui a été fait à la main pour le logement
social (section 25 du carnet) et la population (section 36).

Logique de merge (pas besoin de donnée IRIS, contrairement au Chantier 4) :
chaque IRIS de contrôle hérite de la valeur de SON QPV apparié (même logique
que test_heterogeneite_evolution_population dans 05_tests_robustesse.py,
généralisée ici à n'importe quelle variable numérique).

Chaque variable est testée en plus du contrôle logement social déjà retenu
comme référence (section 33 du carnet), pour chercher ce qui explique le
résidu de pauvreté non expliqué par le logement social seul.

ATTENTION (à répéter dans le carnet) : tester ~24 variables une par une sur
la même régression augmente le risque de faux positifs (problème de tests
multiples, pas de correction de type Bonferroni appliquée ici). Résultat
exploratoire, pas confirmatoire.
"""
import pandas as pd
import numpy as np
from linearmodels import PanelOLS

from importlib import import_module
reg_mod = import_module('04_regression_event_study')


def charger_demographie_qpv(chemin_xls):
    """Charge la feuille 'Quartiers' du fichier démographie 2010 (62 colonnes
    de variables + 5 colonnes d'identification). Retire la ligne d'agrégat
    parasite en tête de fichier (repérable par l'absence de code QP...)."""
    xl = pd.ExcelFile(chemin_xls)
    demo = xl.parse('Quartiers', header=5)
    return demo[demo['qp'].astype(str).str.startswith('QP')].copy()


def variables_non_redondantes():
    """Sélectionne les variables de 'premier rang' (calculées par rapport à
    la population totale du quartier) et exclut les déclinaisons de 'second
    rang' par sexe/nationalité (préfixes h_/f_/fr_/et_, ou tx_f_.../tx_et_...),
    qui répètent le même total déjà présent sur une sous-population — cf.
    doc du fichier source, feuille 'Documentation', point 5-6. Exception :
    tx_f (part de femmes dans la population totale) est gardée, ce n'est pas
    la déclinaison d'un total déjà présent mais une variable de composition
    à part entière."""
    return [
        'ind_jeune', 'tx_tot_0a14', 'tx_tot_15a24', 'tx_tot_25a59', 'tx_tot_60a74',
        'tx_tot_75etplus', 'tx_f', 'tx_tot_et', 'tx_tot_empl', 'tx_tot_eprec',
        'tx_tot_infbac', 'tx_tot_diplbac', 'tx_tot_diplbac2', 'tx_tot_scol',
        'tx_tot_men1', 'tx_tot_men1_60a74', 'tx_tot_men1_75etplus', 'tx_tot_fam_mono',
        'tx_tot_men6', 'tx_l_2piec', 'tx_l_5piec', 'tx_l_vacant', 'l_nbpers',
        'tx_nblog_20l',
    ]


def construire_logement_social_z(chemin_rpls_qpv, chemin_rpls_iris):
    """Reconstruit le contrôle logement social (ls_z) déjà utilisé pour le
    résultat de référence (section 33) : nbLsPls standardisé, côté QPV et
    côté IRIS directement (donnée réelle des deux côtés, pas d'héritage)."""
    rpls_qpv = pd.read_csv(chemin_rpls_qpv)
    rpls_iris = pd.read_csv(chemin_rpls_iris)
    qpv_side = rpls_qpv[['CodGeo', 'nbLsPls']].copy()
    qpv_side['unit_id'] = 'QPV_' + qpv_side['CodGeo']
    iris_side = rpls_iris[['CodGeo', 'nbLsPls']].copy()
    iris_side['unit_id'] = 'IRIS_' + iris_side['CodGeo']
    ls = pd.concat([qpv_side[['unit_id', 'nbLsPls']], iris_side[['unit_id', 'nbLsPls']]], ignore_index=True)
    m, s = ls['nbLsPls'].mean(), ls['nbLsPls'].std()
    ls['ls_z'] = (ls['nbLsPls'] - m) / s
    return ls[['unit_id', 'ls_z']]


def valeur_par_unite(demo_df, appariement_df, variable):
    """Série indexée par unit_id : valeur propre pour un QPV, valeur du QPV
    apparié pour un IRIS de contrôle (héritage, pas une caractéristique
    propre à l'IRIS — voir limite documentée dans le carnet)."""
    qpv_val = demo_df.set_index('qp')[variable]
    valeurs = {f'QPV_{code}': v for code, v in qpv_val.items()}
    for _, row in appariement_df.iterrows():
        if row['code_qpv'] in qpv_val.index:
            valeurs[f"IRIS_{row['iris_controle']}"] = qpv_val[row['code_qpv']]
    return pd.Series(valeurs, name=variable)


def estimer_avec_controles(reg_data, outcome, colonnes_controles, reference='pooled'):
    """Généralise estimer_event_study : ajoute une interaction annee x controle
    pour chaque colonne (déjà standardisée) listée dans colonnes_controles,
    en plus des interactions traite x annee habituelles."""
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
    for controle in colonnes_controles:
        for a in annees_interaction:
            col = f'{controle}_x_{a}'
            data[col] = data[controle] * (data['annee'] == a).astype(int)
            interaction_cols.append(col)

    data_idx = data.set_index(['unit_id', 'annee'])
    mod = PanelOLS(data_idx[outcome], data_idx[interaction_cols], entity_effects=True, time_effects=True)
    res = mod.fit(cov_type='clustered', clusters=data_idx['commune_cluster'])

    cols_traite = [c for c in interaction_cols if c.startswith('traite_x_')]
    resultat = pd.DataFrame({'coef': res.params[cols_traite], 'p_value': res.pvalues[cols_traite]})
    if not colonnes_controles:
        return resultat, pd.Series(dtype=float)
    dernier_controle = colonnes_controles[-1]
    cols_var = [c for c in interaction_cols if c.startswith(f'{dernier_controle}_x_')]
    return resultat, res.pvalues[cols_var]


def balayage(reg_data_eq, demo_df, appariement_df, variables, outcome='taux_pauvrete',
             annees_sig=(2015, 2016, 2018, 2021)):
    """Pour chaque variable démographique, ajoute son interaction avec l'année
    en plus du contrôle logement social déjà en place, et mesure la réduction
    en % du coefficient traite x annee sur les années significatives de la
    référence (baseline = traite x annee + ls_z x annee seul)."""
    baseline, _ = estimer_avec_controles(reg_data_eq, outcome, ['ls_z'])
    reg_data_eq = reg_data_eq.copy()

    lignes = []
    for var in variables:
        valeurs_unit = valeur_par_unite(demo_df, appariement_df, var)
        pct_manquant = valeurs_unit.isna().mean() * 100
        raw = reg_data_eq['unit_id'].map(valeurs_unit).astype(float)
        moyenne, ecart_type = raw.mean(), raw.std()
        if ecart_type == 0 or pd.isna(ecart_type):
            continue
        reg_data_eq['var_z'] = ((raw - moyenne) / ecart_type).fillna(0)

        res, var_pvals = estimer_avec_controles(reg_data_eq, outcome, ['ls_z', 'var_z'])
        reductions = {
            a: (baseline.loc[f'traite_x_{a}', 'coef'] - res.loc[f'traite_x_{a}', 'coef'])
               / baseline.loc[f'traite_x_{a}', 'coef'] * 100
            for a in annees_sig
        }
        ligne = {'variable': var, 'reduction_moyenne_%': np.mean(list(reductions.values()))}
        ligne.update({f'reduction_{a}_%': r for a, r in reductions.items()})
        ligne['pct_valeurs_manquantes_qpv'] = pct_manquant
        ligne['n_interactions_significatives_sur_6'] = int((var_pvals < 0.05).sum())
        lignes.append(ligne)

    tableau = pd.DataFrame(lignes).sort_values('reduction_moyenne_%', ascending=False).reset_index(drop=True)
    return tableau, baseline


if __name__ == '__main__':
    reg_data = reg_mod.construire_panel_regression(
        'data/processed/appariement_qpv_iris_v2.csv',
        'data/processed/panel_qpv_complet_v2.csv',
        'data/processed/panel_iris_complet_v2.csv',
        'data/processed/qpv_info_nom_commune.csv',
    )
    ls_z = construire_logement_social_z('data/processed/rpls_qpv.csv', 'data/processed/rpls_iris.csv')
    reg_data = reg_data.merge(ls_z, on='unit_id', how='left')
    reg_data['ls_z'] = reg_data['ls_z'].fillna(0)
    reg_data_sans_2020 = reg_data[reg_data['annee'] != 2020].copy()
    reg_data_eq = reg_mod.restreindre_panel_equilibre(reg_data_sans_2020)

    demo = charger_demographie_qpv('data/processed/demographie_2010_qpv.xls')
    app = pd.read_csv('data/processed/appariement_qpv_iris_v2.csv')
    variables = variables_non_redondantes()

    tableau, baseline = balayage(reg_data_eq, demo, app, variables)

    print(f"=== Référence (traite x année + logement social x année seul, "
          f"panel équilibré {reg_data_eq['unit_id'].nunique()} unités, sans 2020) ===")
    print(baseline.round(4))

    print(f"\n=== Balayage de {len(variables)} variables démographiques 2010 "
          f"(déduplication sexe/nationalité, sur {len(demo)} QPV documentés) ===")
    pd.set_option('display.width', 160)
    print(tableau.round(2).to_string())

    tableau.to_csv('data/processed/balayage_demographie_2010.csv', index=False)
