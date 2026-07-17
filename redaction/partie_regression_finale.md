# Partie régression / DiD — synthèse finale (clôturée)

*Ce document constitue la version rédigée et prête à l'emploi de la partie causale du mémoire. Il peut être repris presque tel quel pour la section "Résultats", moyennant adaptation du style.*

---

## 1. Rappel du design

Question de recherche : le classement d'un quartier en Quartier Prioritaire de la Politique de la Ville (QPV) en 2015 a-t-il eu un effet sur les trajectoires de revenu et de pauvreté de ses habitants ?

Méthode : différence de différences (DiD), implémentée comme régression à effets fixes individuels et temporels avec interaction traitement × année (extension du panel data / estimateur *within* de Frisch-Waugh) :

```
Y_it = α_i + λ_t + Σ_k β_k·(Traité_i × Année_k) + ε_it
```

Groupe traité : QPV (génération 2015, géographie stable 2015-2023). Groupe de contrôle : IRIS non-QPV appariés sur le taux de pauvreté pré-traitement (2012-2014), au niveau communal en priorité, unité urbaine en repli. Référence temporelle : moyenne des années 2012-2014 (plutôt qu'une seule année, pour plus de robustesse). Erreurs standard groupées par commune.

## 2. Échantillon final

- 3218 unités (972 QPV + 2246 IRIS de contrôle), présentes sur les 10 années sans exception (panel strictement équilibré)
- 10 années : 2012 à 2021, à l'exclusion de 2015 et 2020 dans les versions préliminaires (réintégrées dans la version finale après vérification)
- 640 communes distinctes (clusters pour l'inférence)
- Périmètre : France métropolitaine uniquement (DOM-TOM exclus, méthode d'identification QPV différente et couverture de données incomplète)

## 3. Validation du design : la tendance parallèle tient pour la pauvreté, pas pour le revenu

Un test de Wald conjoint sur les coefficients pré-traitement (H0 : les écarts QPV-contrôle de 2012 et 2013 sont nuls) donne :
- **Taux de pauvreté : statistique de Wald = 3,34, p = 0,19 → H0 non rejetée.** La tendance parallèle est validée statistiquement pour cette variable.
- **Revenu médian (log) : statistique de Wald = 6,25, p = 0,04 → H0 rejetée.** La tendance parallèle est mise en doute par un test formel, pas seulement par une lecture visuelle des coefficients.

**Conséquence méthodologique assumée : l'analyse causale principale porte sur le taux de pauvreté. Le revenu médian est reporté à titre secondaire et indicatif, sa validité de design étant statistiquement questionnable.**

## 4. Résultats — taux de pauvreté (résultat principal)

| Année | Écart QPV-contrôle (points, réf. 2012-2014) | Significatif à 5% |
|---|---|---|
| 2015 | +0,33 | Oui |
| 2016 | +0,41 | Oui |
| 2017 | +0,17 | Non |
| 2018 | +0,67 | Oui |
| 2019 | +0,15 | Non |
| 2020 | -0,41 | Oui (signe opposé) |
| 2021 | +0,72 | Oui |

*(Spécification incluant un contrôle logement social × année, cf. section 6)*

**Lecture** : à partir de 2015, un écart de pauvreté positif apparaît entre QPV et contrôle, significatif la plupart des années sauf 2017 et 2019. Le contrôle est validé statistiquement (tendance parallèle non rejetée), ce qui distingue ce résultat d'une simple corrélation observée.

## 5. Résultats — revenu médian (secondaire, à interpréter avec prudence)

Coefficients disponibles mais **non retenus comme preuve causale** compte tenu de l'échec du test de tendance parallèle. Mentionnés uniquement pour transparence méthodologique et cohérence directionnelle avec le résultat sur la pauvreté (les années significatives coïncident largement entre les deux variables, dans des directions cohérentes : revenu en baisse quand pauvreté en hausse).

## 6. Facteurs explicatifs identifiés et quantifiés

Trois facteurs de confusion ont été identifiés et, pour deux d'entre eux, quantifiés :

1. **Logement social** : les QPV de l'échantillon ont en moyenne 2,6 fois plus de logements sociaux que leurs contrôles appariés (vérifié sur données RPLS 2022, pas une supposition générale). La réforme du loyer de solidarité (RLS, 2018), qui affecte spécifiquement le parc social, explique une partie substantielle (17 à 46% selon l'année) de l'écart mesuré. Un contrôle logement social × année est donc intégré à la spécification finale.
2. **Ruptures méthodologiques Filosofi documentées** : réorganisation de la production des indicateurs en 2015-2016 (bascule vers le Recensement pour plusieurs variables socio-démographiques), réforme du prélèvement à la source et primes exceptionnelles non captées en 2019, aides exceptionnelles Covid non captées en 2020-2021.
3. **Signes opposés 2020/2021** : preuve empirique directe (pas une simple supposition) que ces deux années ne peuvent fournir aucune inférence causale fiable — un même dispositif ne peut produire un effet inversé d'une année sur l'autre.

## 7. Limite non résolue, transmise au volet suivant (ML)

Une hypothèse alternative, non testée dans cette partie faute de données adaptées (nécessiterait des données de population/nombre de ménages sur la période, non disponibles dans les sources mobilisées ici) : une partie de l'écart pourrait refléter un **effet de composition lié à la mobilité résidentielle** plutôt qu'un effet causal du classement — les ménages dont la situation s'améliore ayant statistiquement plus de chances de quitter le quartier (mécanisme documenté par L'Institut Paris Region, 2025, comme l'un des deux facteurs principaux de sortie du classement QPV). Cette hypothèse est transmise au volet ML comme piste d'approfondissement.

## 8. Conclusion de la partie (à utiliser telle quelle ou reformulée)

*Le classement en QPV est associé, à partir de 2015, à un écart de taux de pauvreté statistiquement significatif la plupart des années par rapport à un groupe de contrôle apparié, avec une hypothèse de tendance parallèle validée formellement pour cette variable. Une partie substantielle de cet écart s'explique par des facteurs de mesure identifiés et quantifiés (réforme du logement social, ruptures méthodologiques dans la source de données). Un résidu demeure, dont l'origine — effet causal propre au classement, effet de composition lié à la mobilité résidentielle, ou autre facteur non observé — ne peut être tranchée avec les seules données de revenu mobilisées ici. Le résultat sur le revenu médian, present à titre secondaire, ne bénéficie pas de la même validation méthodologique et n'est pas interprété causalement.*

---

*Fin de la partie régression/DiD — statut : clôturée. Prochaine étape : volet ML (typologie, hétérogénéité, piste de la mobilité résidentielle).*
