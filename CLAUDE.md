# CLAUDE.md

## Contexte du projet

Mémoire de fin de DU Data Analytics (Paris 1 Panthéon-Sorbonne), en parallèle d'un MSc Public Policy à Audencia. Format : 40 pages max + note de synthèse 2-3 pages, soutenance orale 30mn. Deadline personnelle : 3 août (avant un départ en voyage) ; rendu officiel début septembre.

Question de recherche : le classement d'un quartier en Quartier Prioritaire de la Politique de la Ville (QPV) en 2015 a-t-il eu un effet causal sur les trajectoires de revenu et de pauvreté de ses habitants ?

**Avant toute chose : lis `carnet/carnet.md` en entier.** C'est le journal complet et chronologique de toutes les décisions méthodologiques prises jusqu'ici, avec leur justification. Ce fichier CLAUDE.md ne fait que résumer les règles de travail et la boîte à outils — le carnet est la source de vérité sur ce qui a été fait et pourquoi.

## Règles de travail (à respecter absolument, posées dès le premier échange)

- Ne jamais construire de méthodologie ou de plan sur une donnée non vérifiée concrètement (recherche réelle, pas déduction depuis la doc). Toujours vérifier qu'un fichier existe, est accessible, et couvre la période voulue avant de bâtir dessus.
- Être honnête sur la faisabilité même quand ça complique ce qui est en cours — Alexandre préfère apprendre tôt qu'une piste est bancale plutôt que d'avancer sur une hypothèse optimiste.
- Expliquer tout concept technique en langage clair avant de l'utiliser, sans supposer un terme acquis. Alexandre a explicitement dit avoir "quasi tout oublié" de certains cours — repartir de zéro si besoin, avec des exemples concrets (analogies, calculs à la main).
- Ne jamais s'emballer sur un plan complet ou une méthodologie détaillée avant une décision explicite prise ensemble. Si un choix méthodologique se présente (seuil, périmètre, spécification), le poser clairement avec ses compromis plutôt que trancher seul.
- Distinguer explicitement, pour toute méthode envisagée : ce qui est dans le cours (à mobiliser directement), ce qui est une extension raisonnable du cours (à signaler comme tel), et ce qui est hors cours (à citer comme ouverture, pas à implémenter sauf accord explicite).
- Réponses détaillées et complètes, pas synthétiques.
- Ne pas partager systématiquement tous les fichiers/résultats intermédiaires sans qu'on le demande (consigne donnée en cours de route pour éviter de gonfler les échanges) — mais documenter chaque étape dans le carnet.

## Boîte à outils du cours — ce qui est acquis vs extension vs hors-cadre

**Solidement acquis (mobilisable directement) :**
- Régression linéaire, tests d'hypothèses (test T, test F/Wald pour hypothèses conjointes), hétéroscédasticité
- Panel data avec effets fixes (estimateur *within*, théorème de Frisch-Waugh)
- Variables instrumentales (2SLS, cadre LATE/compliers, évaluation de politique publique)
- Choix discret (logit/probit), ridge/lasso
- Séries temporelles (stationnarité, ARIMA)
- ML supervisé : arbres, random forest, boosting, réglage d'hyperparamètres (train/test, validation croisée)
- ML non supervisé : clustering hiérarchique, DBSCAN
- Interprétabilité des modèles ML

**Vu mais en introduction seulement (profondeur à vérifier au cas par cas) :** deep learning (intro), NLP (intro)

**Extension raisonnable du cours (à signaler comme telle, pas un prérequis) :**
- Différence de différences (DiD) : pas enseignée telle quelle, mais implémentable comme régression à effets fixes (individu + temps) avec interaction traitement × période — c'est exactement l'approche retenue pour ce mémoire (voir carnet).

**Hors cadre du cours, à ne PAS mobiliser sauf demande explicite :**
- Régression sur discontinuité (RDD) — écartée de toute façon pour ce sujet précis (ajustement politique du zonage QPV, cf. carnet section 22/34)
- Contrôle synthétique, appariement par score de propension formel (PSM), tests placebo/randomisation — mentionnés en discussion mais explicitement écartés par Alexandre pour rester dans le cadre du cours

## État d'avancement (résumé — détails complets dans le carnet)

- **Partie régression/DiD : CLÔTURÉE.** Résultat final dans `redaction/partie_regression_finale.md`. Design : QPV appariés à des IRIS de contrôle sur pauvreté pré-traitement (2012-2014), panel équilibré 2012-2021 (hors 2020 pour la régression principale, biais Covid démontré empiriquement), référence groupée 2012-2014. Tendance parallèle validée (test de Wald) pour la pauvreté, rejetée pour le revenu (résultat secondaire).
- **Partie ML : en cours.** Objectif : typologie des QPV (clustering) pour tester l'hétérogénéité de l'effet trouvé, en particulier l'hypothèse de mobilité résidentielle (rejetée dans un premier test simple, cf. carnet section 36 — le clustering formel reste à faire). Données démographiques riches disponibles (2010, 2017-2024) mais encore peu exploitées.

## Structure du dépôt

- `carnet/carnet.md` — journal chronologique complet, source de vérité
- `scripts/` — scripts Python réutilisables et testés (construction des panels, régression event-study, tests de robustesse)
- `data/processed/` — jeux de données déjà construits (panels, appariements, résultats)
- `data/raw/` — non versionné, fichiers bruts INSEE volumineux (voir .gitignore)
- `redaction/` — textes rédigés prêts pour intégration au mémoire

## Style de travail attendu de Claude Code

Même exigence de rigueur que dans le carnet : vérifier les données avant de coder dessus, expliquer les choix, ne pas volontairement rendre un résultat plus propre qu'il ne l'est. Mettre à jour `carnet/carnet.md` après chaque étape significative, dans le même style que l'existant (numérotation de section continue, ce qui a été fait / trouvé / décidé).
