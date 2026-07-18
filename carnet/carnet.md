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

## 37. Reconstruction du script d'appariement manquant (03_controle_iris_miroirs.py complété)

Ménage du dépôt : plusieurs fichiers `data/processed/` étaient des sorties orphelines d'un pipeline antérieur (scripts 06/07 disparus, versions `v1` remplacées par leurs `v2`) — supprimés. Mais quatre fichiers (`iris_controle_candidats.csv`, `qpv_pauvrete_pretraitement.csv`, `iris_pauvrete_pretraitement.csv`, `commune_vers_unite_urbaine.csv`) n'étaient reproduits par AUCUN script présent dans le dépôt : `03_controle_iris_miroirs.py` ne contenait que des définitions de fonctions, jamais exécutées de bout en bout.

**Reconstruction et vérification** (script complété, voir `scripts/03_controle_iris_miroirs.py`) :
- Découverte en reconstruisant l'exclusion des IRIS "miroirs" : la comparaison de nom doit se faire sur le nom **propre de l'IRIS**, pas sur le nom de sa commune (`libcom` dans `panel_iris_complet_v2.csv`, identique pour tous les IRIS d'une même commune — inutilisable). Le vrai nom de chaque IRIS (`LibGeo`) se trouve dans `rpls_iris.csv`. Une fois ce champ utilisé, reproduction exacte de `iris_controle_candidats.csv` (8380/8380), avec la règle qu'un IRIS sans entrée RPLS (15 cas) est exclu par prudence.
- `qpv_pauvrete_pretraitement.csv` et `iris_pauvrete_pretraitement.csv` : reproduits à l'identique (précision flottante), y compris le motif exact des valeurs manquantes (secret statistique, 985/7328 IRIS).
- `appariement_qpv_iris_v2.csv` : reproduit à l'identique une fois compris que l'algorithme K plus proches voisins ne doit PAS écarter au préalable les IRIS à pauvreté masquée — ils restent inclus (avec distance vide) quand une commune/UU a moins de 5 candidats à distance connue, exactement comme dans le fichier existant (184 lignes de ce type).
- `commune_vers_unite_urbaine.csv` : ce n'est pas une sortie du pipeline mais une table de référence externe (nomenclature INSEE, section 17) — conservée telle quelle, non régénérée.

**Fausse alerte en cours de route** : une première vérification (bug de comparaison de ma part - un test tautologique masquait le motif réel de valeurs manquantes) avait fait croire à un vrai trou de données sur 985 IRIS. Revérification directe sur le fichier committé : confirmé qu'il s'agissait bien de valeurs manquantes des deux côtés (secret statistique), pas d'un écart. Leçon retenue : toujours comparer les valeurs elles-mêmes, pas seulement la présence de la clé.

**Suite au ménage** : `iris_controle_candidats.csv`, `qpv_pauvrete_pretraitement.csv`, `iris_pauvrete_pretraitement.csv` supprimés (regénérables par `03_controle_iris_miroirs.py`). `commune_vers_unite_urbaine.csv` et `appariement_qpv_iris_v2.csv` conservés committés (le premier comme donnée de référence externe, le second comme entrée directe déjà lue par `04_regression_event_study.py`/`05_tests_robustesse.py`).

## 38. Inventaire consolidé de toutes les limites de la partie régression

Suite à une discussion approfondie sur ce que le DiD peut/ne peut pas garantir, un inventaire complet de toutes les limites, compromis et problèmes a été dressé et rédigé dans `redaction/limites_consolidees.md`. Six catégories : contraintes de données non choisies, compromis d'appariement, limite structurelle du DiD (tendance parallèle protège seulement contre une divergence pré-existante, pas contre un choc post-traitement qui active une différence de composition anodine), ruptures de mesure identifiées, résultats de validation et leurs failles (Wald, panel équilibré), non résolu assumé comme tel.

Discussion clé ayant mené à cet inventaire : le DiD ne "retire" pas automatiquement tout ce qui touche les deux groupes différemment — seulement ce qui les touche également. Un facteur de confusion qui interagit avec un choc précis (logement social × RLS 2018) doit être activement cherché et corrigé, pas supposé absent.

**Suite décidée avec Alexandre** : 5 chantiers d'approfondissement de la partie régression, du plus simple (aucune nouvelle donnée) au plus lourd (nouvelle donnée à intégrer). Fonctions ajoutées dans `scripts/05_tests_robustesse.py` : `reestimer_excluant_annee`, `reestimer_appariement_communal_strict`.

## 39. Chantier 1 — Réestimation en excluant 2020 : coefficients quasi identiques, confirmé

**Objectif** : vérifier que l'exclusion de 2020 du panel (déjà justifiée par l'inversion de signe 2020/2021, section 30) ne fait que recalculer les effets fixes année, sans changer la lecture des autres années.

**Méthode** : `reg_data` filtré pour exclure `annee == 2020` avant de réappliquer `restreindre_panel_equilibre` (donc la complétude du panel équilibré est redéfinie sur les 9 années restantes plutôt que sur 10) — même spécification que la référence (§33) : référence poolée 2012-2014, panel équilibré, sans contrôle logement social.

**Effet de bord attendu et vérifié** : le panel équilibré passe de 3218 à 3238 unités (+20, les unités masquées uniquement en 2020 redeviennent "complètes" sur les 9 années restantes). C'est le seul changement de composition, cohérent avec ce qui était anticipé.

| Année | Pauvreté (avec 2020) | Pauvreté (sans 2020) | Revenu log (avec 2020) | Revenu log (sans 2020) |
|---|---|---|---|---|
| 2015 | 0,483*** | 0,486*** | -0,0066*** | -0,0065*** |
| 2016 | 0,590*** | 0,582*** | -0,0051*** | -0,0050*** |
| 2017 | 0,270* | 0,265* | -0,0007 n.s. | -0,0007 n.s. |
| 2018 | 0,843*** | 0,850*** | -0,0044** | -0,0044** |
| 2019 | 0,284 (p=0,054) | 0,294* (p=0,049) | -0,0003 n.s. | -0,0003 n.s. |
| 2021 | 0,953*** | 0,963*** | -0,0065** | -0,0065** |

**Conclusion** : confirmé, coefficients quasi identiques (écarts de l'ordre du millième pour le revenu, de quelques centièmes pour la pauvreté). Seule 2019 change de statut, et de façon marginale : passe de non significatif à 5% (p=0,0537) à tout juste significatif (p=0,0492) — un artefact de seuil, pas un changement substantiel (2019 restait de toute façon la moins convaincante des années significatives). L'exclusion de 2020 est donc bien neutre pour la lecture des autres années, comme attendu.

## 40. Chantier 2 — Appariement communal strict (sans repli unité urbaine) : résultat rassurant, signal légèrement plus fort

**Objectif** : vérifier si le repli sur l'unité urbaine (quand aucun IRIS n'existe dans la commune du QPV) dilue, neutralise ou renforce le signal, en comparant au sous-ensemble apparié uniquement en commune stricte.

**Méthode** : filtre `niveau == 'commune'` sur `appariement_qpv_iris_v2.csv`, panel reconstruit sur ce sous-ensemble uniquement, même spécification (référence poolée 2012-2014, panel équilibré).

**Échantillon résultant** : 1066 QPV appariés en communal strict (contre 1246 avec repli, soit 96% de couverture totale — voir section 18), 3059 unités dans le panel équilibré (contre 3218). **Note** : le chiffre de 888 QPV cité dans le brief initial pour "communal strict" correspondait à une version antérieure du pipeline (section 17, avant l'amélioration de la couverture géographique via TAG_QPV_2015 en section 18) — le chiffre à jour est 1066/1296 QPV éligibles (deux QPV en moins que le nombre total avec pauvreté pré-traitement connue, cohérent).

| Année | Pauvreté (complet, avec repli) | Pauvreté (communal strict) | Revenu log (complet) | Revenu log (communal strict) |
|---|---|---|---|---|
| 2015 | 0,483*** | 0,592*** | -0,0066*** | -0,0075*** |
| 2016 | 0,590*** | 0,701*** | -0,0051*** | -0,0062*** |
| 2017 | 0,270* | 0,402*** | -0,0007 n.s. | -0,0019 n.s. |
| 2018 | 0,843*** | 0,988*** | -0,0044** | -0,0055*** |
| 2019 | 0,284 n.s. | 0,481*** | -0,0003 n.s. | -0,0023 n.s. |
| 2020 | -0,338* | -0,138 n.s. | 0,0056*** | 0,0039* |
| 2021 | 0,953*** | 1,218*** | -0,0065** | -0,0090*** |

**Conclusion** : le repli sur l'unité urbaine n'est pas source de dilution du signal — c'est même l'inverse. Sur le sous-échantillon communal strict, tous les coefficients de pauvreté sont plus élevés en magnitude et gagnent en significativité (2017 et 2019 passent de marginal/non significatif à significatif à 1%), et 2020 (déjà hors analyse principale) perd sa significativité. Interprétation prudente : soit les appariements de repli (unité urbaine) sont légèrement plus bruités qu'annoncé en section 17 (où leur distance moyenne était pourtant meilleure : 5,6 vs 14,2 points), soit le sous-échantillon communal strict correspond à des QPV en zones plus denses/plus grandes villes où l'effet réel est plus marqué — cette deuxième explication n'est pas testée ici, à garder comme piste pour le volet ML (typologie urbaine). Dans tous les cas, la règle d'appariement à deux niveaux (section 17-18) n'affaiblit pas le résultat principal — au contraire, elle permet de couvrir 180 QPV supplémentaires (1246 vs 1066) sans dégrader le signal, ce qui la conforte comme choix méthodologique pour l'échantillon final.

## 41. Chantier 5 — Balayage systématique des variables démographiques 2010 : exploratoire, à ne pas sur-interpréter

**Donnée utilisée** : `data/processed/demographie_2010_qpv.xls` (feuille "Quartiers", 1292 QPV, 60 variables numériques hors identifiants). Fichier ignoré par git (`*.xls` dans `.gitignore`) — **point de reproductibilité à garder en tête** : si ce fichier n'est pas retéléchargé/reconstruit ailleurs, ce chantier n'est pas rejouable tel quel à partir du seul dépôt Git. À signaler dans le mémoire si cette donnée sert à un résultat cité.

**Déduplication sexe/nationalité** (demandée par le brief) : d'après la feuille "Documentation" du fichier source, les variables suivent une convention `tx_[PREFIXE]_[SUFFIXE]` où PREFIXE ∈ {tot, f, et} (parfois h/fr pour l'indice de jeunesse). Les variables de "premier rang" (calculées sur la population totale du quartier) sont gardées ; celles de "second rang" (calculées sur une sous-population — femmes, étrangers — donc mesurant le même phénomène restreint à un sous-groupe) sont exclues comme redondantes. Résultat : **24 variables non redondantes retenues sur 60** (au lieu des "62" du brief, qui comptaient probablement les colonnes d'identification ou une version légèrement différente du fichier). Exception documentée : `tx_f` (part de femmes dans la population) est gardée malgré son préfixe, car ce n'est pas la déclinaison d'un total déjà présent mais une variable de composition à part entière.

**Méthode** : chaque variable, standardisée (z-score) et interagie avec l'année, est ajoutée à la régression de référence qui contient déjà `traite×année` et `logement_social×année` (celle du résultat final, section 33, mais panel restreint à 9 ans sans 2020 — cf. Chantier 1). Chaque IRIS de contrôle hérite de la valeur de SON QPV apparié (même logique que le test de population, section 36) — ce n'est donc pas une vraie caractéristique de l'IRIS, seulement un indicateur du type de QPV auquel il est rattaché. Référence (baseline, avant ajout d'une variable démographique) :

| Année | Coef. pauvreté (traite×année + logement social×année) | p-value |
|---|---|---|
| 2015 | 0,324 | 0,0003 |
| 2016 | 0,393 | 0,0008 |
| 2017 | 0,152 | 0,24 n.s. |
| 2018 | 0,665 | 0,0001 |
| 2019 | 0,142 | 0,40 n.s. |
| 2021 | 0,706 | 0,0005 |

(Cohérent avec la liste du brief — années significatives : 2015, 2016, 2018, 2021.)

**Tableau des variables les plus "explicatives"** (réduction moyenne en % du coefficient traite×année sur les 4 années significatives, script `scripts/06_balayage_demographie.py`, sortie complète dans `data/processed/balayage_demographie_2010.csv`) :

| Rang | Variable | Réduction moyenne | Interactions var×année significatives (/6) | % QPV manquants |
|---|---|---|---|---|
| 1 | `tx_tot_men1` (part de ménages d'une personne) | 5,7% | 5/6 | 0,7% |
| 2 | `tx_f` (part de femmes) | 4,6% | 6/6 | 0,02% |
| 3 | `l_nbpers` (nb moyen de personnes par logement) | 4,3% | 5/6 | 0,3% |
| 4 | `tx_tot_men6` (part de ménages nombreux) | 3,4% | 2/6 | 49,1% (!) |
| 5 | `tx_tot_et` (part d'étrangers) | 3,0% | 1/6 | 8,5% |
| 6 | `tx_tot_diplbac2` (part diplômés Bac+2 ou +) | 2,4% | 1/6 | 8,9% |
| ... | (18 autres variables, réduction 0,1% à 2,3%) | | | |
| dernier | `tx_tot_fam_mono` (part familles monoparentales) | **-3,6%** | 5/6 | 4,7% |
| avant-dernier | `tx_l_vacant` (part logements vacants) | **-2,6%** | 2/6 | 48,2% |

**Lecture, avec prudence** :
- `tx_tot_men1` et `l_nbpers` (taille des ménages/logements) et `tx_f` (part de femmes) sont les variables qui absorbent le plus de signal — cohérent avec une lecture "composition démographique du ménage" déjà entrevue via le test de mobilité résidentielle (section 36). `tx_f` a la significativité la plus nette (6/6 années) et quasiment aucune valeur manquante — c'est la variable la plus fiable de tout le balayage, à privilégier si une seule doit être retenue pour un futur contrôle.
- **Deux variables (`tx_tot_fam_mono`, `tx_l_vacant`) vont dans le sens INVERSE** : les ajouter fait grossir le coefficient traite×année plutôt que le réduire. Résultat contre-intuitif à ne pas sur-interpréter sans creuser davantage — pourrait signaler une confusion plus complexe (ex. composition changeante dans le temps) plutôt qu'un simple effet additif.
- **`tx_tot_men6` et `tx_l_vacant` ont un taux de valeurs manquantes proche de 50%** (secret statistique) — leur classement est fragile, à ne pas citer comme un résultat solide sans vérifier la sensibilité au traitement des manquants (ici, remplacées par 0 après standardisation, càd traitées comme "dans la moyenne" — choix conservateur mais qui mérite d'être signalé si ces variables sont citées).

**Avertissement à conserver dans le mémoire (déjà anticipé par le brief)** : 24 variables testées une par une sur la même régression, sans correction pour tests multiples (type Bonferroni). Le classement ci-dessus est **exploratoire, pas confirmatoire** — sert à orienter une hypothèse à tester plus rigoureusement (ex. dans le volet ML, ou en resserrant une hypothèse spécifique comme cela a été fait pour le logement social et la population), pas à affirmer que `tx_tot_men1` "explique" causalement une partie de l'effet QPV.

## 42. Chantier 3 — Logement social en proportion : résultat non concluant, révèle un problème de fond plutôt qu'une réponse propre

**Recherche de données préalable** : vérifié en direct sur `insee.fr/fr/statistiques/8647012` — aucune version QPV/quartiers du produit IRIS "Logement" n'existe (page confirmée : IRIS uniquement). Recherche d'une population QPV plus récente que 2018 (pour servir de dénominateur de repli cohérent avec le RPLS/logement 2022) également négative : le fichier "Estimations démographiques 2022 QPV2015" (`sig.ville.gouv.fr`, insee.fr/fr/statistiques/8742564) ne contient que des **parts en pourcentage**, aucune population en valeur absolue (vérifié en ouvrant le fichier, pas déduit du descriptif de la page — la synthèse automatique de la page avait annoncé à tort qu'il contenait la population totale). Et la page dédiée à la population confirme que la géographie QPV2015 s'arrête à 2018 ; au-delà, l'INSEE ne propose que la géographie QPV2024 (zonage différent, incompatible avec le design du mémoire). **Décision prise avec Alexandre** : utiliser la population QPV 2018 comme dénominateur de repli, en l'assumant comme approximation documentée plutôt que de partir sur une reconstruction lourde (table de passage QPV2024→QPV2015, écartée).

**Construction** : `logement_social_proportion` = nbLsPls (RPLS 2022) / total logements 2022 (`P22_LOG`, source `IRIS - Logement - 2022`, vérifié : nom de variable exactement conforme à ce qu'anticipait le brief) côté IRIS ; nbLsPls / population QPV 2018 côté QPV. Script : `scripts/07_logement_social_proportion.py`.

**Incident technique noté** : le module Python `zipfile` lève une erreur CRC-32 sur l'archive `IRIS - Logement - 2022.zip` alors que `unzip` en ligne de commande la lit sans aucune erreur (`unzip -t` confirme "No errors detected"). Contournement : extraction via `subprocess` + `unzip` plutôt que `zipfile`. Cause non investiguée plus avant (pas bloquant une fois le contournement identifié), mais à garder en tête si d'autres archives INSEE posent le même problème.

**Résultat (taux de pauvreté, panel équilibré, référence poolée 2012-2014)** :

| Année | Sans contrôle | Contrôle absolu (nbLsPls, réf. section 33) | Contrôle proportion "mixte" (logements IRIS / pop. QPV) | Contrôle proportion "homogène" (pop. des deux côtés, diagnostic) |
|---|---|---|---|---|
| 2015 | 0,483*** | 0,320*** | 0,572*** | -0,084 n.s. |
| 2016 | 0,590*** | 0,403*** | 0,698*** | -0,150 n.s. |
| 2017 | 0,270* | 0,159 n.s. | 0,356** | -0,424** |
| 2018 | 0,843*** | 0,659*** | 0,996*** | -0,363* |
| 2019 | 0,284 n.s. | 0,132 n.s. | 0,404** | -0,721*** |
| 2020 | -0,338* | -0,412* | -0,264 n.s. | -1,105*** |
| 2021 | 0,953*** | 0,697*** | 1,170*** | -0,756*** |

**Ce que ça révèle, avec le recul nécessaire** : la version "proportion mixte" (celle demandée dans le brief) n'absorbe PAS plus de signal que le contrôle absolu — elle en absorbe MOINS, et fait même remonter les coefficients au-dessus du niveau sans aucun contrôle. En creusant pourquoi (moyennes par groupe : `prop_mixte_z` = 0,118 en QPV contre 0,199 en IRIS de contrôle), on découvre que le contrôle "mixte" fait apparaître les QPV comme ayant proportionnellement MOINS de logement social que leurs contrôles — l'inverse de ce qu'on sait être vrai (section 24). Un contrôle de cohérence (même dénominateur — population 2018 — des deux côtés) confirme le diagnostic : avec un dénominateur homogène, les QPV ressortent bien nettement au-dessus (moyenne 0,717 contre -0,332), dans le sens attendu, et ce contrôle absorbe cette fois énormément de signal (les coefficients traité×année deviennent négatifs).

**Conclusion à retenir pour le mémoire** : ce chantier ne débouche pas sur un contrôle en proportion utilisable. Le problème n'est pas la proportion en tant que telle, mais le fait que le numérateur (logements sociaux) est rapporté à deux concepts différents selon le groupe — logements côté IRIS, population côté QPV — ce qui rend les deux proportions non comparables et inverse artificiellement le classement QPV/contrôle. Ce n'est pas un problème qu'on peut corriger avec les données actuellement disponibles (aucune population QPV récente, aucun total-logements QPV n'existe). **Le contrôle en nombre absolu (section 25/33) reste donc la version à conserver comme référence du mémoire** — ce chantier confirme, a contrario, que la donnée manquante (total logements ou population comparable côté QPV) est une vraie limite de données à documenter explicitement, pas un simple raffinement optionnel resté de côté. Le résultat "homogène" (diagnostic) n'est lui-même pas utilisable tel quel comme contrôle final : l'écart de moyenne entre groupes est si large (près d'un écart-type) qu'ajouter cette interaction revient probablement à sur-contrôler (la population du quartier est elle-même liée au mécanisme de sélection QPV, cf. limite de mobilité résidentielle section 27/36) plutôt qu'à isoler un facteur de confusion propre.

## 43. Point de reproductibilité réglé (chantiers 4 et 5) et Chantier 4 — Score de propension multivarié

**Reproductibilité (signalée en section 41)** : `data/processed/demographie_2010_qpv.xls` était exclu par le `.gitignore` (règle générale `*.xls`), ce qui rendait le Chantier 5 non rejouable depuis le seul dépôt Git. Réglé par une exception ciblée dans `.gitignore` (`!data/processed/demographie_2010_qpv.xls`) : le fichier est léger (788 Ko, simple copie de `data/raw/`, jamais retravaillé), committé tel quel.

**Décision (a) confirmée pour le Chantier 4** : Alexandre avait déjà récupéré les 5 fichiers Insee "Base infra-communale (IRIS)" du recensement 2010 nécessaires à l'option (a) du brief (équivalent IRIS des variables démographiques QPV) : Population, Activité des résidents, Diplômes/Formations, Couples/Familles/Ménages, Logement. Ces fichiers sont volumineux (~200 Mo au total, `data/raw/`, non versionné par choix de projet) — bien trop lourds pour être committés bruts. Traités comme les autres sources Insee du projet : un script d'extraction (`scripts/08_demographie_iris_2010.py`) construit un extrait réduit aux colonnes utiles et committable (`data/processed/demographie_2010_iris.csv`, 2,2 Mo, 8380 IRIS candidats × 13 variables), ce qui règle aussi la reproductibilité du Chantier 4 depuis le seul dépôt Git — les fichiers bruts eux-mêmes n'ont pas besoin d'être committés, seul leur extrait nettoyé l'est (même logique que rpls_iris.csv, panel_iris_complet_v2.csv, etc.).

**Construction de l'équivalent IRIS (13 variables sur 24 non redondantes, vérifié variable par variable — jamais déduit du seul nom de colonne)** : chaque formule a été confirmée en croisant la feuille "Documentation" du fichier QPV avec les feuilles "Liste des variables" des 5 fichiers Insee.
- Reconstructibles à l'identique : `tx_f`, `tx_tot_et`, `ind_jeune` (fichier Population), `tx_tot_empl` (fichier Activité des résidents), `tx_tot_infbac`, `tx_tot_diplbac`, `tx_tot_diplbac2` (fichier Diplômes/Formations), `tx_tot_men1`, `tx_tot_fam_mono` (fichier Couples/Familles/Ménages), `tx_l_2piec`, `tx_l_5piec`, `tx_l_vacant`, `l_nbpers` (fichier Logement).
- **Non reconstruites, par prudence plutôt que par approximation risquée** : `tx_tot_0a14/15a24/25a59/60a74/75etplus` et leurs déclinaisons par tranche d'âge des ménages d'une personne (bornes d'âge différentes entre le fichier QPV et les fichiers Insee IRIS 2010 mobilisés — ex. 15-29/30-44/45-59 au lieu de 15-24/25-59 — impossible de recalculer les mêmes bornes sans le détail par âge simple) ; `tx_tot_eprec` (catégories de contrats précaires non exactement superposables, population de référence différente) ; `tx_tot_scol` (même problème de bornes d'âge) ; `tx_tot_men6` et `tx_nblog_20l` (aucune variable équivalente disponible dans ces 5 fichiers).

**Incident technique** : `unzip` échouait en ligne de commande sur les fichiers aux noms accentués fournis, alors que Python les listait correctement — cause identifiée : les noms de fichiers sur disque sont normalisés Unicode NFD (accents décomposés) alors qu'un littéral Python écrit dans l'éditeur est en NFC (accents composés), une comparaison stricte échoue silencieusement. Contourné par une recherche par préfixe (`os.listdir` + `startswith`) plutôt que par nom exact. Même contournement que la section 42 (CRC-32 de `zipfile`) réutilisé ici : extraction des zips via `unzip` en sous-processus plutôt que le module `zipfile`.

**Sélection finale des variables du score (9 sur les 13 reconstructibles, pas 13)** : en construisant la table de covariables, un taux de valeurs manquantes élevé côté QPV a été découvert sur 4 des 13 variables reconstructibles — `tx_l_vacant` (49,7%), `tx_l_5piec` (20,4%), `ind_jeune` (15,1%), `tx_l_2piec` (13,3%) — cohérent avec le constat déjà fait en section 41 sur `tx_l_vacant` et `tx_tot_men6` (secret statistique plus fréquent sur des quartiers plus petits que les IRIS). Cumulées par suppression listwise avec les 9 autres variables, ces 4 variables auraient fait perdre plus de 60% des QPV (488/1296 restants dans un premier essai). Retirées du score (gardées disponibles dans `demographie_2010_iris.csv` pour un usage futur éventuel) : la perte redescend à 16% (1089/1296 QPV avec covariables complètes), un compromis documenté plutôt qu'un choix arbitraire.

**Variables du score final** : pauvreté pré-traitement, log(revenu médian pré-traitement) — déjà utilisées dans l'appariement univarié — plus 9 variables démographiques 2010 : `tx_f`, `tx_tot_et`, `tx_tot_empl`, `tx_tot_infbac`, `tx_tot_diplbac`, `tx_tot_diplbac2`, `tx_tot_men1`, `tx_tot_fam_mono`, `l_nbpers`. Toutes standardisées (z-score) sur l'ensemble QPV + IRIS candidats combiné.

**Modèle et incident méthodologique révélateur** : régression logistique QPV=1/IRIS candidat=0 (choix discret, dans le cadre du cours). Un logit non pénalisé (`statsmodels`) ne converge pas — Hessienne singulière. Diagnostic : séparation quasi-parfaite, pas un bug numérique. C'est en réalité un résultat substantiel attendu : le zonage QPV est défini administrativement à partir de critères socio-économiques (la pauvreté en premier lieu), donc les variables pré-traitement suffisent presque à elles seules à distinguer un QPV d'un IRIS candidat. Résolu dans le cadre du cours par une régression logistique pénalisée (ridge/L2, ridge/lasso au programme), force de régularisation choisie par validation croisée (5 plis, `LogisticRegressionCV`, scikit-learn — **nouvelle dépendance installée**, absente jusqu'ici du projet) plutôt que fixée à la main. Coefficients standardisés (poids décroissant) : `tx_tot_infbac` (1,44), `tx_f` (1,33), `tx_tot_empl` (1,21), `tx_tot_men1` (1,13), `tx_tot_diplbac` (1,09), `tx_tot_fam_mono`, `tx_tot_diplbac2`, `tx_tot_et` (~0,76-0,77), `taux_pauvrete_pre` (0,41), `log_revenu_pre` (-0,33), `l_nbpers` (0,15).

**Limite de recouvrement (common support), à ne pas passer sous silence** : même après pénalisation, l'AUC in-sample reste à 1,000 et les scores prédits sont quasi tous saturés près de 1 aussi bien pour les QPV que pour les IRIS qui leur ressemblent le plus dans chaque commune. Conséquence directe : l'appariement par plus proche voisin sur le score (K=5, même règle de repli commune → unité urbaine que l'appariement univarié, `scripts/09_score_propension.py`) reproduit **76% des mêmes paires QPV-IRIS** que l'appariement univarié sur la seule pauvreté (3777/4952 paires identiques), et un équilibre des covariables (écart standardisé QPV − contrôle) quasiment identique entre les deux méthodes sur les 11 covariables comparées (ex. `tx_f` : 2,82 dans les deux cas ; `taux_pauvrete_pre` : 1,12 univarié contre 1,12 score). Le score multivarié ne « corrige » donc rien qui clochait dans l'appariement univarié — il aboutit à un résultat très proche, ce qui est en soi un résultat de robustesse plutôt qu'un raffinement qui change la donne.

**Comparaison de la régression event-study (panel équilibré, référence poolée 2012-2014, sans 2020 — même spécification que le Chantier 1)** :

| Année | Pauvreté (univarié) | Pauvreté (score propension) | Revenu log (univarié) | Revenu log (score propension) |
|---|---|---|---|---|
| 2015 | 0,486*** | 0,577*** | -0,0065*** | -0,0081*** |
| 2016 | 0,582*** | 0,608*** | -0,0050*** | -0,0058*** |
| 2017 | 0,265* | 0,302* | -0,0007 n.s. | -0,0013 n.s. |
| 2018 | 0,850*** | 0,864*** | -0,0044** | -0,0054** |
| 2019 | 0,294* (p=0,049) | 0,288 (p=0,082 n.s.) | -0,0003 n.s. | -0,0009 n.s. |
| 2021 | 0,963*** | 0,954*** | -0,0065** | -0,0072** |

Panel équilibré : 3238 unités (univarié) contre 2691 unités (score de propension) — perte cohérente avec les 16% de QPV en moins après suppression listwise. **Conclusion : les coefficients bougent peu et dans le même sens** (légèrement plus élevés en magnitude pour la pauvreté la plupart des années, 2019 repasse sous le seuil de significativité à 5% mais restait déjà la moins convaincante des années significatives, cf. section 39). Le score de propension multivarié **confirme le résultat principal plutôt qu'il ne le remet en cause** — cohérent avec le diagnostic de recouvrement ci-dessus : puisque l'appariement change peu, le résultat de régression change peu.

**Fichiers** : `scripts/08_demographie_iris_2010.py` (extraction IRIS), `data/processed/demographie_2010_iris.csv` (résultat), `scripts/09_score_propension.py` (score, ré-appariement, comparaison), `data/processed/appariement_qpv_iris_score_propension.csv` (résultat de l'appariement).

**Statut des 5 chantiers du brief limites/robustesse : tous traités** (chantiers 1, 2, 5, 3, 4 — dans l'ordre recommandé). Prochaine étape : reprendre le volet ML (typologie des QPV, clustering) resté en suspens depuis la section 36.