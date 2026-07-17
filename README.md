# Mémoire DU Data Analytics — Effet causal du classement QPV sur les trajectoires de revenu

Question de recherche : le classement d'un quartier en Quartier Prioritaire
de la Politique de la Ville (QPV) en 2015 a-t-il eu un effet causal sur les
trajectoires de revenu et de pauvreté de ses habitants ?

Design : différence de différences (panel à effets fixes + interaction
traitement × période), groupe traité = QPV, groupe de contrôle = IRIS
non-QPV appariés sur le niveau de pauvreté pré-traitement.

## Structure du dépôt

- `carnet/carnet.md` — journal de bord : toutes les décisions méthodologiques,
  leur justification, et les limites identifiées. Sert de brouillon pour la
  section "Données" et "Limites" du mémoire.
- `scripts/` — scripts de construction du panel, un fichier par étape (voir
  ci-dessous)
- `data/processed/` — jeux de données déjà construits (panels intermédiaires)
- `data/raw/` — **non versionné** (voir .gitignore) : fichiers bruts INSEE,
  trop volumineux et librement retéléchargeables depuis data.gouv.fr / insee.fr

## Pipeline (scripts/)

Chaque script part des sorties du précédent. Les scripts 01-03 lisent des
fichiers INSEE bruts (`data/raw/`, non versionné) ; les scripts 04-07 ne
lisent que des fichiers déjà committés dans `data/processed/` et sont donc
exécutables tels quels dans ce dépôt.

| Script | Entrée principale | Sortie |
|---|---|---|
| `01_build_panel_qpv.py` | `data/raw/qpv_{annee}/*` | `panel_qpv_complet.csv` |
| `02_build_panel_iris.py` | `data/raw/iris_{annee}/*` | `panel_iris_complet.csv` |
| `03_controle_iris_miroirs.py` | tables de correspondance QP2015/QP2024 | fonctions utilisées en amont de `iris_controle_candidats.csv` |
| `04_appariement_qpv_iris.py` | `qpv_pauvrete_pretraitement.csv`, `iris_pauvrete_pretraitement.csv`, `commune_vers_unite_urbaine.csv` | `appariement_qpv_iris_v2.csv` |
| `05_construire_panel_regression.py` | `panel_qpv_complet.csv`, `panel_iris_complet.csv`, `appariement_qpv_iris_v2.csv` | `panel_regression.csv` |
| `06_fusion_rpls.py` | `panel_regression.csv`, `{qpv,iris}_rpls_clean.csv` | `panel_regression_v2.csv` |
| `07_event_study.py` | `panel_regression.csv`, `panel_regression_v2.csv` | `event_study_resultats.json`, `event_study_resultats_v2.json`, `tendance_complete_2012_2021.csv` |

Les scripts 04 à 07 ont été reconstruits a posteriori (2026-07-17) à partir
des fichiers `data/processed/` déjà committés — 04, 05 et 06 reproduisent
leur fichier de sortie à l'identique (diff vide), 07 reproduit les
coefficients de régression à la précision flottante près. Les extensions
2016-2019 des scripts 01/02 n'ont en revanche pas pu être testées dans cet
environnement (fichiers bruts INSEE non disponibles ici) — à vérifier avant
de leur faire confiance.

### Fichiers `_v2` dans `data/processed/`

Plusieurs fichiers existent en deux versions, ce ne sont pas des doublons
accidentels mais des étapes successives du projet :
- `appariement_qpv_iris.csv` (v1, appariement commune stricte, 888 QPV) est
  une étape intermédiaire antérieure, remplacée par `appariement_qpv_iris_v2.csv`
  (repli unité urbaine + couverture TAG_QPV_2015, 1246 QPV) — **v2 fait foi**.
- `panel_regression.csv` (sans contrôle logement social) et
  `panel_regression_v2.csv` (avec contrôle logement social, voir carnet
  section 24-25) sont **deux spécifications volontairement distinctes**,
  toutes deux utilisées (voir `07_event_study.py`) — ce ne sont pas une
  version et son remplacement.
- `tendance_qpv_vs_controle_2012_2014.csv` et `tendance_qpv_vs_controle_complet.csv`
  sont des instantanés d'étapes intermédiaires du projet (avant l'ajout des
  années 2016-2019) : `tendance_complete_2012_2021.csv` est la version
  actuelle et complète, conservée à jour par `07_event_study.py`.

## Sources de données

Voir `carnet/carnet.md` section 2 pour le détail complet des sources et de
leur disponibilité (années, niveaux géographiques, limites connues).

## État d'avancement

Voir `carnet/carnet.md`, mis à jour à chaque session de travail.
