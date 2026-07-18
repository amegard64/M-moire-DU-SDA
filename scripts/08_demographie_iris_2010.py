"""
Chantier 4 (brief limites/robustesse) - étape 1 : reconstruire côté IRIS de
contrôle les variables démographiques 2010 déjà disponibles côté QPV
(data/processed/demographie_2010_qpv.xls, 24 variables non redondantes,
carnet section 41), condition nécessaire pour un score de propension
multivarié (le score a besoin des MEMES variables des deux côtés, traité et
contrôle - contrairement au Chantier 5 qui se contente d'un héritage QPV vers
IRIS apparié).

Source : 5 produits "Base infracommunale (IRIS)" de l'Insee, recensement de
la population 2010 (data/raw/, non versionné - fichiers bruts volumineux,
~200 Mo au total) :
- IRIS - Population - 2010.zip           -> base-ic-evol-struct-pop-2010.xls
- IRIS - Activité des résidents - 2010.zip -> base-ic-caract-emploi-2010.xls
- IRIS - Diplômes:Formations - 2010.xls
- IRIS - Couples:Familles:Ménages - 2010.zip -> base-ic-couples-familles-menages-2010.xls
- IRIS - Logement - 2010.xls

Sur les 24 variables non redondantes retenues côté QPV (section 41), 13 sont
reconstructibles CÔTÉ IRIS avec une formule exactement conforme à la
documentation du fichier QPV (vérifiée variable par variable, feuille
"Documentation" du fichier QPV et feuilles "Liste des variables" des 5
fichiers Insee - jamais déduite du seul nom de colonne) :

  tx_f, tx_tot_et, ind_jeune, tx_tot_empl, tx_tot_infbac, tx_tot_diplbac,
  tx_tot_diplbac2, tx_l_2piec, tx_l_5piec, tx_l_vacant, l_nbpers,
  tx_tot_men1, tx_tot_fam_mono

Les 11 autres ne sont PAS reconstruites ici, par prudence plutôt que par
approximation risquée :
- tx_tot_0a14/15a24/25a59/60a74/75etplus (+ déclinaisons men1_60a74/75etplus) :
  les fichiers Insee IRIS 2010 utilisés découpent l'âge en tranches
  différentes de celles du fichier QPV (ex. 15-29/30-44/45-59 au lieu de
  15-24/25-59) - impossible de recalculer les mêmes bornes sans les données
  détaillées par âge simple, non disponibles dans ces produits agrégés.
- tx_tot_eprec : la définition QPV agrège des catégories de contrats précaires
  (apprentissage, intérim, emplois-jeunes, CES, qualification, stagiaires
  rémunérés, "autres emplois à durée limitée") qui ne correspondent pas
  exactement aux catégories disponibles côté IRIS (SAL15P_CDD/INTERIM/EMPAID/
  APPR, sur une population de référence différente - 15 ans ou plus, pas
  15-64 ans) - reconstruction trop incertaine pour être présentée comme fiable.
- tx_tot_scol : bornes d'âge différentes également (15-17/18-24/25-29 côté
  Insee IRIS vs 16-24 côté QPV).
- tx_tot_men6 et tx_nblog_20l : aucune variable équivalente disponible dans
  les 5 fichiers Insee IRIS 2010 mobilisés (pas de détail par taille de
  ménage au-delà de "personne seule", pas de détail par taille d'immeuble).

Sortie : data/processed/demographie_2010_iris.csv (IRIS des communes
candidates uniquement - cf. 03_controle_iris_miroirs.construire_iris_candidats
- et 13 colonnes utiles, pas les ~50 000 IRIS de France ni les décompositions
sexe/nationalité/tranche d'âge non retenues). Fichier volontairement réduit
aux colonnes et lignes exploitées, pour rester commitable (quelques centaines
de Ko) malgré des fichiers sources bruts trop volumineux (~200 Mo) pour être
versionnés - même logique que rpls_iris.csv, panel_iris_complet_v2.csv, etc.
"""
import zipfile
import subprocess
import tempfile
import os
import pandas as pd

from importlib import import_module
miroirs = import_module('03_controle_iris_miroirs')

FICHIERS = {
    'population': ('IRIS - Population - 2010', 'base-ic-evol-struct-pop-2010.xls', 5),
    'emploi': ('IRIS - Activit', 'base-ic-caract-emploi-2010.xls', 5),
    'diplomes': ('IRIS - Dipl', None, 5),
    'menages': ('IRIS - Couples', 'base-ic-couples-familles-menages-2010.xls', 5),
    'logement': ('IRIS - Logement - 2010', None, 5),
}


def _trouver_fichier(prefixe, dossier_raw):
    """Recherche par préfixe plutôt que nom exact : les noms de fichiers
    accentués fournis par Alexandre sont normalisés en NFD sur le disque,
    alors qu'un littéral Python dans ce fichier source est en NFC - une
    comparaison stricte échoue silencieusement selon l'éditeur utilisé."""
    candidats = [f for f in os.listdir(dossier_raw) if f.startswith(prefixe)]
    if len(candidats) != 1:
        raise FileNotFoundError(f"Préfixe '{prefixe}' : {len(candidats)} correspondance(s) dans {dossier_raw}")
    return candidats[0]


def _extraire_si_zip(nom_archive, nom_membre, dossier_raw='data/raw'):
    """Extraction via `unzip` en sous-processus plutôt que le module zipfile :
    zipfile lève une erreur CRC-32 sur certaines archives Insee alors que
    `unzip` les lit sans erreur (même incident que celui documenté pour
    IRIS - Logement - 2022.zip, carnet section 42, cause non investiguée)."""
    chemin_archive = os.path.join(dossier_raw, nom_archive)
    if not nom_archive.endswith('.zip'):
        return chemin_archive
    dossier_tmp = tempfile.mkdtemp()
    subprocess.run(['unzip', '-o', chemin_archive, nom_membre, '-d', dossier_tmp],
                   check=True, capture_output=True)
    return os.path.join(dossier_tmp, nom_membre)


def _lire_feuille_iris(cle, dossier_raw='data/raw'):
    prefixe, nom_membre, header = FICHIERS[cle]
    nom_archive = _trouver_fichier(prefixe, dossier_raw)
    chemin = _extraire_si_zip(nom_archive, nom_membre, dossier_raw)
    return pd.read_excel(chemin, sheet_name='IRIS', header=header, dtype={'IRIS': str})


def construire_demographie_iris(dossier_raw='data/raw'):
    pop = _lire_feuille_iris('population', dossier_raw)
    emploi = _lire_feuille_iris('emploi', dossier_raw)
    diplomes = _lire_feuille_iris('diplomes', dossier_raw)
    menages = _lire_feuille_iris('menages', dossier_raw)
    logement = _lire_feuille_iris('logement', dossier_raw)

    out = pop[['IRIS']].copy()
    out['tx_f'] = pop['P10_POPF'] / pop['P10_POP']
    out['tx_tot_et'] = pop['P10_POP_ETR'] / pop['P10_POP']
    out['ind_jeune'] = pop['P10_POP0019'] / (pop['P10_POP6074'] + pop['P10_POP75P'])

    emploi = emploi[['IRIS']].copy().assign(
        tx_tot_empl=emploi['P10_ACTOCC1564'] / emploi['P10_POP1564'])
    out = out.merge(emploi, on='IRIS', how='left')

    diplomes = diplomes.assign(
        tx_tot_infbac=(diplomes['P10_NSCOL15P_DIPL0'] + diplomes['P10_NSCOL15P_CEP']
                       + diplomes['P10_NSCOL15P_BEPC'] + diplomes['P10_NSCOL15P_CAPBEP'])
                      / diplomes['P10_NSCOL15P'],
        tx_tot_diplbac=diplomes['P10_NSCOL15P_BAC'] / diplomes['P10_NSCOL15P'],
        tx_tot_diplbac2=(diplomes['P10_NSCOL15P_BACP2'] + diplomes['P10_NSCOL15P_SUP'])
                        / diplomes['P10_NSCOL15P'],
    )
    out = out.merge(diplomes[['IRIS', 'tx_tot_infbac', 'tx_tot_diplbac', 'tx_tot_diplbac2']],
                     on='IRIS', how='left')

    menages = menages.assign(
        tx_tot_men1=menages['C10_MENPSEUL'] / menages['C10_MEN'],
        tx_tot_fam_mono=menages['C10_MENFAMMONO'] / menages['C10_MEN'],
    )
    out = out.merge(menages[['IRIS', 'tx_tot_men1', 'tx_tot_fam_mono']], on='IRIS', how='left')

    logement = logement.assign(
        tx_l_2piec=logement['P10_RP_2P'] / logement['P10_RP'],
        tx_l_5piec=logement['P10_RP_5PP'] / logement['P10_RP'],
        tx_l_vacant=logement['P10_LOGVAC'] / logement['P10_LOG'],
        l_nbpers=logement['P10_NPER_RP'] / logement['P10_RP'],
    )
    out = out.merge(logement[['IRIS', 'tx_l_2piec', 'tx_l_5piec', 'tx_l_vacant', 'l_nbpers']],
                     on='IRIS', how='left')

    out = out.rename(columns={'IRIS': 'iris'})
    return out


if __name__ == '__main__':
    dossier = 'data/processed'
    panel_iris = pd.read_csv(f'{dossier}/panel_iris_complet_v2.csv', dtype={'iris': str, 'com': str})
    qpv_info = pd.read_csv(f'{dossier}/qpv_info_nom_commune.csv', dtype={'code': str, 'insee_com': str})
    rpls_iris = pd.read_csv(f'{dossier}/rpls_iris.csv', dtype=str)
    candidats = miroirs.construire_iris_candidats(panel_iris, qpv_info, rpls_iris)

    demo_iris = construire_demographie_iris()
    demo_iris_candidats = candidats.merge(demo_iris, on='iris', how='left')

    print(f"IRIS candidats : {len(candidats)}")
    print(f"IRIS candidats avec démographie 2010 : {demo_iris_candidats['tx_f'].notna().sum()}")
    for col in demo_iris.columns:
        if col == 'iris':
            continue
        pct_manquant = demo_iris_candidats[col].isna().mean() * 100
        print(f"  {col} : {pct_manquant:.1f}% manquant")

    demo_iris_candidats[['iris', 'com'] + [c for c in demo_iris.columns if c != 'iris']].to_csv(
        f'{dossier}/demographie_2010_iris.csv', index=False)
