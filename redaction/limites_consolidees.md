# Limites de la partie régression/DiD — synthèse consolidée

*Inventaire complet des limites, compromis et problèmes identifiés au cours de la partie causale du mémoire. Organisé par thème pour reprise directe dans la section "Limites".*

## 1. Contraintes de données (non choisies)
- Seulement 3 années pré-traitement disponibles (2012-2014, limite de la source Filosofi)
- DOM-TOM exclus (méthode d'identification QPV différente, couverture incomplète)
- 2015 et 2020 écartés de l'analyse principale (ambiguïté de traitement / bruit de mesure confirmé)
- Secret statistique variable par année (22-25% de valeurs masquées, panel déséquilibré en résultant)
- Logement social disponible en nombre absolu seulement, pas en proportion
- Aucune donnée individuelle : uniquement des statistiques agrégées par quartier

## 2. Compromis dans la construction du groupe de contrôle
- Appariement univarié (pauvreté pré-traitement uniquement), distance moyenne réelle 13-15 points
- Exclusion des IRIS "miroirs" par similarité de nom (approximation textuelle, validée sur 25 cas manuels)
- Règle à deux niveaux (commune puis unité urbaine), 96% de couverture atteinte
- RDD écartée : hors cours ET invalide (ajustement politique du zonage documenté deux fois)

## 3. Limite structurelle du design DiD lui-même
- La tendance parallèle pré-traitement ne protège que contre une divergence déjà présente avant traitement
- Ne protège pas contre un choc post-traitement qui active une différence de composition par ailleurs anodine (cas vérifié : logement social × réforme RLS 2018)
- Cette vigilance n'est possible que pour les facteurs auxquels on pense à chercher — pas une garantie exhaustive

## 4. Ruptures de mesure Filosofi identifiées
- 2015-2016 : réorganisation de la production des indicateurs (non quantifiée précisément)
- 2018 : réforme RLS + dégradation fichier taxe d'habitation (quantifiée : 17-46% du signal expliqué)
- 2019 : PEPA/heures sup/PAS (identifiée, mais année non significative de toute façon)
- 2020-2021 : aides Covid non captées (prouvé empiriquement par l'inversion de signe)

## 5. Résultats de validation et leurs failles
- Test de Wald : tendance parallèle validée pour la pauvreté (p=0,19), rejetée pour le revenu (p=0,04)
- Panel équilibré : améliore la lecture pauvreté, dégrade la validité du design sur le revenu
- 2017 et 2019 non significatifs : effet par activations ponctuelles, pas une tendance continue

## 6. Non résolu, assumé comme tel
- Résidu de pauvreté inexpliqué après contrôle logement social (2016, 2018, 2021)
- Hypothèse alternative (rénovation PNRU) non vérifiée faute de données ANRU
- Effet des dispositifs superposés (ANRU, éducation) non isolable du seul label QPV
