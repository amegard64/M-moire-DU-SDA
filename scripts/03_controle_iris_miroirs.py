"""
Deux étapes de construction du groupe de contrôle :
1. Lien QP2015 -> commune (via QP2024 comme intermédiaire, faute du fichier
   TAG_QPV_2015 direct)
2. Exclusion des IRIS "miroirs" (probable chevauchement géographique avec un
   QPV) par similarité de noms - approximation documentée comme limite,
   validée manuellement sur 25 cas sans faux positif détecté (voir carnet).
"""
import pandas as pd
import unicodedata
import re

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
