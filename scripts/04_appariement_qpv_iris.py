"""
Construction du groupe de contrôle final : appariement K plus proches
voisins (K=5) de chaque QPV avec des IRIS non-QPV, sur le niveau de
pauvreté pré-traitement (moyenne 2012-2014).

Règle à deux niveaux :
1. Chercher d'abord les IRIS candidats (non-miroirs) dans la MÊME COMMUNE
   que le QPV. Si au moins un candidat existe, apparier sur ce périmètre
   (jusqu'à 5 plus proches en pauvreté).
2. Si aucun candidat en commune, replier sur l'UNITÉ URBAINE (UU2020) de
   la commune : chercher parmi tous les IRIS candidats des communes de la
   même UU, apparier sur ce périmètre élargi (jusqu'à 5 plus proches).

Entrées (déjà construites, voir carnet section 17-18) :
- data/processed/qpv_pauvrete_pretraitement.csv (QPV, pauvreté 2012-2014, commune)
- data/processed/iris_pauvrete_pretraitement.csv (IRIS candidats non-miroirs,
  pauvreté 2012-2014, commune) — déjà restreint aux candidats non-miroirs
  par 03_controle_iris_miroirs.py + filtré aux IRIS avec pauvreté 2012-2014
  disponible (~24% de secret statistique exclus, voir carnet section 14 corrigée)
- data/processed/commune_vers_unite_urbaine.csv (repli géographique)

Sortie : data/processed/appariement_qpv_iris_v2.csv
(code_qpv, iris_controle, distance_pauvrete, niveau)
"""
import pandas as pd

K_VOISINS = 5


def charger_donnees(dossier='data/processed'):
    qpv = pd.read_csv(f'{dossier}/qpv_pauvrete_pretraitement.csv',
                       dtype={'code': str, 'insee_com': str})
    iris = pd.read_csv(f'{dossier}/iris_pauvrete_pretraitement.csv',
                        dtype={'iris': str, 'com': str})
    iris = iris.dropna(subset=['taux_pauvrete_pre'])
    com_uu = pd.read_csv(f'{dossier}/commune_vers_unite_urbaine.csv',
                         dtype={'commune': str, 'unite_urbaine': str})
    iris = iris.merge(com_uu, left_on='com', right_on='commune', how='left') \
                .drop(columns='commune')
    return qpv, iris, com_uu


def plus_proches(candidats, valeur_pauvrete_qpv, k=K_VOISINS):
    """Retourne les k IRIS candidats les plus proches en pauvreté."""
    c = candidats.copy()
    c['distance_pauvrete'] = (c['taux_pauvrete_pre'] - valeur_pauvrete_qpv).abs()
    return c.sort_values('distance_pauvrete').head(k)


def apparier(qpv, iris, com_uu):
    commune_to_uu = com_uu.set_index('commune')['unite_urbaine']
    resultats = []

    for _, q in qpv.iterrows():
        commune = q['insee_com']
        candidats_commune = iris[iris['com'] == commune]

        if len(candidats_commune) > 0:
            proches = plus_proches(candidats_commune, q['taux_pauvrete_pre'])
            niveau = 'commune'
        else:
            uu = commune_to_uu.get(commune)
            candidats_uu = iris[iris['unite_urbaine'] == uu] if pd.notna(uu) else iris.iloc[0:0]
            if len(candidats_uu) == 0:
                continue
            proches = plus_proches(candidats_uu, q['taux_pauvrete_pre'])
            niveau = 'unite_urbaine'

        for _, r in proches.iterrows():
            resultats.append({
                'code_qpv': q['code'],
                'iris_controle': r['iris'],
                'distance_pauvrete': r['distance_pauvrete'],
                'niveau': niveau,
            })

    return pd.DataFrame(resultats)


if __name__ == '__main__':
    qpv, iris, com_uu = charger_donnees()
    appariement = apparier(qpv, iris, com_uu)
    appariement.to_csv('data/processed/appariement_qpv_iris_v2.csv', index=False)

    n_qpv = appariement['code_qpv'].nunique()
    print(f"Appariement final : {n_qpv}/{len(qpv)} QPV appariés "
          f"({n_qpv / len(qpv):.0%}), {appariement['iris_controle'].nunique()} "
          f"IRIS de contrôle distincts")
    print(appariement.groupby('niveau')['distance_pauvrete'].agg(['count', 'mean']))
