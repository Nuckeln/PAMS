import pandas as pd
import numpy as np
import plotly as py
import uuid


from Data_Class.MMSQL_connection import read_Table, save_Table

def fuege_Stammdaten_zu_LT22():
    '''This function calculates the Order Quantity for Case and PAL and merges the Masterdata to the df
    :return: save to SQL Table = Tall_Pall_Orders'''
    
    df = pd.read_excel('Doku Langenbach 29-04-24.xlsx', sheet_name='LT22 Export', header=0)
    dfMasterdata = read_Table('data_materialmaster-MaterialMasterUnitOfMeasures')
    dfPAMSMasterdata = read_Table('PAMS_TALL_MASTERDATA')
    dfMasterdata

    dfMasterdata['MaterialNumber'] = dfMasterdata['MaterialNumber'].str.replace('0000000000', '')

    df['Material'] = df['Material'].astype(str)
    df_merged_Case = pd.merge(df, dfMasterdata[dfMasterdata['UnitOfMeasure'] == 'CS'], left_on='Material', right_on='MaterialNumber', how='left')
    df_merged_Case['MM_TH_Pro_Karton'] = df_merged_Case.NumeratorToBaseUnitOfMeasure / df_merged_Case.DenominatorToBaseUnitOfMeasure
    df['MM_TH_Pro_Karton'] = df_merged_Case['MM_TH_Pro_Karton']
    df['height_Case'] = df_merged_Case['Height']
    df['length_Case'] = df_merged_Case['Length']
    df['width_Case'] = df_merged_Case['Width']

    df_merged_pal = pd.merge(df, dfMasterdata[dfMasterdata['UnitOfMeasure'] == 'D97'], left_on='Material', right_on='MaterialNumber', how='left')
    df_merged_pal['MM_TH_Pro_Palette'] = df_merged_pal.NumeratorToBaseUnitOfMeasure / df_merged_pal.DenominatorToBaseUnitOfMeasure
    df['MM_TH_Pro_Palette'] = df_merged_pal['MM_TH_Pro_Palette']
    df['height_PAL'] = df_merged_pal['Height']
    df['length_PAL'] = df_merged_pal['Length']
    df['width_PAL'] = df_merged_pal['Width']

    df_merged_PD = pd.merge(df, dfMasterdata[dfMasterdata['UnitOfMeasure'] == 'PD'], left_on='Material', right_on='MaterialNumber', how='left')
    df_merged_PD['Case_on_Layer'] = df_merged_PD.NumeratorToBaseUnitOfMeasure / df_merged_PD.DenominatorToBaseUnitOfMeasure
    df['Case_on_Layer'] = df_merged_PD['Case_on_Layer']

    # ########## UNTERBAU  ##########
    dfPAMSMasterdata['SKU'] = dfPAMSMasterdata['SKU'].astype(str)
    df = pd.merge(df, dfPAMSMasterdata, left_on='Material', right_on='SKU', how='left')
    nan_indices = df[df['AUFPACKEN_JA_NEIN'].isna()].index
    df.loc[nan_indices, 'GEEIGNET_UNTERBAU'] = 'FALSE'
    df.loc[nan_indices, 'AUFPACKEN_JA_NEIN'] = 'FALSE'
    df

    df['Teilbar_durch'] =  df['MM_TH_Pro_Palette'].astype(int) / df['Case_on_Layer'].astype(int)
    df['Teilbar_durch'] = df['Teilbar_durch'].astype(float)
    df['Pal_ID'] = [uuid.uuid4() for _ in range(len(df.index))]
    df['Teilbar_durch'] = df['Teilbar_durch'].apply(lambda x: round(x))
    df['Teilhöhe'] = df['height_PAL'].astype(float) / df['Teilbar_durch']
    df['Teilhöhe'] = df['Teilhöhe'].apply(lambda x: round(x, 2)) + 1
    return df 


