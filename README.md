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
- `scripts/` — scripts de construction du panel, un fichier par étape
- `data/processed/` — jeux de données déjà construits (panels intermédiaires)
- `data/raw/` — **non versionné** (voir .gitignore) : fichiers bruts INSEE,
  trop volumineux et librement retéléchargeables depuis data.gouv.fr / insee.fr

## Sources de données

Voir `carnet/carnet.md` section 2 pour le détail complet des sources et de
leur disponibilité (années, niveaux géographiques, limites connues).

## État d'avancement

Voir `carnet/carnet.md`, mis à jour à chaque session de travail.
