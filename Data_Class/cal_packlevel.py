from src.sql import SQL
from src.read_synapse import Synapse_Daten
import pandas as pd
import numpy as np

class cal_masterdata:
    @classmethod
    def get_Masterdata_mit_packlevel():
        try: 
            dfStammdaten = Synapse_Daten.read_parquet_from_blob('raw/Shared/Global/MasterData/MaterialMaster/MaterialMasterUnitOfMeasures.parquet')
        except:
            dfStammdaten = pd.read_csv('rohdaten/MaterialMasterUnitOfMeasures.csv')
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
        dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(['CS','D97','OUT','PK'])]
        #dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
        def f_OUT(row):
            try:
                if row.UnitOfMeasure == 'OUT':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        dfStammdaten['OUT'] = dfStammdaten.apply(f_OUT,axis=1)
        def f_OUT_Gewicht(row):
            try:
                if row.UnitOfMeasure == 'OUT':
                    return row.GrossWeight
            except:
                return np.nan
        dfStammdaten['OUT_Gewicht'] = dfStammdaten.apply(f_OUT_Gewicht,axis=1)
        def f_CS(row):
            try:
                if row.UnitOfMeasure == 'CS':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        dfStammdaten['CS'] = dfStammdaten.apply(f_CS,axis=1)
        def f_CS_Gewicht(row):
            try:
                if row.UnitOfMeasure == 'CS':
                    return row.GrossWeight
            except:
                return np.nan
        dfStammdaten['CS_Gewicht'] = dfStammdaten.apply(f_CS_Gewicht,axis=1)
        def f_PAL(row):
            try:
                if row.UnitOfMeasure == 'D97':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        dfStammdaten['PAL'] = dfStammdaten.apply(f_PAL,axis=1)
        def f_PAL_Gewicht(row):
            try:
                if row.UnitOfMeasure == 'D97':
                    return row.GrossWeight
            except:
                return np.nan
        dfStammdaten['PAL_Gewicht'] = dfStammdaten.apply(f_PAL_Gewicht,axis=1)
        def f_PK(row):
            try:
                if row.UnitOfMeasure == 'PK':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        dfStammdaten['PK'] = dfStammdaten.apply(f_PK,axis=1)
        def f_PK_Gewicht(row):
            try:
                if row.UnitOfMeasure == 'PK':
                    return row.GrossWeight
            except:
                return np.nan
        dfStammdaten['PK_Gewicht'] = dfStammdaten.apply(f_PK_Gewicht,axis=1)
        dfStammdaten = dfStammdaten[['MaterialNumber', 'OUT', 'CS', 'PAL', 'PK', 'OUT_Gewicht', 'CS_Gewicht', 'PAL_Gewicht', 'PK_Gewicht']]

        # Daten bereinigen (NaN durch 0 ersetzen)
        dfStammdaten = dfStammdaten.fillna(0)

        # Gruppieren nach MaterialNumber und Aggregation
        dfStammdaten = dfStammdaten.groupby('MaterialNumber').sum().reset_index()
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].astype(str)

        return dfStammdaten
    
    @classmethod
    def cal_packing_combination(row, mengen_Spalte):
        epsilon = 1e-9      # kleiner Wert zur Kompensation von Rundungsfehlern
        tolerance = 1e-8    # Toleranz, um fast null zu erkennen

        # 1. Paletten ermitteln:
        if row['PAL'] > 0:
            paletten = int((row[mengen_Spalte] + epsilon) // row['PAL'])
        else:
            paletten = 0
        rest_after_pal = row[mengen_Spalte] - (paletten * row['PAL'])
        
        # 2. Cases ermitteln:
        if row['CS'] > 0:
            cases = int((rest_after_pal + epsilon) // row['CS'])
        else:
            cases = 0
        rest_after_cs = rest_after_pal - (cases * row['CS'])
        if abs(rest_after_cs) < tolerance:
            rest_after_cs = 0

        # 3. Outers ermitteln:
        # Hier wird angenommen, dass die Einheit für Outers in der Spalte 'OUT' hinterlegt ist.
        if row['OUT'] > 0:
            outers = int((rest_after_cs + epsilon) // row['OUT'])
        else:
            outers = 0
        rest_after_outers = rest_after_cs - (outers * row['OUT'])
        if abs(rest_after_outers) < tolerance:
            rest_after_outers = 0

        # 4. Packs ermitteln (aufgerundet, da keine halben Packs möglich sind):
        if row['PK'] > 0:
            # Sicherstellen, dass kein negativer Rest vorliegt
            rest_after_outers = max(rest_after_outers, 0)
            packs = int(np.ceil(rest_after_outers / row['PK']))
        else:
            packs = 0

        return pd.Series([paletten, cases, outers, packs], index=["Paletten", "Cases", "Outers", "Packs"])
    
    def teil_menge_in_Lieferverpackungseinheiten(MaterialnummerSpalte: str,Mengen_Spalte:str , dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Diese Funktion berechnet die Anzahl der Paletten, Cases, Outers und Packs für jede Position über die Mengenspalte der BaseUnitofMessure (TH,KG) in einem DataFrame.
        """


        # Wende die Funktion auf das DataFrame an:
        
        df_masterdata = cal_masterdata.get_Masterdata_mit_packlevel()
        df = df.merge(df_masterdata, left_on=MaterialnummerSpalte, right_on='MaterialNumber', how='left')
        
        df[["Paletten", "Cases", "Outers", "Packs"]] = df.apply(cal_masterdata.cal_packing_combination, axis=1)
        
        return df
    
    def teil_menge_in_vorgegebene_Lieferverpackungseinheiten(MaterialnummerSpalte: str,Mengen_Spalte:str ,sel_verpackungseinheit: str, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Diese Funktion rechnet die BaseUnitofMessure (TH,KG) in eine gewählte Lieferverpackungseinheit um z.B. 265 TH in 2 Paletten und 1 Packung.
        Aktuell werden nur die Einheiten Paletten, Cases, Outers und Packs unterstützt.

        :param MaterialnummerSpalte: Name der Spalte mit den Materialnummern
        :param Mengen_Spalte: Name der Spalte mit den Mengen
        :param sel_verpackungseinheit: Die gewählte Lieferverpackungseinheit (z.B. 'PAL', 'CS', 'OUT', 'PK')
        :param dataframe: Das DataFrame, das die Daten enthält
        :return: Ein DataFrame mit den berechneten Paletten, Cases, Outers und Packs
        """
        # Wende die Funktion auf das DataFrame an:
        # if pal change to D97
        if sel_verpackungseinheit == 'PAL':
            sel_verpackungseinheit = 'D97'
        try: 
            #dfStammdaten = Synapse_Daten.read_parquet_from_blob('raw/Shared/Global/MasterData/MaterialMaster/MaterialMasterUnitOfMeasures.parquet')
            dfStammdaten = pd.read_csv('rohdaten/MaterialMasterUnitOfMeasures.csv')

            print('Daten aus Synapse geladen')
        except:
            dfStammdaten = pd.read_csv('rohdaten/MaterialMasterUnitOfMeasures.csv')
            print('Daten aus CSV geladen')
            
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
        # Filter gezielt nur auf die gewählte Verpackungseinheit
        dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'] == sel_verpackungseinheit].copy()
        dfStammdaten['Faktor'] = dfStammdaten['NumeratorToBaseUnitOfMeasure'] / dfStammdaten['DenominatorToBaseUnitOfMeasure']
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].astype(str)         
        dataframe = dataframe.merge(dfStammdaten[['MaterialNumber', 'Faktor']], 
                                    left_on=MaterialnummerSpalte, 
                                    right_on='MaterialNumber', 
                                    how='left')

        dataframe.drop(columns=['MaterialNumber'], inplace=True)
        dataframe['MengeSpalte_ORG'] = dataframe[Mengen_Spalte]
        dataframe[Mengen_Spalte] = dataframe[Mengen_Spalte] / dataframe['Faktor']
        dataframe.drop(columns=['Faktor'], inplace=True)

        return dataframe