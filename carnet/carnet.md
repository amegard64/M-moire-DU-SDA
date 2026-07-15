# Carnet de bord — Mémoire QPV et trajectoires de revenu

*Document de travail : trace toutes les décisions méthodologiques et leur justification, au fur et à mesure. Sert de brouillon pour la section "Données" du mémoire — sera à condenser et reformuler pour la version finale, pas à copier tel quel.*

---

## 1. Question de recherche

Le classement d'un quartier en Quartier Prioritaire de la Politique de la Ville (QPV) en 2015 a-t-il eu un effet causal sur les trajectoires de revenu et de pauvreté de ses habitants ?

**Logique retenue** : différence de différences (DiD), implémentée comme régression à effets fixes + interaction traitement × période (extension du panel data vu en cours, la DiD elle-même n'étant pas enseignée telle quelle).

## 2. Sources de données identifiées et confirmées disponibles

| Source | Contenu | Années | Niveau géo |
|---|---|---|---|
| INSEE — Revenus, pauvreté et niveau de vie (QPV 2015) | Médiane, quartiles/déciles, Gini, S80/S20, taux pauvreté 60%, décomposition du revenu | 2012-2021 | QPV |
| INSEE — Revenus, pauvreté et niveau de vie (IRIS) | Mêmes indicateurs | 2012-2021 (2012 et 2015 à confirmer) | IRIS |
| Table de correspondance QP2024 ↔ QP2015 | Lien entre les deux générations de zonage | Statique | — |
| Liste QP2024 avec commune (`listeqp2024-cog2024.csv`) | Code commune de chaque QP2024 | Statique | — |
| Table d'appartenance géographique QPV (TAG_QPV_2015) | Lien direct QP2015 → commune/EPCI/UU | Par millésime | — |

## 3. Limites méthodologiques identifiées (à documenter dans le mémoire)

1. **Rupture de géoréférencement en 2019** : méthode de localisation des ménages améliorée à partir du millésime 2019 → ne pas comparer naïvement des années de part et d'autre de cette rupture.
2. **Bruit Covid 2020-2021** : plusieurs aides exceptionnelles (PEPA, fonds de solidarité entreprises, indemnité inflation) mal ou pas captées par Filosofi ces années-là.
3. **Couverture géographique** : les indicateurs de revenu QPV/IRIS couvrent France métropolitaine, Martinique, La Réunion — pas Guadeloupe, Guyane, Mayotte, Polynésie.
4. **Secret statistique** : ~22% des QPV ont une médiane de revenu masquée dans le fichier 2021 (à vérifier si ce taux est stable sur les autres années).
5. **Couverture IRIS variable dans le temps** : jusqu'au millésime 2019, IRIS des communes ≥10 000 hab. ; à partir de 2019, ≥5 000 hab. → fixer un périmètre de communes constant sur toute la période pour éviter un changement de composition de l'échantillon de contrôle.
6. **Seul le thème "Revenus, pauvreté et niveau de vie" couvre la période pré-2015** — tous les autres thèmes (emploi, éducation, logement, tissu économique) démarrent entre 2015 et 2021 selon le thème, donc ne permettent pas de test de tendance parallèle pré-traitement.

## 4. Construction du groupe de traitement et de contrôle

**Groupe traité** : les QPV (génération 2015), identifiés par leur code `QP...`.

**Groupe de contrôle — décision prise** : IRIS non-QPV, dans la même commune, avec un niveau de pauvreté pré-traitement (2012-2014) comparable à celui du QPV. Deux raffinements décidés :
- **Exclusion des IRIS dont le nom correspond visiblement à un QPV** (ex. IRIS "Croix Blanche" dans une commune où existe un QPV "Croix Blanche") — ces IRIS chevauchent probablement le QPV lui-même et ne peuvent pas servir de contrôle.
- **Rejet de l'option "tous les IRIS non-QPV de la commune, y compris les plus aisés"** : incohérent avec la question de recherche (isoler l'effet du classement, pas l'écart pauvre/riche). Peut être gardé en indicateur secondaire, pas comme identification causale principale.

## 5. Étapes techniques réalisées

| Étape | Résultat | Statut |
|---|---|---|
| Jointure QP2015 → QP2024 → commune (via fichiers déjà en main, sans attendre TAG_QPV_2015) | 1422/1514 QP2015 avec correspondant 2024 (92 manquants, dont 44 hors-champ car Outre-mer/Mayotte non couvert par les données de revenu) | ✅ Fait (prototype 2021) |
| Chargement fichier revenu QPV 2021 | 1352 QPV présents, 1047 avec médiane non masquée | ✅ Fait |
| Chargement fichier IRIS général 2021 | 16 026 IRIS | ✅ Fait |
| Vérification sur cas réel (Bourg-en-Bresse) | Confirme la présence d'IRIS "miroirs" des QPV (à exclure du contrôle) | ✅ Fait |
| Exclusion des IRIS "miroirs" par nom (similarité de Jaccard sur les mots du nom, seuil 0.5) | 761/8293 IRIS candidats exclus (~9%). Vérification manuelle sur plusieurs cas : matchs plausibles, pas de faux positif détecté. **Limite à documenter** : approximation par les noms, pas une vérification géographique réelle (pas de croisement de polygones, hors cours) | ✅ Fait (méthode validée sur 2021) |
| Récupération données IRIS et QPV 2012-2014 (pré-traitement) | — | 🔲 À faire — nécessaire pour l'appariement sur pauvreté pré-traitement (bloquant pour la suite) |
| Récupération années manquantes (2012-2020 sauf 2021 déjà en main) | — | 🔲 À faire |
| Fixer le périmètre de communes (≥10 000 hab. constant) | — | 🔲 À faire |
| Construction du panel complet | — | 🔲 À faire |
| Vérification visuelle des tendances parallèles pré-2015 | — | 🔲 À faire |
| Spécification et estimation de la régression | — | 🔲 À faire |

## 5bis. Validation manuelle de l'exclusion par nom

25 cas vérifiés manuellement au total (15 lors du premier passage + 10 tirés aléatoirement dans des communes non revues), répartis sur des communes variées, y compris deux communes à 9 QPV chacune où la méthode a correctement associé chaque IRIS au bon QPV parmi de nombreux candidats. **Zéro faux positif détecté.** Méthode considérée suffisamment fiable pour être utilisée comme construction du groupe de contrôle, avec la limite documentée en 5. conservée dans le mémoire (faux négatifs possibles : chevauchement réel non détecté si les noms diffèrent).

## 5ter. Indicateur secondaire retenu : comparaison QPV vs ensemble de la commune

En complément (pas en remplacement) du groupe de contrôle apparié : comparer chaque QPV à la moyenne de sa commune d'accueil. Sert à répondre à une question différente et complémentaire : convergence ou divergence du QPV par rapport à sa ville, et neutralisation des chocs locaux communs à toute la commune (ex. fermeture d'un employeur majeur, boom immobilier) qu'une comparaison à des IRIS d'autres villes ne capterait pas.

## 5quater. Piste ML envisagée (à trancher plus tard, pas urgent)

Utiliser les thèmes hors revenu (emploi, éducation, logement, démographie), qui ne couvrent pas la période pré-2015 et ne peuvent donc pas servir à une DiD causale, comme matière pour un volet ML complémentaire. Deux pistes identifiées :
- **Typologie des QPV par clustering** (hiérarchique ou DBSCAN) à partir des variables démographie/emploi/éducation/logement, puis croisement avec l'hétérogénéité de l'effet DiD selon le type de quartier — connecte les deux volets du mémoire.
- **Modèle prédictif + interprétabilité** (random forest / boosting) pour expliquer la pauvreté en coupe transversale à partir des autres thématiques.
Décision entre les deux pas encore prise.

## 7. Millésime 2013 — découvertes structurelles (à documenter comme limites/précautions)

1. **Le taux de pauvreté (TP60) n'est pas dans le même fichier selon les années** : en 2021, il est dans le fichier "revenu disponible" (`DISP_TP6021`) ; en 2013, il est dans le fichier "socio-démographique" séparé (`TP60_A13`). Les noms de colonnes changent aussi de convention (majuscules/suffixe année en 2021 vs minuscules en 2013) — ne jamais supposer une correspondance directe de nom de colonne entre deux millésimes, toujours vérifier.
2. **Couverture géographique incohérente à l'intérieur même du millésime 2013** : fichier "revenu disponible" = France métropolitaine seule (1296 QPV) ; fichier "socio" = métropole + Martinique + La Réunion (1352 QPV). Fusion : 56 QPV d'Outre-mer avec pauvreté/socio mais sans revenu détaillé.
3. **Ligne d'agrégat national mêlée aux données** : chaque fichier contient une première ligne "Ensemble des quartiers prioritaires de la politique de la ville" qui n'est pas un QPV réel — à retirer systématiquement (repérable par l'absence de code commençant par "QP").
4. **Fichier socio-démographique disponible seulement 2012-2014** (confirmé par Alexandre) — utile pour construire une typologie de QPV **avant traitement**, bien adapté à l'usage prévu (typologie pour hétérogénéité de l'effet), pas une contrainte pour ce cas d'usage précis.

## 8. Panel 2013 construit (prototype)

Fusion revenu disponible × socio-démographique 2013 réalisée : 1352 QPV au total (1296 avec revenu détaillé + socio, 56 Outre-mer avec socio/pauvreté seulement). Fichier : `panel_qpv_2013.csv`.

## 9. Décision prise : besoin de plusieurs années pré-traitement, pas une seule

Correction d'un choix pris trop vite : pour vérifier les tendances parallèles avant 2015, il faut plusieurs points temporels pré-traitement (2012, 2013, 2014), pas une seule année isolée. 2013 est en cours de traitement ; 2012 et 2014 restent à récupérer (QPV + IRIS), de même que l'IRIS 2013 (encore en attente au moment de la rédaction de cette entrée).



## 6. Décisions en attente / à trancher

## 10. Décision : périmètre restreint à la France métropolitaine

Décision prise avec Alexandre : on exclut les DOM-TOM (Guadeloupe, Martinique, Guyane, Réunion, Mayotte, Polynésie, Saint-Martin) du champ de l'analyse. Justifications :
- Couverture des données incohérente et incomplète en Outre-mer (fichiers pas toujours disponibles, périmètres différents d'un fichier à l'autre au sein même d'un millésime)
- **Différence de méthode d'identification des QPV** : en métropole/Martinique/Réunion, classement sur critère de revenu (RFL 2011) ; dans les autres DOM, classement à partir du recensement à l'IRIS — un mécanisme d'assignation du traitement différent, ce qui rend une analyse causale unifiée métropole+DOM méthodologiquement discutable de toute façon
- Contextes économiques et sociaux trop différents pour un même modèle de comparaison
→ Panels 2013 et 2021 déjà filtrés en conséquence (1296 QPV métropole sur 2013, cohérent avec le total officiel).

## 11. Correction sur le paysage des données "autres thèmes" (pour le volet ML)

Ce qu'on croyait au départ (thèmes hors revenu = démarrent seulement après 2015) est trop simpliste. Vérifié concrètement : le thème "Démographie" (piloté par l'ANCT à partir de 2017, sources INSEE recensement + CNAF) contient des variables très proches de celles du fichier socio-démographique 2012-2014 (ex. nombre de familles monoparentales). **Ce n'est donc pas une absence de données après 2015, mais une réorganisation** : mêmes concepts, sources différentes (Filosofi avant / recensement+CNAF après), avec un trou 2015-2016 et un changement de méthodologie à documenter comme rupture — moins grave qu'une vraie absence de données, mais toujours une précaution à prendre pour la typologie ML si on veut comparer des caractéristiques de part et d'autre de 2015.

## 12. Note technique (bug corrigé)

Premier essai de filtrage DOM-TOM sur le panel 2013 basé sur une colonne "reg" perdue pendant une fusion précédente (colonne non incluse dans les colonnes du fichier socio récupérées) — filtre inefficace, corrigé en utilisant le préfixe du code QPV lui-même (ex. QP972 = Martinique) qui est plus fiable. Résultat vérifié : 1296 QPV métropole, cohérent avec le total officiel.


## 14. Panel 2012-2014 construit (QPV et IRIS)

**QPV** (`panel_qpv_2012_2014.csv`) : fusion revenu disponible × socio par année, empilées. 2012 : 1294 QPV métropole ; 2013 et 2014 : 1296 chacun. Variables harmonisées : `revenu_median`, `taux_pauvrete`, `gini`, `s80s20` (absent en 2012), `part_monoparental`, `part_locataires`.

**IRIS** (`panel_iris_2012_2014.csv`) : `revenu_median` et `taux_pauvrete` uniquement (pas de socio pour les IRIS), extraits par nom de colonne technique (`DISP_MEDxx`, `DISP_TP60xx`, cohérent sur les 3 années malgré des présentations différentes). 2012 : 11 721 IRIS ; 2013 : 11 737 ; 2014 : 12 209. Aucune valeur manquante sur ces deux variables.

**Découvertes structurelles supplémentaires (à documenter comme précautions techniques)** :
- La position de la ligne d'en-tête technique varie d'un fichier à l'autre (ligne 5 pour certains, 6 ou 8 pour d'autres) — détection automatique mise en place plutôt que position fixe, pour éviter une erreur silencieuse.
- Noms de feuilles Excel légèrement différents selon les années ("Données quartier" vs "Données quartiers" vs "Donnees quartier" sans accent) — encore un signe qu'il ne faut jamais rien supposer stable d'un millésime à l'autre.
- **2012 n'a ni Gini ni S80/S20** (ni QPV ni IRIS) — seules médiane et taux de pauvreté sont exploitables sur toute la période 2012-2021 sans trou.
- Le fichier IRIS 2012 a une structure différente (colonnes de dénombrement en plus, présentation par déciles directe) mais les noms techniques des variables clés (`DISP_MED12`, `DISP_TP6012`) restent cohérents avec les autres années — confirmé en vérifiant l'en-tête technique, pas la présentation visuelle.
- Légère précision décimale inhabituelle sur certaines valeurs IRIS (plusieurs chiffres après la virgule) — probablement juste la précision brute du fichier source sous-jacente à l'arrondi affiché ailleurs par l'INSEE, pas une anomalie identifiée à ce stade.

## 15. État d'avancement

On a maintenant les deux côtés (QPV traité + IRIS contrôle) pour 2012, 2013, 2014, et 2021. Prochaine étape réelle : finaliser la construction du groupe de contrôle (exclusion par nom + appariement sur pauvreté pré-traitement, en utilisant maintenant les vraies données 2012-2014), puis produire le graphique de vérification des tendances parallèles.



- Seuil de proximité pour l'appariement sur pauvreté pré-traitement (ex. ± X points de taux de pauvreté, ou méthode de matching plus formelle ?)
- Périmètre exact de communes de comparaison (seuil de population à fixer sur toute la période)
- Composition exacte du volet ML "typologie" : quelles variables du fichier socio 2012-2014 (et/ou du thème Démographie 2017+) retenir précisément
## 16. Décisions en attente / à trancher

- Seuil de proximité pour l'appariement sur pauvreté pré-traitement (ex. ± X points de taux de pauvreté, ou méthode de matching plus formelle ?)
- Périmètre exact de communes de comparaison (seuil de population à fixer sur toute la période)
- Composition exacte du volet ML "typologie" : quelles variables du fichier socio 2012-2014 (et/ou du thème Démographie 2017+) retenir précisément

## 17. Appariement finalisé (commune + repli unité urbaine)

Table commune -> unité urbaine (UU2020) obtenue via la Table d'appartenance géographique des communes (INSEE, millésime 2026). Règle d'appariement à deux niveaux : même commune en priorité, repli sur l'unité urbaine si aucun IRIS candidat en commune.

Résultat : 1015/1248 QPV appariés (81%, contre 888/1248 soit 71% avec la seule règle "commune"). 233 QPV toujours sans contrôle (bassins urbains trop petits pour contenir un seul IRIS). Fait notable : les appariements de repli (niveau unité urbaine) sont en moyenne MEILLEURS (distance moyenne 5,6 points) que les appariements en commune stricte (14,2 points) — plus de candidats disponibles dans une zone plus large permet un meilleur choix parmi eux.

Fichier `panel_qpv_2013_metropole.csv` retiré du dépôt (redondant avec `panel_qpv_2012_2014.csv`, gardé par erreur lors d'une étape antérieure).

Décision en attente mise à jour : le seuil/méthode d'appariement (K=5 plus proches voisins) est maintenant stabilisé à deux niveaux commune/UU ; reste à décider si on garde tous les appariements (y compris les moins bons, ~20+ points d'écart) ou si on fait un test de robustesse sur le sous-ensemble le mieux apparié (voir section 16, option (c) recommandée, décision encore ouverte).
