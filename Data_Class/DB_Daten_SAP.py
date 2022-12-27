from distutils.log import info
import datetime
import pandas as pd
import numpy as np
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL

##TODO: SAFE BACKUP LT22 BEFORE ANYTHING

class DatenAgregieren():


    
    def sapLt22DatenBerechnen(dflt22):
        #dflt22 = pd.read_excel('Data/upload/lt22.xlsx')
        dfStammdaten = SQL.sql_Stammdaten()
        dfOrders = SQL.sql_datenTabelleLaden(SQL.tabelle_DepotDEBYKNOrders)
        dfMitarbeiter = SQL.sql_datenTabelleLaden(SQL.tabellemitarbeiter)
        dflt22.set_index('Transfer Order Number', inplace=True)

        # Weil ich nunmal ein Excel Idiot bi

        dflt22.columns = ['MaterialNumber','C','D','E','F','G','H','I','J','K','L','M','MitarbeiterCreateTO','MitarbeiterConfirmTO','P','Q','R','S','T','DestStorType','DestBin','W','X','Y','Z','AA','AB','AC''ToNumber']
        dflt22['Ziel'] = dflt22['DestStorType'].str[:2]
        dflt22['Quelle'] = dflt22['E'].str[:2]
        dflt22['Pick Datum'] = dflt22['L'].dt.strftime('%m/%d/%y')
        #dflt22['K'] = dflt22['K'].astype(str)
        dflt22['MaterialNumber'] = dflt22['MaterialNumber'].astype(str)
        dflt22['K'] = pd.to_datetime(dflt22['K'], format='%H:%M:%S')
        dflt22['Pick Zeit'] = dflt22['K']
        dflt22['L'] = pd.to_datetime(dflt22['L'])
        dflt22['SuperDepot'] = dflt22['DestBin'].isin(dfOrders['SapOrderNumber'])
        dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(['CS','D97','OUT'])]
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
        dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(['CS','D97','OUT'])]   
        def f_CS(row):
            try:
                if row.UnitOfMeasure == 'CS':          
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        def f_PAL(row):
            try:
                if row.UnitOfMeasure == 'D97':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        def f_OUT(row):
            try:
                if row.UnitOfMeasure == 'OUT':
                    return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
            except:
                return np.nan
        dfStammdaten['OUT'] = dfStammdaten.apply(f_OUT,axis=1)
        dfStammdaten['CS'] = dfStammdaten.apply(f_CS,axis=1)
        dfStammdaten['PAL'] = dfStammdaten.apply(f_PAL,axis=1)
        

        dflt22 = pd.merge(dflt22, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'CS'][['MaterialNumber','CS']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')
        dflt22 = pd.merge(dflt22, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'D97'][['MaterialNumber','PAL']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')
        dflt22 = pd.merge(dflt22, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'OUT'][['MaterialNumber','OUT']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')

        # print('pickschleife')
        # #Schleife erst Picks Berechnen -> Dann Umlagerungen ermitteln
        for each in dflt22.index:
            if dflt22.loc[each, 'E'] == 'TN1' and dflt22.loc[each, 'DestStorType'] == '916' and dflt22.loc[each, 'DestStorType'] == '916':
                dflt22.loc[each, 'PICKS'] = dflt22.loc[each, 'H'] 
                dflt22.loc[each, 'Picks OUT'] = dflt22.loc[each, 'H'] 
                dflt22.loc[each, 'Pick Art'] = 'Stange'
            if dflt22.loc[each, 'E'] == 'SN1' and dflt22.loc[each, 'DestStorType'] == '916' or dflt22.loc[each, 'E'] == 'SN2' and dflt22.loc[each, 'DestStorType'] == '916' or dflt22.loc[each, 'E'] == 'SN3' and dflt22.loc[each, 'DestStorType'] == '916' or dflt22.loc[each, 'E'] == 'SN4' and dflt22.loc[each, 'DestStorType'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
                dflt22.loc[each, 'Picks CS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
                dflt22.loc[each, 'Pick Art'] = 'Karton'
            if dflt22.loc[each, 'E'] == 'BS3' and dflt22.loc[each, 'DestStorType'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']
                dflt22.loc[each, 'PICKS PAL'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']
                dflt22.loc[each, 'Pick Art'] = 'Palette'
            #Umlagerungen Ermitteln 
            if dflt22.loc[each, 'E'] == 'BS3' and dflt22.loc[each, 'Ziel'] == 'SN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Karton'
            if dflt22.loc[each, 'Quelle'] == 'RS' and dflt22.loc[each, 'Ziel'] == 'SN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Karton'
            if dflt22.loc[each, 'Quelle'] == 'SN' and dflt22.loc[each, 'Ziel'] == 'TN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Gebinde'

        ## Füge den Mitarbeiter hinzu
        # if the value of dfMitarbeiter[OneID] exists in dflt22[MitarbeiterConfirmTO] then add the value of dfMitarbeiter[Mitarbeiter] to dflt22[MitarbeiterConfirmTO]
        dflt22 = pd.merge(dflt22, dfMitarbeiter,left_on='MitarbeiterConfirmTO', right_on='One ID',how='left')
        #fill none with 'Unbekannt'
        dflt22['Name'] = dflt22['Name'].fillna('Unbekannt')
        dflt22['LieferscheinErhalten'] = dfOrders['SapOrderNumber'].apply(lambda x: dfOrders.loc[dfOrders['SapOrderNumber'] == x]['CreatedTimestamp'].iloc[0])
        dflt22['PartnerNo'] = dfOrders['SapOrderNumber'].apply(lambda x: dfOrders.loc[dfOrders['SapOrderNumber'] == x]['PartnerNo'].iloc[0])
        dflt22['SuperDepot'] = dflt22['DestBin'].isin(dfOrders['SapOrderNumber'])
        # save to parquet
        dflt22.to_parquet('Data/upload/lt22.parquet')

        #PartnerNo
        return dflt22