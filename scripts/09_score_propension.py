"""
Chantier 4 (brief limites/robustesse) - étape 2 : score de propension
multivarié pour remplacer l'appariement univarié (seule la pauvreté
pré-traitement, cf. 03_controle_iris_miroirs.py) par un appariement sur un
score prédit par régression logistique (choix discret, dans le cadre du
cours - cf. Statistics_Slides_bin_choice.pdf).

Option retenue (a) du brief : utiliser l'équivalent IRIS des variables
démographiques 2010, construit à l'étape 1 (08_demographie_iris_2010.py,
data/processed/demographie_2010_iris.csv), en plus des deux caractéristiques
déjà disponibles des deux côtés (pauvreté et revenu médian pré-traitement).

Modèle : logit(QPV=1 / IRIS candidat=0) ~ 9 variables démographiques 2010
(standardisées) + pauvreté pré-traitement (standardisée) + log(revenu médian
pré-traitement) (standardisé). Les 9 variables démographiques retenues sont
un sous-ensemble des 13 reconstructibles côté IRIS (08_demographie_iris_2010.py) :
4 en ont été retirées (ind_jeune, tx_l_2piec, tx_l_5piec, tx_l_vacant) à cause
d'un taux de valeurs manquantes côté QPV trop élevé (13 à 50% selon la
variable, secret statistique - quartiers plus petits que les IRIS), qui se
serait cumulé par suppression listwise avec les 9 autres variables et aurait
fait perdre plus de 60% des QPV. Voir VARIABLES_DEMOGRAPHIQUES ci-dessous
pour le détail de ce qui est gardé/exclu et pourquoi.

Score prédit = probabilité prédite d'appartenir au groupe QPV. Ré-appariement
K plus proches voisins (K=5, comme l'appariement univarié) sur la distance
absolue en score, même règle de repli commune -> unité urbaine que
03_controle_iris_miroirs.apparier_qpv_iris.

Limite importante à documenter : lignes avec au moins une variable manquante
(secret statistique) exclues du calcul du score (logit puis appariement) -
listwise deletion plutôt qu'une imputation qui masquerait le problème,
cohérent avec le traitement du secret statistique déjà appliqué ailleurs
dans le pipeline (03_controle_iris_miroirs.py). Perte résultante : 1296 ->
1089 QPV avec covariables complètes (16% de perte, contre 0% pour
l'appariement univarié qui n'utilise que la pauvreté).

Résultat obtenu (à détailler dans le carnet) : le logit non pénalisé ne
converge pas (séparation quasi-parfaite - la pauvreté et les variables qui
lui sont corrélées suffisent presque à elles seules à distinguer QPV et IRIS
candidats, ce qui n'est pas surprenant vu la définition même du zonage QPV).
Une fois résolu par pénalisation ridge (C choisi par validation croisée),
l'AUC in-sample reste à 1.000 et les scores prédits sont quasi tous saturés
près de 1 pour les QPV ET pour les IRIS qui leur ressemblent le plus - de
sorte que l'appariement par plus proche voisin sur le score reproduit à 76%
les mêmes paires QPV-IRIS que l'appariement univarié sur la seule pauvreté
(3777/4952 paires identiques), et un équilibre des covariables presque
identique aux deux méthodes. Le score multivarié ne change donc pas
qualitativement l'appariement ni les résultats de la régression event-study
(mêmes signes, magnitudes proches) - un résultat de robustesse plutôt qu'une
correction du design.
"""
import warnings
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_auc_score

warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')

from importlib import import_module
miroirs = import_module('03_controle_iris_miroirs')
reg_mod = import_module('04_regression_event_study')
balayage = import_module('06_balayage_demographie')

K_VOISINS = miroirs.K_VOISINS
ANNEES_PRETRAITEMENT = miroirs.ANNEES_PRETRAITEMENT

VARIABLES_DEMOGRAPHIQUES = [
    'tx_f', 'tx_tot_et', 'tx_tot_empl', 'tx_tot_infbac',
    'tx_tot_diplbac', 'tx_tot_diplbac2', 'tx_tot_men1', 'tx_tot_fam_mono',
    'l_nbpers',
]
# Exclues du score bien que reconstruites côté IRIS (08_demographie_iris_2010.py) :
# ind_jeune, tx_l_2piec, tx_l_5piec, tx_l_vacant. Raison : missingness côté QPV
# (secret statistique, quartiers plus petits que les IRIS) trop élevée pour ces
# 4 variables - 13 à 50% selon la variable (vérifié directement, pas supposé) -
# qui se cumulerait par suppression listwise avec les 9 autres variables et
# détruirait l'échantillon. tx_l_vacant et son voisin tx_tot_men6 (déjà exclu,
# non reconstructible côté IRIS) étaient déjà signalés comme les deux variables
# les plus fragiles du balayage (carnet section 41, ~50% de manquants).


def construire_revenu_pretraitement_qpv(panel_qpv, qpv_info):
    pre = panel_qpv[panel_qpv['annee'].isin(ANNEES_PRETRAITEMENT)]
    moy = pre.groupby('code')['revenu_median'].mean().reset_index() \
        .rename(columns={'revenu_median': 'revenu_median_pre'})
    return moy.merge(qpv_info, on='code')[['code', 'revenu_median_pre']]


def construire_revenu_pretraitement_iris(panel_iris, iris_candidats):
    pre = panel_iris[panel_iris['annee'].isin(ANNEES_PRETRAITEMENT)]
    moy = pre.groupby('iris')['revenu_median'].mean().reset_index() \
        .rename(columns={'revenu_median': 'revenu_median_pre'})
    return iris_candidats.merge(moy, on='iris', how='inner')[['iris', 'revenu_median_pre']]


def construire_table_covariables():
    """Assemble une table unique QPV + IRIS candidats, une ligne par unité,
    avec 'traite' (1=QPV, 0=IRIS) et les covariables brutes (non standardisées)."""
    dossier = 'data/processed'
    panel_qpv = pd.read_csv(f'{dossier}/panel_qpv_complet_v2.csv', dtype={'code': str})
    panel_iris = pd.read_csv(f'{dossier}/panel_iris_complet_v2.csv', dtype={'iris': str, 'com': str})
    qpv_info = pd.read_csv(f'{dossier}/qpv_info_nom_commune.csv', dtype={'code': str, 'insee_com': str})
    rpls_iris = pd.read_csv(f'{dossier}/rpls_iris.csv', dtype=str)

    candidats = miroirs.construire_iris_candidats(panel_iris, qpv_info, rpls_iris)
    qpv_pauvrete = miroirs.construire_pauvrete_pretraitement_qpv(panel_qpv, qpv_info)
    iris_pauvrete = miroirs.construire_pauvrete_pretraitement_iris(panel_iris, candidats)
    qpv_revenu = construire_revenu_pretraitement_qpv(panel_qpv, qpv_info)
    iris_revenu = construire_revenu_pretraitement_iris(panel_iris, candidats)

    demo_qpv = balayage.charger_demographie_qpv(f'{dossier}/demographie_2010_qpv.xls')
    demo_iris = pd.read_csv(f'{dossier}/demographie_2010_iris.csv', dtype={'iris': str, 'com': str})

    demo_qpv = demo_qpv.copy()
    for col in VARIABLES_DEMOGRAPHIQUES:
        demo_qpv[col] = pd.to_numeric(demo_qpv[col], errors='raise')

    qpv = qpv_pauvrete.merge(qpv_revenu, on='code').merge(
        demo_qpv[['qp'] + VARIABLES_DEMOGRAPHIQUES], left_on='code', right_on='qp', how='left')
    qpv['unit_id'] = 'QPV_' + qpv['code']
    qpv['traite'] = 1
    qpv['commune'] = qpv['insee_com']

    iris = iris_pauvrete.merge(iris_revenu, on='iris').merge(
        demo_iris.drop(columns='com'), on='iris', how='left')
    iris['unit_id'] = 'IRIS_' + iris['iris']
    iris['traite'] = 0
    iris['commune'] = iris['com']

    cols = ['unit_id', 'traite', 'commune', 'taux_pauvrete_pre', 'revenu_median_pre'] + VARIABLES_DEMOGRAPHIQUES
    table = pd.concat([qpv[cols], iris[cols]], ignore_index=True)
    id_source = pd.concat([
        qpv[['unit_id']].assign(code_qpv=qpv['code']),
        iris[['unit_id']].assign(iris_code=iris['iris'], com=iris['com']),
    ], ignore_index=True)
    return table, id_source


def standardiser_covariables(table):
    """Standardise (z-score) sur l'ensemble QPV + IRIS candidats combiné,
    même convention que construire_logement_social_z (06_balayage_demographie.py)."""
    table = table.copy()
    table['log_revenu_pre'] = np.log(table['revenu_median_pre'])
    colonnes_brutes = ['taux_pauvrete_pre', 'log_revenu_pre'] + VARIABLES_DEMOGRAPHIQUES
    colonnes_z = []
    for col in colonnes_brutes:
        m, s = table[col].mean(), table[col].std()
        col_z = f'{col}_z'
        table[col_z] = (table[col] - m) / s
        colonnes_z.append(col_z)
    return table, colonnes_z


def estimer_logit(table, colonnes_z):
    """Régression logistique QPV=1/IRIS=0 sur les covariables standardisées.
    Listwise deletion sur les lignes à covariable manquante (secret statistique).

    Un logit non pénalisé (statsmodels) ne converge pas ici : Hessienne
    singulière, symptôme classique de séparation quasi-parfaite. Résultat
    attendu et substantiel, pas un simple bug numérique : le zonage QPV est
    précisément défini à partir de critères socio-économiques (pauvreté en
    tête), donc les 15 covariables pré-traitement (dont la pauvreté
    elle-même) suffisent quasiment à elles seules à séparer QPV et IRIS
    candidats. Solution dans le cadre du cours : régression logistique
    pénalisée (ridge/L2, cf. ridge/lasso au programme), force de
    régularisation choisie par validation croisée plutôt que fixée à la
    main (LogisticRegressionCV, scikit-learn)."""
    complet = table.dropna(subset=colonnes_z).copy()
    X = complet[colonnes_z].to_numpy()
    y = complet['traite'].to_numpy()
    modele = LogisticRegressionCV(cv=5, penalty='l2', solver='lbfgs',
                                    scoring='neg_log_loss', max_iter=2000).fit(X, y)
    complet['score'] = modele.predict_proba(X)[:, 1]
    return modele, complet


def _plus_proches_score(candidats, score_qpv, k=K_VOISINS):
    c = candidats.copy()
    c['distance_score'] = (c['score'] - score_qpv).abs()
    return c.sort_values('distance_score').head(k)


def apparier_sur_score(complet, id_source, commune_vers_uu):
    """Même logique que miroirs.apparier_qpv_iris (repli commune -> unité
    urbaine, K=5), mais la distance est calculée sur le score de propension
    plutôt que sur la seule pauvreté pré-traitement."""
    complet = complet.merge(id_source, on='unit_id', how='left')
    qpv = complet[complet['traite'] == 1].dropna(subset=['code_qpv'])
    iris = complet[complet['traite'] == 0].dropna(subset=['iris_code']).drop(columns='commune')
    iris = iris.merge(commune_vers_uu, left_on='com', right_on='commune', how='left').drop(columns='commune')
    commune_to_uu = commune_vers_uu.set_index('commune')['unite_urbaine']

    resultats = []
    for _, q in qpv.iterrows():
        candidats_commune = iris[iris['com'] == q['commune']]
        if len(candidats_commune) > 0:
            proches = _plus_proches_score(candidats_commune, q['score'])
            niveau = 'commune'
        else:
            uu = commune_to_uu.get(q['commune'])
            candidats_uu = iris[iris['unite_urbaine'] == uu] if pd.notna(uu) else iris.iloc[0:0]
            if len(candidats_uu) == 0:
                continue
            proches = _plus_proches_score(candidats_uu, q['score'])
            niveau = 'unite_urbaine'
        for _, r in proches.iterrows():
            resultats.append({'code_qpv': q['code_qpv'], 'iris_controle': r['iris_code'],
                               'distance_score': r['distance_score'], 'niveau': niveau})
    return pd.DataFrame(resultats)


def comparer_equilibre_covariables(complet, appariement_score, appariement_univarie, colonnes_z):
    """Différence de moyennes standardisées (SMD) QPV vs IRIS de contrôle,
    pour chacune des deux méthodes d'appariement, sur les covariables
    utilisées par le score. Indicateur simple de qualité d'appariement
    (pas un test formel, juste une comparaison descriptive avant/après)."""
    qpv_vals = complet[complet['traite'] == 1][colonnes_z]
    moyenne_qpv = qpv_vals.mean()

    def moyenne_controle(app, colonne_iris):
        iris_ids = app[colonne_iris].unique()
        sous = complet[complet['unit_id'].isin('IRIS_' + pd.Series(iris_ids))]
        return sous[colonnes_z].mean()

    moyenne_score = moyenne_controle(appariement_score, 'iris_controle')
    moyenne_univarie = moyenne_controle(appariement_univarie, 'iris_controle')

    ecart_type_pool = complet[colonnes_z].std()
    tableau = pd.DataFrame({
        'moyenne_qpv': moyenne_qpv,
        'moyenne_iris_univarie': moyenne_univarie,
        'smd_univarie': (moyenne_qpv - moyenne_univarie) / ecart_type_pool,
        'moyenne_iris_score': moyenne_score,
        'smd_score': (moyenne_qpv - moyenne_score) / ecart_type_pool,
    })
    return tableau


if __name__ == '__main__':
    dossier = 'data/processed'
    table, id_source = construire_table_covariables()
    table, colonnes_z = standardiser_covariables(table)

    print(f"Unités QPV : {(table['traite'] == 1).sum()}, IRIS candidats : {(table['traite'] == 0).sum()}")
    print(f"Valeurs manquantes par covariable (sur l'ensemble QPV+IRIS) :")
    for col in colonnes_z:
        print(f"  {col} : {table[col].isna().mean() * 100:.1f}%")

    modele, complet = estimer_logit(table, colonnes_z)
    print(f"\nÉchantillon retenu pour le logit (covariables complètes) : "
          f"{(complet['traite'] == 1).sum()} QPV, {(complet['traite'] == 0).sum()} IRIS "
          f"(sur {(table['traite'] == 1).sum()} et {(table['traite'] == 0).sum()} au départ)")
    print(f"\n=== Régression logistique QPV=1/IRIS=0 (ridge, C choisi par validation croisée = {modele.C_[0]:.4g}) ===")
    coefs = pd.Series(modele.coef_[0], index=colonnes_z).sort_values(key=abs, ascending=False)
    print(coefs.round(3))
    auc = roc_auc_score(complet['traite'], complet['score'])
    print(f"AUC (in-sample) : {auc:.3f}")

    commune_vers_uu = pd.read_csv(f'{dossier}/commune_vers_unite_urbaine.csv',
                                   dtype={'commune': str, 'unite_urbaine': str})
    appariement_score = apparier_sur_score(complet, id_source, commune_vers_uu)
    n_qpv_score = appariement_score['code_qpv'].nunique()
    print(f"\nAppariement sur score : {n_qpv_score} QPV appariés, "
          f"{appariement_score['iris_controle'].nunique()} IRIS de contrôle distincts")

    appariement_univarie = pd.read_csv(f'{dossier}/appariement_qpv_iris_v2.csv', dtype=str)
    appariement_univarie['distance_pauvrete'] = appariement_univarie['distance_pauvrete'].astype(float)

    equilibre = comparer_equilibre_covariables(complet, appariement_score, appariement_univarie, colonnes_z)
    print("\n=== Équilibre des covariables (écart standardisé QPV - contrôle) ===")
    pd.set_option('display.width', 160)
    print(equilibre.round(3))

    chemin_tmp_score = 'data/processed/appariement_qpv_iris_score_propension.csv'
    appariement_score.to_csv(chemin_tmp_score, index=False)

    print("\n=== Comparaison régression event-study : univarié (pauvreté seule) vs score de propension ===")
    for chemin_app, nom in [
        ('data/processed/appariement_qpv_iris_v2.csv', 'univarié (pauvreté)'),
        (chemin_tmp_score, 'score de propension'),
    ]:
        reg_data = reg_mod.construire_panel_regression(
            chemin_app,
            f'{dossier}/panel_qpv_complet_v2.csv',
            f'{dossier}/panel_iris_complet_v2.csv',
            f'{dossier}/qpv_info_nom_commune.csv',
        )
        reg_data_sans_2020 = reg_data[reg_data['annee'] != 2020].copy()
        reg_data_eq = reg_mod.restreindre_panel_equilibre(reg_data_sans_2020)
        res_pauvrete, _ = reg_mod.estimer_event_study(reg_data_eq, 'taux_pauvrete', reference='pooled')
        res_revenu, _ = reg_mod.estimer_event_study(reg_data_eq, 'log_revenu', reference='pooled')
        print(f"\n--- {nom} (panel équilibré {reg_data_eq['unit_id'].nunique()} unités, sans 2020) ---")
        print("Pauvreté :")
        print(res_pauvrete.round(4))
        print("Revenu log :")
        print(res_revenu.round(4))
