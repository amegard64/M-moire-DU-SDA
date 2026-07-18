# Brief de travail — approfondissement de la partie régression

Ce document liste 5 chantiers décidés avec Alexandre suite à une discussion approfondie sur les limites du design (voir carnet section 38 et `redaction/limites_consolidees.md`). Priorisés du plus simple (aucune nouvelle donnée) au plus lourd (nouvelle donnée à intégrer). **Documenter chaque résultat dans `carnet/carnet.md` au fur et à mesure, à la suite de la section 38.**

---

## Chantier 1 (facile, aucune nouvelle donnée) — Réestimer sans 2020

**Objectif** : vérifier que l'exclusion de 2020 (déjà justifiée par l'inversion de signe avec 2021) ne change pas les coefficients des autres années.

**Comment** : reprendre `scripts/04_regression_event_study.py`, filtrer `reg_data` pour exclure `annee == 2020`, réestimer avec la même spécification (référence poolée 2012-2014, panel équilibré). Comparer les coefficients de 2015/2016/2017/2018/2019/2021 à la version avec 2020 inclus — ils doivent être quasi identiques (petites variations dues au recalcul des effets fixes année, rien de plus).

**Sortie attendue** : tableau comparatif avant/après exclusion de 2020, à documenter dans le carnet.

---

## Chantier 2 (facile, aucune nouvelle donnée) — Appariement communal strict (sans repli unité urbaine)

**Objectif** : vérifier si le repli sur l'unité urbaine (quand aucun IRIS n'existe dans la commune) change les résultats, ou si c'est neutre/bénéfique.

**Comment** : `data/processed/appariement_qpv_iris_v2.csv` contient une colonne `niveau` (`'commune'` ou `'unite_urbaine'`). Filtrer pour ne garder que les lignes `niveau == 'commune'`, reconstruire le panel de régression sur ce sous-ensemble uniquement, réestimer, comparer au résultat complet (qui inclut le repli).

**Sortie attendue** : tableau comparatif, + un commentaire sur la taille d'échantillon résultante (sera plus petite, cf. carnet section 17-18 : 888 QPV en communal strict contre 1246 avec repli).

---

## Chantier 3 (nouvelle donnée à télécharger, mais simple) — Logement social en proportion, pas en nombre absolu

**Objectif** : remplacer le contrôle logement social actuel (nombre absolu de logements sociaux, `nbLsPls`) par une vraie proportion (logements sociaux / total des logements).

**Donnée manquante à récupérer** : la base infracommunale IRIS "Logement" de l'INSEE, qui donne le nombre total de logements par IRIS. Utiliser le millésime 2022 pour rester cohérent avec le RPLS 2022 déjà utilisé :
- Page : `insee.fr/fr/statistiques/8647012` (chercher le fichier IRIS, format XLSX/CSV)
- Variable technique attendue : un champ du type `P22_LOG` (nombre total de logements) — vérifier le nom exact une fois le fichier ouvert, ne pas supposer.
- Fera aussi l'affaire pour le fichier QPV si une version "quartiers 2015" existe pour ce produit (vérifier sur la même page, sommaire similaire aux autres produits QPV) ; sinon, calculer le total de logements QPV par agrégation depuis les IRIS qui le composent n'est pas possible directement (géographies différentes) — dans ce cas, utiliser la population QPV comme dénominateur de repli et le signaler comme approximation.

**Comment** : recalculer `logement_social_proportion = nbLsPls / total_logements` (au lieu de `nbLsPls` brut), standardiser, refaire l'interaction avec l'année exactement comme pour la version en nombre absolu (cf. section 25 du carnet), comparer les deux versions du contrôle.

**Sortie attendue** : le contrôle en proportion absorbe-t-il plus, moins, ou autant du signal que la version en nombre absolu ?

---

## Chantier 4 (le plus lourd, nouvelle donnée substantielle) — Score de propension multivarié

**Objectif** : remplacer l'appariement univarié (seule la pauvreté pré-traitement) par un score de propension construit sur plusieurs caractéristiques pré-traitement (régression logistique, dans le cadre du cours — cf. `Statistics_Slides_bin_choice.pdf`).

**Donnée manquante, importante à signaler avant de commencer** : on a `data/processed/demographie_2010_qpv.csv` (62 variables démographiques) **côté QPV uniquement**. Il n'existe **aucun équivalent côté IRIS de contrôle** dans le dépôt actuel. Sans ça, impossible de construire un vrai score de propension (qui a besoin des mêmes variables des deux côtés, traité et contrôle).

**Deux options, à soumettre à Alexandre avant de choisir :**
- (a) Chercher et télécharger l'équivalent IRIS de ces variables (recensement de la population, données socio-démographiques par IRIS, millésime proche de 2010 si possible) — plus long, mais rigoureux.
- (b) Construire un score de propension "allégé", limité aux variables déjà disponibles des deux côtés (taux de pauvreté pré-traitement, revenu médian pré-traitement — pas les 62 variables démographiques) — faisable immédiatement, mais moins riche que ce qu'Alexandre a en tête.

**Ne pas décider seul entre (a) et (b) — redemander à Alexandre si ambigu**, conformément à la règle de travail du projet (pas de méthodologie engagée sans validation explicite).

**Si (a) choisi** : une fois la donnée en main, régression logistique (QPV=1 / IRIS candidat=0) sur les variables pré-traitement des deux côtés, calcul du score prédit, ré-appariement par plus proche voisin sur ce score plutôt que sur la seule pauvreté, comparaison des deux méthodes d'appariement (qualité de match, résultats de la régression event-study).

---

## Chantier 5 (faisable maintenant, aucune nouvelle donnée) — Balayage systématique des variables démographiques 2010

**Objectif** : au lieu de tester une hypothèse à la fois (logement social, puis population), tester systématiquement chacune des 62 variables de `demographie_2010_qpv.csv` en interaction avec l'année, pour voir lesquelles absorbent le plus de signal — une version automatisée et exhaustive de ce qui a été fait à la main pour le logement social et la population (cf. carnet sections 25 et 36).

**Important, pas besoin de donnée IRIS pour ce chantier** (contrairement au chantier 4) : on utilise la même logique que le test de population (section 36) — chaque IRIS de contrôle hérite du groupe/de la valeur de SON QPV apparié. On n'a pas besoin de la caractéristique côté IRIS lui-même pour faire cette analyse d'hétérogénéité.

**Comment** :
1. Pour chaque variable numérique de `demographie_2010_qpv.csv` (exclure les doublons redondants — colonnes découpées par sexe/nationalité qui répètent un total déjà présent, cf. carnet section précédente sur les 62 variables) :
   - Standardiser la variable (z-score)
   - Merger sur `unit_id` (QPV directement, IRIS via son QPV apparié — voir la logique déjà écrite dans `scripts/05_tests_robustesse.py`, fonction `test_heterogeneite_evolution_population`, à généraliser)
   - Interagir avec chaque année, ajouter à la régression de base (comme le contrôle logement social)
   - Noter : (a) la réduction en % du coefficient traité×année pour les années significatives (2015,2016,2018,2021), (b) si l'interaction elle-même est significative
2. Trier les 62 variables par ampleur de réduction du signal — présenter un tableau des 10-15 variables les plus "explicatives"

**Attention à signaler dans le carnet** : tester 62 variables une par une augmente le risque de trouver des résultats significatifs par pur hasard (problème de tests multiples). Ne pas présenter le résultat le plus fort comme une certitude — le signaler explicitement comme exploratoire, pas confirmatoire, exactement comme on l'a fait pour le premier balayage de corrélations (carnet, avant section 36).

---

## Ordre d'exécution recommandé

1. Chantier 1 (rapide, confirme un acquis)
2. Chantier 2 (rapide, confirme un acquis)
3. Chantier 5 (faisable tout de suite, riche en enseignements, pas de nouvelle donnée)
4. Chantier 3 (une donnée à récupérer, ciblée)
5. Chantier 4 (le plus lourd — statuer d'abord avec Alexandre sur l'option (a) ou (b) avant de s'y lancer)
