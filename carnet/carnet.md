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

## 18. Couverture finale du groupe de contrôle (avec TAG_QPV_2015)

Le fichier TAG_QPV2015_2025 (fourni par Alexandre) remplace la méthode de contournement par QP2024 pour le lien QPV -> commune : 1436 QPV avec commune (contre 1422 avant), et surtout 89 des 92 QPV auparavant sans correspondance sont désormais couverts. Petite approximation documentée : pour les QPV à cheval sur plusieurs communes (141 cas sur 1436), seule la première commune listée est retenue comme commune de rattachement principale.

Pipeline entièrement relancé avec cette couverture améliorée :
- QPV avec pauvreté pré-traitement + commune connue : 1296 (contre 1248)
- IRIS candidats (communes avec QPV) : 9257, dont 877 exclus comme miroirs
- **Appariement final (commune, repli unité urbaine, K=5 plus proches voisins sur pauvreté 2012-2014) : 1246/1296 QPV appariés (96%), 50 sans aucun contrôle disponible**

C'est la version considérée comme définitive du groupe de contrôle pour la suite (vérification des tendances parallèles, puis régression).

## 19. Extension 2016-2019 (option A choisie)

Fichiers 2016 (.xls) et 2017-2019 (.xlsx) traités. Découvertes :
- Taux de pauvreté déjà présent dans le fichier "revenu disponible" dès 2016 (plus besoin du fichier socio séparé comme pour 2012-2014) — la bascule s'est donc produite entre 2014 et 2016 exactement.
- Convention de nommage des colonnes change aussi entre 2017 (minuscules, `disp_q2_a17`) et 2018 (majuscules, `DISP_MED_A18`).
- IRIS : ~23% de valeurs de pauvreté manquantes (secret statistique), cohérent avec les autres années.
- Bug de lecture corrigé : la détection automatique de ligne d'en-tête prenait la ligne "lisible" au lieu de la ligne technique (toutes deux commencent par "IRIS") — corrigé en vérifiant aussi que la 2e colonne vaut "LIBIRIS".

**Panel complet désormais disponible : 2012, 2013, 2014, 2016, 2017, 2018, 2019, 2021** (2015 et 2020 volontairement exclus : 2015 ambiguë sur le statut de traitement, 2020 fiable sur le statut mais pas sur la mesure - bruit Covid).

Trajectoire QPV vs contrôle (groupes appariés, moyennes) : pas de rupture nette visible autour de 2015-2016 dans les moyennes agrégées ; les deux séries progressent de façon relativement régulière. Le taux de pauvreté fluctue dans une bande assez étroite pour les deux groupes (QPV : 41,7-45,1% ; contrôle : 26,7-28%) sans divergence flagrante. **Ceci reste une lecture purement descriptive de moyennes agrégées — ne remplace pas la régression event-study à faire.**

Prochaine étape : spécifier et estimer la régression event-study (effets fixes + interaction traitement × année).

## 20. Synthèse à intégrer au mémoire : justification du choix du groupe de contrôle

Trois points distincts à préciser explicitement dans la méthodologie (identifiés suite aux questions d'Alexandre) :

**1. Pourquoi les IRIS de contrôle doivent être pauvres (et pas juste "non-QPV")** : les QPV ont été sélectionnés sur leur pauvreté en 2011. Le niveau de pauvreté est corrélé au rythme d'évolution attendu (convergence/retour à la moyenne des zones très pauvres). Un contrôle à niveau très différent n'aurait donc probablement pas évolué au même rythme, violant l'hypothèse de tendance parallèle — indépendamment de toute politique.

**2. Pourquoi des IRIS pauvres non-QPV existent** : le classement QPV repose sur (a) un seuil relatif au bassin urbain d'appartenance (pas un seuil national absolu), (b) un critère de concentration géographique et de taille de population minimale, (c) un ajustement politique local post-identification statistique, (d) un effet de seuil net sur un critère continu. Des zones presque aussi pauvres qu'un QPV mais non classées existent donc naturellement.

**3. Pourquoi l'écart de niveau résiduel après appariement n'est pas rédhibitoire** : la DiD neutralise mathématiquement tout écart de niveau stable dans le temps (voir démonstration : le double différenciement élimine les effets fixes de niveau). L'écart de niveau n'est un problème que s'il s'accompagne d'un écart de *rythme d'évolution* — précisément ce que l'appariement sur la pauvreté vise à éviter, et ce que la vérification empirique des tendances pré-2015 (quasi identiques malgré l'écart de niveau) vient corroborer.

Brouillon de paragraphe rédigé pour la section méthodologie (voir réponse Claude du [session en cours] pour le texte complet) — à retravailler mais la structure logique est posée.

## 21. Références bibliographiques confirmées : retour à la moyenne / biais d'Ashenfelter

Trois niveaux à citer dans le mémoire (revue de littérature méthodologique) :

1. **Galton, F. (1886)**, "Regression Towards Mediocrity in Hereditary Stature" — le mécanisme statistique de base (régression vers la moyenne). Quasi-mécanique : se manifeste dès que la corrélation entre deux mesures est <1 (Britannica).
2. **Ashenfelter, O. (1978)**, sur les programmes de formation professionnelle — traduction du phénomène en biais d'évaluation de politiques publiques ("Ashenfelter's dip"), très largement cité depuis. Explicitement relié aux designs DiD combinant ciblage géographique/éligibilité (cf. notes de cours MIT/Harvard 14.771/2390b).
3. **Rathelot, R. & Sillard, P. (2008)**, "Zones Franches Urbaines : quels effets sur l'emploi salarié et les créations d'établissements ?", Économie et Statistique n°415-416 ; et **Givord, Rathelot & Sillard (2011/2013)**, "Place-based tax exemptions and displacement effects", Regional Science and Urban Economics — application quasi-identique en France sur les ZFU (ancêtre méthodologique des QPV), utilisant explicitement un groupe de contrôle apparié pour cette même raison.

Point clé pour la rédaction : le mécanisme de base (1) est une quasi-loi statistique ; son ampleur dans un contexte donné reste une question empirique (2 et 3), ce qui justifie la stratégie d'appariement retenue plutôt qu'une simple affirmation de principe.

## 22. Découverte majeure (apportée par Alexandre) : ruptures méthodologiques Filosofi documentées, coïncidant avec les années significatives

L'INSEE documente explicitement, pour chaque millésime, des changements de législation/qualité de source qui affectent la comparabilité. Deux notes trouvées et très pertinentes :

**2018** : réforme du loyer de solidarité (RLS) — comptabilise la baisse des APL sans la baisse de loyer compensatoire, **ne touche que le logement social**. Dégradation du fichier taxe d'habitation la même année, avec sortie du champ des ménages aux revenus modestes en particulier.

**2019** : primes exceptionnelles et heures supplémentaires exonérées non captées par Filosofi (écart de +2,6% vs -0,2% entre ERFS et Filosofi sur le niveau de vie médian national) — touchent surtout "ouvriers, employés". Prime d'activité élargie. Amélioration (partielle compensation) du fichier taxe d'habitation cette année-là contrairement à 2018.

**Avertissement général INSEE, répété sur presque chaque millésime** : "il est déconseillé d'utiliser deux millésimes consécutifs pour mesurer des évolutions."

**Implication pour nos résultats** : les années où la régression event-study trouve un écart significatif (2016, 2018, 2021) incluent au moins deux (2018 documenté ci-dessus, 2021 déjà documenté pour le Covid) qui coïncident avec des ruptures de mesure connues, touchant potentiellement de façon disproportionnée les caractéristiques surreprésentées en QPV (logement social notamment pour la RLS 2018). **Ça affaiblit sérieusement l'interprétation causale du résultat sur le taux de pauvreté** — une partie substantielle pourrait être un artefact de mesure plutôt qu'un effet réel de la politique.

**À faire avant toute conclusion** :
- Vérifier si 2016 a une explication méthodologique documentée similaire (pas encore recherché)
- Envisager une spécification alternative excluant les années à rupture documentée (2018, 2021), ne gardant que 2016, 2017, 2019 comme post-traitement "propre"
- Mentionner explicitement cette limite dans le mémoire, avec citation des notes méthodologiques INSEE par millésime

## 23. Vérification 2016 : pas de rupture méthodologique spécifique documentée

Contrairement à 2018/2019/2021, la documentation INSEE 2016 ne mentionne que la mise en garde générique standard, sans changement législatif ou de qualité de source spécifique. 2016 reste donc un résultat significatif sans explication de mesure identifiée — à traiter différemment de 2018/2021 dans la discussion des limites (peut-être un vrai signal précoce, peut-être un résultat significatif par hasard sur plusieurs tests, à ne pas trancher prématurément).

Prochaine étape décidée : réestimer la régression event-study en excluant 2018 et 2021 (ruptures documentées confirmées), pour isoler ce qui reste de 2016/2017/2019 seuls.

## 24. Vérification confirmée : les QPV ont bien plus de logement social que leurs contrôles appariés

Données RPLS 2022 (nombre de logements sociaux, `nbLsPls`), comparées sur notre échantillon apparié exact (1246 QPV, 2818 IRIS de contrôle) :
- Moyenne : 1166 logements sociaux (QPV) vs 445 (contrôle) — ratio ×2,6
- Médiane : 734 vs 397 — ratio ×1,85
- 96,7% des QPV ont ≥100 logements sociaux, contre 85,4% des contrôles

**Confirme empiriquement, sur notre propre échantillon (pas une statistique nationale générique), l'hypothèse avancée pour expliquer une partie du résultat 2018** (réforme RLS touchant spécifiquement le logement social). Renforce la prudence nécessaire sur l'interprétation causale des coefficients significatifs.

Limite technique : RPLS donne un compte absolu de logements sociaux, pas une part rapportée au nombre total de logements du quartier (donnée non disponible dans ce fichier) — comparaison en niveau, pas en proportion, mais l'écart est large (×2 à ×2,6) donc conclusion peu sensible à ce détail.

Décision : ajouter le nombre de logements sociaux (RPLS 2022) comme variable de contrôle dans la régression, en plus de documenter l'écart dans les limites.

## 25. Régression avec contrôle logement social × année : résultat nuancé

Ajout d'interactions logement_social(standardisé)×année en plus de traité×année. Effet : tous les coefficients traité×année rétrécissent (17% à 46% selon année/variable), confirmant que le logement social explique une partie du signal. Mais le taux de pauvreté reste significatif sur 2016/2018/2021 même après contrôle (0,32/0,60/0,73 points, tous p<0.01). Le revenu devient non significatif ou marginal partout après contrôle.

**Interprétation à retenir pour le mémoire** : résultat nuancé, pas un "tout s'explique" ni un "rien ne change". Le logement social explique une partie de la divergence observée (surtout côté revenu), mais un écart résiduel robuste subsiste sur le taux de pauvreté, dont l'origine (vrai effet ? autre facteur non contrôlé ?) reste ouverte. À présenter comme tel, avec honnêteté, plutôt que de trancher artificiellement.

Prochaines pistes possibles, non tranchées : chercher d'autres variables de composition (catégorie socio-professionnelle, pour tester la piste PEPA/heures sup 2019-2021) ; ou accepter ce résultat nuancé comme conclusion du mémoire avec limites bien posées.

## 26. Tests de robustesse effectués : 2016 émerge comme le résultat le plus solide

**Test 1 — sous-échantillon à appariement serré** (528/1246 QPV, distance pré-traitement ≤10 points) : résultat pauvreté globalement similaire (2016, 2018 significatifs, magnitude proche), MAIS le coefficient 2012 (pré-traitement) devient limite significatif (0,29, p=0,053) — affaiblit la confiance dans la tendance parallèle pour CE sous-échantillon spécifiquement. Revenu : pattern plus cohérent (tous négatifs) mais aucun significatif à 5%.

**Test 2 — exclusion de 2018 et 2021** (ruptures documentées) : 2016 reste quasi inchangé et significatif (pauvreté 0,438 p<0,001 ; revenu -0,0028 p=0,004) sur les deux variables. Confirme que 2016 n'est PAS un artefact de la présence de 2018/2021 dans la spécification.

**Synthèse à ce stade** : 2016 est le résultat le plus robuste de toute la série de tests (résiste à l'appariement serré, à l'exclusion des années suspectes, et partiellement au contrôle logement social — seule année où le signal ne s'effondre jamais). C'est aussi la seule année sans explication méthodologique documentée trouvée à ce jour. **Priorité identifiée : comprendre 2016 spécifiquement**, plutôt que de continuer à consolider 2018/2021 (déjà bien expliqués) ou 2019 (jamais significatif).

Prochaine étape à décider avec Alexandre : chercher activement une explication (documentation INSEE plus fine sur 2016, ou caractéristique spécifique des QPV/communes concernées cette année-là), ou accepter 2016 comme un résultat robuste mais dont la cause reste ouverte, à documenter comme telle dans le mémoire.

## 27. Limite non traitée jusqu'ici, identifiée via une consultation externe (Gemini) : renouvellement de population

Point valide non anticipé : nos données (Filosofi, niveau quartier) mesurent le lieu, pas les personnes. Si le classement QPV fonctionne et qu'un ménage s'enrichit, il peut déménager hors du quartier (mobilité résidentielle ascendante), remplacé par un ménage plus pauvre. Le quartier peut alors ne montrer "aucun effet" agrégé alors que des trajectoires individuelles se seraient améliorées. Limite réelle de toute analyse à l'échelle géographique (pas individuelle) avec ce type de source — à mentionner explicitement dans les limites du mémoire. Rappel connexe : l'étude ONPV trouvée en tout début de conversation notait déjà que "ceux qui s'installent [en QPV] sont plus pauvres que ceux qui partent" — cohérent avec ce mécanisme.

Idée à garder pour le volet ML/hétérogénéité (non retenue pour l'instant, piste future) : croiser avec l'intensité des financements ANRU (rénovation urbaine) par QPV, pour tester si l'hétérogénéité de l'effet est liée à l'ampleur des investissements plutôt qu'au seul classement.

Point d'attention méthodologique confirmé (déjà connu, re-signalé en creusant une source externe) : le classement QPV a fait l'objet d'ajustements politiques locaux après l'identification statistique — ce qui rend une RDD (Régression sur Discontinuité) fragile pour ce sujet, en plus d'être hors du cadre des cours suivis. Décision : ne pas mobiliser la RDD.

## 28. CORRECTION IMPORTANTE : une rupture documentée existe bien pour 2016

Contrairement à ce qui était noté en section 23 ("pas de rupture méthodologique spécifique documentée pour 2016"), une recherche plus poussée révèle que le millésime 2016 correspond à une **réorganisation majeure du système de production des indicateurs QPV** :
- Le taux de pauvreté est déplacé vers la table "revenu disponible" (déjà connu)
- **3 indicateurs socio-démographiques retirés de Filosofi**, remplacés par une nouvelle source (Recensement/Estimations démographiques) — exactement la bascule qu'Alexandre avait pressentie plus tôt dans la conversation
- 1 indicateur (part ménages dépendant des indemnités chômage) **supprimé purement et simplement**, secret statistique masquant >50% des QPV

**Ça change la lecture de la section 23 et 26** : 2016 n'est PAS sans explication documentée — c'est au contraire l'année de la plus grosse réorganisation méthodologique de toute la série 2012-2021. Le résultat robuste qu'on observe cette année-là pourrait donc, comme 2018/2021, être en bonne partie lié à cette rupture de production des données plutôt qu'à un vrai effet causal. À vérifier plus avant, mais la piste "artefact de mesure" reprend de la force sur 2016 aussi.

## 29. Décision : ajouter 2015 et 2020 pour compléter le graphique event-study sans aucun trou

Liens confirmés :
- QPV 2015 : `insee.fr/fr/statistiques/4200153?sommaire=2500477`
- IRIS 2015 : `insee.fr/fr/statistiques/4217503`
- QPV 2020 : `insee.fr/fr/statistiques/7231733?sommaire=2500477`
- IRIS 2020 : `insee.fr/fr/statistiques/7233950`

Objectif : obtenir la version complète (2012-2021, dix années sans trou) du graphique event-study, qui reste le livrable central de cette partie du mémoire.

## 30. Régression complète à 10 ans (2012-2021, sans trou) : deux découvertes majeures

**2015 est significatif**, dans le même sens et proche en magnitude que 2016 (pauvreté +0,41 vs +0,44 ; revenu -0,0048 vs -0,0028). Piste à retenir : la doc INSEE précise que "les données 2015 sont proposées dans la géographie en vigueur au 1er janvier 2016" — indice possible d'un chevauchement méthodologique entre les deux millésimes, cohérent avec la découverte de la section 28 (réorganisation Filosofi/Recensement autour de 2016).

**2020 et 2021 ont des signes OPPOSÉS, tous deux significatifs** (pauvreté : -0,45 en 2020 contre +0,92 en 2021 ; revenu : +0,0075 en 2020 contre -0,0052 en 2021). Aucun mécanisme de politique publique plausible n'inverserait un effet en une seule année. C'est la preuve la plus concrète que 2020-2021 sont dominés par du bruit de mesure (Covid), confirmant empiriquement ce qu'on supposait depuis le début à partir de la documentation seule.

**Lecture d'ensemble à ce stade** : le signal le plus digne d'intérêt est la paire 2015-2016 (concordante, au moment précis du classement) ; 2018 reste isolé et déjà expliqué (RLS/logement social) ; 2020-2021 s'invalident mutuellement par leur incohérence de signe.

Fichiers : `panel_qpv_complet_v2.csv`, `panel_iris_complet_v2.csv`, `panel_regression_complet.csv` (10 années, aucun trou).

## 31. Panel équilibré (constant sur 10 ans) : confirme l'hypothèse d'Alexandre sur la composition changeante

Vérification demandée par Alexandre : le panel n'était PAS équilibré (972/1246 QPV seulement présents les 10 années ; 2021 particulièrement touché par le masquage, 980 valides contre ~1240 les autres années). Régression relancée sur le sous-ensemble strictement équilibré (3218 unités, 10 années complètes chacune).

**Résultat pauvreté, nettement plus cohérent** : progression quasi continue 2015→2018 (0,44 / 0,54 / 0,22* / 0,80, tous significatifs ou proches), 2019 plus faible (0,24, p=0,08). L'alternance signif/non-signif qui semblait suspecte (section 26/30) s'explique donc en bonne partie par la composition changeante de l'échantillon non équilibré — confirmé empiriquement, pas juste supposé.

**Mais nouveau problème détecté côté revenu** : sur ce panel équilibré, 2012 ET 2013 (pré-traitement) deviennent significatifs (p=0,025 chacun) — la tendance parallèle sur le revenu ne tient plus pour ce sous-ensemble précis. À documenter comme limite : le choix balanced vs unbalanced panel change la validité du design selon la variable regardée.

**2020 reste incohérent avec 2021** (signe opposé) même sur ce panel équilibré — confirme que ces deux années restent à exclure de toute conclusion causale.

Fichier : `panel_regression_equilibre.csv`.

## 32. Référence groupée (2012-2014) et test de Wald conjoint sur la tendance parallèle

**Changement de référence** : passage d'une référence unique (2014) à une référence groupée (moyenne implicite 2012-2013-2014, obtenue en omettant leurs interactions individuelles). Résultat pauvreté nettement plus lisible : progression quasi continue et significative 2015→2021 (hors 2020), magnitudes légèrement plus fortes (0,48 à 0,95).

**Test de Wald conjoint** (H0 : coef(2012)=coef(2013)=0, sur la spécification à référence 2014 seule, panel équilibré) :
- Pauvreté : statistique 3,34, p=0,188 → **H0 non rejetée**, cohérent avec tendance parallèle
- Revenu : statistique 6,25, p=0,044 → **H0 rejetée**, tendance parallèle mise en doute formellement

**Implication** : validation méthodologique asymétrique selon la variable — le résultat sur la pauvreté repose sur un design validé statistiquement (test formel, pas juste visuel), celui sur le revenu repose sur un design dont l'hypothèse de base est statistiquement rejetée. À utiliser pour hiérarchiser la confiance entre les deux résultats dans la rédaction : pauvreté > revenu en termes de crédibilité du design.

Décision : ne pas mobiliser de test placebo (hors du cadre jugé confortable par Alexandre), le test de Wald conjoint (dans les cours) suffit comme validation formelle de la tendance parallèle.

## 33. RESULTAT FINAL DE REFERENCE (toutes corrections combinées)

Spécification définitive : panel strictement équilibré (3218 unités, 10 ans) + référence groupée 2012-2014 + contrôle logement social × année.

| Année | Pauvreté (points) | Revenu (log) |
|---|---|---|
| 2015 | +0,33*** | -0,0047*** |
| 2016 | +0,41*** | -0,0031* |
| 2017 | +0,17 n.s. | +0,0004 n.s. |
| 2018 | +0,67*** | -0,0025 n.s. |
| 2019 | +0,15 n.s. | +0,0011 n.s. |
| 2020 | -0,41* | +0,0061*** |
| 2021 | +0,72*** | -0,0043* |

Validation du design : Wald conjoint pré-traitement non rejeté pour pauvreté (p=0,19), rejeté pour revenu (p=0,04).

**C'est la table à utiliser dans le mémoire pour la section résultats.** Conclusion à retenir : évidence robuste d'une divergence de pauvreté à partir de 2015, partiellement expliquée par des facteurs de mesure (logement social, ruptures Filosofi), non attribuable avec certitude à un effet causal pur. Résultat sur le revenu à traiter comme secondaire (tendance parallèle rejetée).

## 34. Source précieuse trouvée par Alexandre : Institut Paris Region (avril 2025)

Référence : Beaufils S., Joinet H., "Les quartiers en politique de la ville, reflet des évolutions de la géographie sociale francilienne", Note rapide Habitat-Société n°1034, L'Institut Paris Region, 10 avril 2025.

**Apports pour le mémoire :**
1. **Méthode de classement précisée et chiffrée** : seuil de 60% du revenu fiscal médian national pondéré par le revenu médian de l'unité urbaine, carroyage 200m, minimum 1000-1500 habitants. Confirme et complète la doc INSEE déjà citée.
2. **Confirmation indépendante de l'ajustement politique du zonage** ("travail itératif entre élus locaux et services de l'État") — deuxième source sur ce point, renforce la décision d'écarter la RDD.
3. **Source sérieuse et chiffrée pour la limite du renouvellement de population** (section 27, initialement soulevée via Gemini) : "l'installation de ménages aux revenus plus élevés et la baisse de la population constituent les deux principaux facteurs de sortie de la politique de la ville." Exemple chiffré : quartier Pleyel (Saint-Denis), -520 habitants et +22% de niveau de vie en 5 ans, sorti du classement en 2024. **Cette source remplace/renforce solidement la mention Gemini, à citer en priorité dans le mémoire.**
4. **Précédent méthodologique pour le volet ML** : typologie à 4 classes de QPV construite par l'IPR à partir de 15 indicateurs socio-démographiques (limitée à l'Île-de-France, non réutilisable telle quelle mais bon précédent à citer).
5. Confirme le rôle des dispositifs bundlés (PNRU rénovation urbaine) dans les trajectoires observées — renforce la prudence déjà actée sur l'attribution causale au seul "label" QPV.

Source à intégrer dans la revue de littérature (sujet traité), qualité élevée (institut public régional reconnu, données Insee/Filosofi, publication récente).

## 35. CLOTURE de la partie régression/DiD

Décision prise avec Alexandre : clôturer la partie causale. Le revenu médian n'est pas supprimé mais rétrogradé en résultat secondaire (le test de Wald rejette la tendance parallèle pour cette variable, donc pas de base pour une interprétation causale) — décision méthodologique assumée et documentée, pas un simple retrait silencieux.

Document de synthèse rédigé, prêt pour intégration au mémoire : `redaction/partie_regression_finale.md`. Contient : rappel du design, échantillon final, validation (tests de Wald), résultats pauvreté (principal), résultats revenu (secondaire caveaté), facteurs explicatifs quantifiés, limite transmise au ML (mobilité résidentielle), conclusion rédigée.

**Statut : partie régression/DiD CLOTUREE.** Prochaine étape : volet ML.

## 36. Test de l'hypothèse "mobilité résidentielle/fuite des enrichis" : REJETÉE, résultat inverse trouvé

Données population QPV (2013, 2018) et IRIS de contrôle (recensement, mêmes années) récupérées et traitées. Évolution moyenne : QPV -0,49% (médiane -1,42%), IRIS de contrôle +1,17% — confirme la baisse de population des QPV en moyenne, cohérent avec la littérature (Institut Paris Region).

**Test direct** : échantillon scindé en deux (médiane de l'évolution de population QPV), régression event-study réestimée séparément dans chaque sous-groupe.

Résultat : **l'écart de pauvreté est plus FAIBLE et moins systématique dans les QPV à forte baisse de population** (2019 non significatif, 2020 fortement négatif), et **plus FORT et plus systématique dans les QPV à population stable/en hausse** (2017 et 2019 deviennent significatifs, 2021 presque doublé : 1,29 contre 0,60).

**C'est l'inverse de l'hypothèse testée.** Si la fuite des ménages enrichis expliquait le résultat, l'écart aurait dû être plus fort là où la population baisse. Hypothèse non confirmée par les données, à documenter comme telle (rejet honnête, pas contournement).

**Piste alternative non vérifiée** : les QPV à forte baisse de population pourraient être ceux ayant bénéficié de programmes de rénovation urbaine (PNRU, démolitions + diversification du parc), ce qui améliorerait leur trajectoire plutôt que de la dégrader — cohérent avec l'exemple de Pleyel (Institut Paris Region). Nécessiterait une donnée sur les programmes ANRU/PNRU par QPV pour être testée, non mobilisée dans ce mémoire faute de temps/données.

Fichiers : `qpv_evolution_population.csv`, `iris_evolution_population.csv`.
