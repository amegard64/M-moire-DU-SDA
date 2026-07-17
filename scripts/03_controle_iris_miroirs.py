"""
Construction complète du groupe de contrôle, de bout en bout :
1. Lien QP2015 -> commune (via QP2024 comme intermédiaire, faute du fichier
   TAG_QPV_2015 direct) - fonction conservée pour mémoire, mais plus utilisée
   dans le pipeline principal : qpv_info_nom_commune.csv (déjà committé) vient
   directement du fichier TAG_QPV_2015, qui a une meilleure couverture (voir
   carnet section 18).
2. Exclusion des IRIS "miroirs" (probable chevauchement géographique avec un
   QPV) par similarité de noms - approximation documentée comme limite,
   validée manuellement sur 25 cas sans faux positif détecté (voir carnet).
3. Pauvreté pré-traitement (moyenne 2012-2014) pour QPV et IRIS candidats.
4. Appariement K plus proches voisins (commune, repli unité urbaine).

Le `__main__` reconstruit iris_controle_candidats.csv,
qpv_pauvrete_pretraitement.csv, iris_pauvrete_pretraitement.csv et
appariement_qpv_iris_v2.csv à partir des fichiers déjà committés
(panel_qpv_complet_v2.csv, panel_iris_complet_v2.csv, qpv_info_nom_commune.csv,
rpls_iris.csv, commune_vers_unite_urbaine.csv) - vérifié en juillet 2026 pour
reproduire à l'identique (mêmes lignes, mêmes valeurs à la précision flottante
près) les quatre fichiers déjà présents dans le dépôt.

Point technique important, découvert en écrivant cette reconstruction :
l'exclusion des miroirs (étape 2) doit comparer le nom du QPV au nom PROPRE
de l'IRIS, pas au nom de sa commune. panel_iris_complet_v2.csv ne contient
que le nom de la commune (`libcom`, identique pour tous les IRIS d'une même
commune) - inutilisable pour cette comparaison. Le nom propre de chaque IRIS
(`LibGeo`, ex. "Les Pérouses-Triangle d'Activités") se trouve dans
rpls_iris.csv. Les quelques IRIS sans entrée RPLS (15 cas) sont exclus par
prudence, faute de nom à comparer - règle qui reproduit exactement le fichier
existant.

commune_vers_unite_urbaine.csv n'est PAS régénéré ici : ce n'est pas une
sortie du pipeline mais une table de référence externe (nomenclature
géographique INSEE, voir carnet section 17), au même titre qu'un fichier
data/raw/. Elle doit être conservée telle quelle.
"""
import pandas as pd
import unicodedata
import re

K_VOISINS = 5
ANNEES_PRETRAITEMENT = [2012, 2013, 2014]

MOTS_VIDES = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'au', 'aux',
              'a', 'en', 'sur', 'sous', 'quartier', 'quartiers'}
SEUIL_SIMILARITE = 0.5


def normalise(texte):
    """Minuscules, sans accents, sans mots vides, ensemble de mots."""
    if pd.isna(texte):
        return set()
    texte = str(texte).lower()
    texte = unicodedata.normalize('NFKD', texte).encode('ascii', 'ignore').decode('utf-8')
    mots = re.findall(r'\w+', texte)
    return set(m for m in mots if m not in MOTS_VIDES and len(m) > 2)


def similarite_jaccard(mots_a, mots_b):
    if not mots_a or not mots_b:
        return 0
    return len(mots_a & mots_b) / len(mots_a | mots_b)


def lier_qp2015_a_commune(fichier_correspondance, fichier_liste_qp2024):
    """QP2015 -> QP2024 (reshape long) -> commune (via liste QP2024)."""
    corr = pd.read_csv(fichier_correspondance, sep=';', encoding='utf-8-sig')
    corr.columns = [c.strip() for c in corr.columns]

    parts = []
    for i in [1, 2, 3]:
        col = f'QP2015_{i}'
        if col in corr.columns:
            sub = corr[['QP2024', col]].dropna(subset=[col]).rename(columns={col: 'QP2015'})
            sub['QP2015'] = sub['QP2015'].str.strip()
            parts.append(sub)
    long_corr = pd.concat(parts, ignore_index=True)

    cog = pd.read_csv(fichier_liste_qp2024, sep=';', encoding='utf-8-sig')
    cog.columns = [c.strip() for c in cog.columns]
    cog = cog[['code_qp', 'insee_com', 'lib_com']].dropna(subset=['code_qp'])

    link = long_corr.merge(cog, left_on='QP2024', right_on='code_qp', how='left')
    return link[['QP2015', 'insee_com', 'lib_com']].drop_duplicates('QP2015')


def exclure_iris_miroirs(iris_df, qpv_par_commune, seuil=SEUIL_SIMILARITE):
    """Marque probable_chevauchement=True pour les IRIS dont le nom
    ressemble fortement à un QPV de la même commune."""
    def calcule_similarite_max(row):
        noms_qpv = qpv_par_commune.get(row['com'], [])
        mots_iris = normalise(row['libcom'] if 'libiris' not in row else row['libiris'])
        sims = [similarite_jaccard(mots_iris, normalise(n)) for n in noms_qpv]
        return max(sims) if sims else 0

    iris_df = iris_df.copy()
    iris_df['similarite_qpv'] = iris_df.apply(calcule_similarite_max, axis=1)
    iris_df['probable_chevauchement'] = iris_df['similarite_qpv'] >= seuil
    return iris_df


# NOTE méthodologique (à garder dans le mémoire, section limites) :
# Cette exclusion par nom est une approximation, pas une vérification
# géographique réelle (pas de croisement de polygones QPV/IRIS, hors du
# cadre des cours suivis). Validée manuellement sur 25 cas répartis sur des
# communes variées (dont deux à 9 QPV chacune) sans faux positif détecté,
# mais cela ne remplace pas une validation systématique.


def construire_iris_candidats(panel_iris, qpv_info, rpls_iris):
    """IRIS candidats au contrôle : dans une commune qui a un QPV, non-miroir
    (voir exclure_iris_miroirs). Le nom propre de l'IRIS vient de rpls_iris
    (LibGeo) - un IRIS sans entrée RPLS est exclu par prudence, faute de nom
    à comparer."""
    qpv_communes = set(qpv_info['insee_com'])
    iris_unique = panel_iris.drop_duplicates('iris')[['iris', 'com']]
    cand = iris_unique[iris_unique['com'].isin(qpv_communes)].merge(
        rpls_iris[['CodGeo', 'LibGeo']].rename(columns={'CodGeo': 'iris', 'LibGeo': 'libiris'}),
        on='iris', how='left')

    qpv_par_commune = qpv_info.groupby('insee_com')['nom_qp'].apply(list).to_dict()
    marque = exclure_iris_miroirs(cand, qpv_par_commune)
    marque.loc[marque['libiris'].isna(), 'probable_chevauchement'] = True
    return marque[~marque['probable_chevauchement']][['iris', 'com']].reset_index(drop=True)


def construire_pauvrete_pretraitement_qpv(panel_qpv, qpv_info):
    """Moyenne du taux de pauvreté 2012-2014 par QPV, avec nom et commune."""
    pre = panel_qpv[panel_qpv['annee'].isin(ANNEES_PRETRAITEMENT)]
    moy = pre.groupby('code')['taux_pauvrete'].mean().reset_index() \
        .rename(columns={'taux_pauvrete': 'taux_pauvrete_pre'})
    return moy.merge(qpv_info, on='code')[['code', 'taux_pauvrete_pre', 'nom_qp', 'insee_com']]


def construire_pauvrete_pretraitement_iris(panel_iris, iris_candidats):
    """Moyenne du taux de pauvreté 2012-2014 pour les IRIS candidats.
    Jointure INNER (pas dropna) : un IRIS absent du panel 2012-2014 est
    écarté, mais un IRIS présent avec pauvreté masquée les 3 années (secret
    statistique) est conservé avec taux_pauvrete_pre=NaN - c'est ce que fait
    le fichier existant, et l'appariement (voir plus bas) en dépend pour
    reproduire le même nombre de contrôles par QPV."""
    pre = panel_iris[panel_iris['annee'].isin(ANNEES_PRETRAITEMENT)]
    moy = pre.groupby('iris')['taux_pauvrete'].mean().reset_index() \
        .rename(columns={'taux_pauvrete': 'taux_pauvrete_pre'})
    return iris_candidats.merge(moy, on='iris', how='inner')[['iris', 'taux_pauvrete_pre', 'com']]


def _plus_proches(candidats, valeur_pauvrete_qpv, k=K_VOISINS):
    c = candidats.copy()
    c['distance_pauvrete'] = (c['taux_pauvrete_pre'] - valeur_pauvrete_qpv).abs()
    # na_position='last' : un IRIS à pauvreté masquée n'est jamais préféré à
    # un IRIS à distance connue, mais reste inclus si la commune/UU n'a pas
    # k candidats à distance connue - reproduit le comportement du fichier
    # existant (colonne distance_pauvrete vide pour ces cas, jamais plus de
    # k lignes par QPV).
    return c.sort_values('distance_pauvrete', na_position='last').head(k)


def apparier_qpv_iris(qpv_pauvrete_pre, iris_pauvrete_pre, commune_vers_uu):
    """Appariement K plus proches voisins sur la pauvreté pré-traitement,
    priorité à la commune, repli sur l'unité urbaine si aucun candidat en
    commune (voir carnet section 17-18)."""
    iris = iris_pauvrete_pre.merge(commune_vers_uu, left_on='com', right_on='commune', how='left') \
        .drop(columns='commune')
    commune_to_uu = commune_vers_uu.set_index('commune')['unite_urbaine']
    qpv = qpv_pauvrete_pre.dropna(subset=['taux_pauvrete_pre'])

    resultats = []
    for _, q in qpv.iterrows():
        commune = q['insee_com']
        candidats_commune = iris[iris['com'] == commune]
        if len(candidats_commune) > 0:
            proches = _plus_proches(candidats_commune, q['taux_pauvrete_pre'])
            niveau = 'commune'
        else:
            uu = commune_to_uu.get(commune)
            candidats_uu = iris[iris['unite_urbaine'] == uu] if pd.notna(uu) else iris.iloc[0:0]
            if len(candidats_uu) == 0:
                continue
            proches = _plus_proches(candidats_uu, q['taux_pauvrete_pre'])
            niveau = 'unite_urbaine'
        for _, r in proches.iterrows():
            resultats.append({'code_qpv': q['code'], 'iris_controle': r['iris'],
                               'distance_pauvrete': r['distance_pauvrete'], 'niveau': niveau})
    return pd.DataFrame(resultats)


if __name__ == '__main__':
    dossier = 'data/processed'
    panel_qpv = pd.read_csv(f'{dossier}/panel_qpv_complet_v2.csv', dtype={'code': str})
    panel_iris = pd.read_csv(f'{dossier}/panel_iris_complet_v2.csv', dtype={'iris': str, 'com': str})
    qpv_info = pd.read_csv(f'{dossier}/qpv_info_nom_commune.csv', dtype={'code': str, 'insee_com': str})
    rpls_iris = pd.read_csv(f'{dossier}/rpls_iris.csv', dtype=str)
    commune_vers_uu = pd.read_csv(f'{dossier}/commune_vers_unite_urbaine.csv',
                                   dtype={'commune': str, 'unite_urbaine': str})

    candidats = construire_iris_candidats(panel_iris, qpv_info, rpls_iris)
    qpv_pre = construire_pauvrete_pretraitement_qpv(panel_qpv, qpv_info)
    iris_pre = construire_pauvrete_pretraitement_iris(panel_iris, candidats)
    appariement = apparier_qpv_iris(qpv_pre, iris_pre, commune_vers_uu)

    candidats.to_csv(f'{dossier}/iris_controle_candidats.csv', index=False)
    qpv_pre.to_csv(f'{dossier}/qpv_pauvrete_pretraitement.csv', index=False)
    iris_pre.to_csv(f'{dossier}/iris_pauvrete_pretraitement.csv', index=False)
    appariement.to_csv(f'{dossier}/appariement_qpv_iris_v2.csv', index=False)

    n_qpv = appariement['code_qpv'].nunique()
    print(f"Candidats IRIS : {len(candidats)}")
    print(f"QPV avec pauvreté pré-traitement : {len(qpv_pre)}")
    print(f"IRIS avec pauvreté pré-traitement : {len(iris_pre)}")
    print(f"Appariement final : {n_qpv}/{len(qpv_pre)} QPV appariés ({n_qpv / len(qpv_pre):.0%}), "
          f"{appariement['iris_controle'].nunique()} IRIS de contrôle distincts")
