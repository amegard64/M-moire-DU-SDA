"""
Construction du panel IRIS (groupe de contrôle candidat) à partir des
fichiers INSEE bruts. Contrairement aux QPV, pas de fichier socio séparé :
taux de pauvreté et médiane sont dans le même fichier "revenu disponible".

Entrée : data/raw/iris_{annee}/*.xls(x)
Sortie : data/processed/panel_iris.csv
"""
import xlrd
import openpyxl
import pandas as pd
import glob


def lire_iris_ancien(annee, dossier='data/raw'):
    """Format .xls (2012-2019 environ). En-tête technique toujours en ligne 5,
    mais VÉRIFIER avant de généraliser à de nouvelles années non testées."""
    f = glob.glob(f'{dossier}/iris_{annee}/*{annee}*')[0]
    wb = xlrd.open_workbook(f)
    sh = wb.sheet_by_name('IRIS_DISP')
    header = sh.row_values(5)
    data = [sh.row_values(r) for r in range(6, sh.nrows)]
    df = pd.DataFrame(data, columns=header)
    df = df[df['IRIS'].astype(str).str.len() > 5]
    yy = str(annee)[2:]
    df_slim = df[['IRIS', 'COM', 'LIBCOM', f'DISP_TP60{yy}', f'DISP_MED{yy}']].copy()
    df_slim.columns = ['iris', 'com', 'libcom', 'taux_pauvrete', 'revenu_median']
    df_slim['annee'] = annee
    df_slim['com'] = df_slim['com'].astype(str)
    return df_slim


def lire_iris_recent(annee, dossier='data/raw'):
    """Format .xlsx récent (2021+), structure openpyxl."""
    f = glob.glob(f'{dossier}/iris_{annee}/*.xlsx')[0]
    wb = openpyxl.load_workbook(f, data_only=True)
    ws = wb['IRIS_DISP']
    data = list(ws.iter_rows(min_row=6, values_only=True))
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df[df['IRIS'].notna()].copy()
    yy = str(annee)[2:]
    df_slim = df[['IRIS', 'COM', 'LIBCOM', f'DISP_TP60{yy}', f'DISP_MED{yy}']].copy()
    df_slim.columns = ['iris', 'com', 'libcom', 'taux_pauvrete', 'revenu_median']
    df_slim['annee'] = annee
    df_slim['com'] = df_slim['com'].astype(str)
    return df_slim


if __name__ == '__main__':
    panels = []
    for annee in [2012, 2013, 2014]:
        panels.append(lire_iris_ancien(annee))
    for annee in [2021]:
        panels.append(lire_iris_recent(annee))

    panel_complet = pd.concat(panels, ignore_index=True)
    panel_complet.to_csv('data/processed/panel_iris.csv', index=False)
    print(f"Panel IRIS construit : {len(panel_complet)} lignes")
    print(panel_complet.groupby('annee').size())
