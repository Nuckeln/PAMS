
import streamlit as st
import hydralit_components as hc
from Data_Class.cal_lt22_TALL_Data import fuege_Stammdaten_zu_LT22


def berechne_stapeln(df):
    # Festlegen der maximalen Höhe
    max_height = 255

    # Erstelle eine Kopie des DataFrames, um die Bearbeitung und Tracking zu erleichtern
    df_stacking = df.copy()

    # Hinzufügen einer Spalte zur Verfolgung der verbleibenden Höhe, die hinzugefügt werden kann
    df_stacking['verbleibende_Höhe'] = max_height - df_stacking['height_PAL']

    # Sortiere die Paletten nach geeignetem Unterbau und dann nach der Möglichkeit aufzupacken
    df_stacking.sort_values(by=['GEEIGNET_UNTERBAU', 'AUFPACKEN_JA_NEIN', 'height_PAL'], ascending=[False, False, True], inplace=True)

    # Liste zur Erfassung der Stapelungsdetails
    stapel_details = []

    # Durchlaufe die Paletten, um Stapelungen zu planen
    for index, target in df_stacking[df_stacking['GEEIGNET_UNTERBAU']].iterrows():
        if target['verbleibende_Höhe'] <= 0:
            continue
        
        # Identifiziere mögliche Paletten, die auf diese Palette gestapelt werden könnten
        for idx, source in df_stacking.iterrows():
            if source['AUFPACKEN_JA_NEIN'] and source['Pal_ID'] != target['Pal_ID']:
                maximale_teile = int(target['verbleibende_Höhe'] / source['Teilhöhe'])
                stapelbare_teile = min(source['Teilbar_durch'], maximale_teile)
                if stapelbare_teile > 0:
                    neue_höhe = target['height_PAL'] + stapelbare_teile * source['Teilhöhe']
                    stapel_details.append({
                        'Quell_Pal_ID': source['Pal_ID'],
                        'Ziel_Pal_ID': target['Pal_ID'],
                        'Anzahl_Teile': stapelbare_teile,
                        'Teilhöhe': source['Teilhöhe'],
                        'Ausgangshöhe': target['height_PAL'],
                        'Neue_Höhe': neue_höhe
                    })
                    # Update der Höhen in den DataFrames
                    df_stacking.at[index, 'height_PAL'] = neue_höhe
                    df_stacking.at[index, 'verbleibende_Höhe'] = max_height - neue_höhe
                    df_stacking.at[idx, 'Teilbar_durch'] -= stapelbare_teile

                    if df_stacking.at[idx, 'Teilbar_durch'] <= 0:
                        df_stacking.drop(idx, inplace=True)
                    break  # Breche die innere Schleife ab, wenn wir gestapelt haben
        unverbrauchte_paletten = df_stacking[df_stacking['Teilbar_durch'] > 0]

        stapel_details, unverbrauchte_paletten[['Pal_ID', 'Teilbar_durch', 'height_PAL']]
    return stapel_details, unverbrauchte_paletten


def page():
# for 1 (index=5) from the standard loader group

    df = fuege_Stammdaten_zu_LT22()
    st.dataframe(df,height=200, use_container_width=True)
    # filtr by 'Queue' == 'GITPD'
    dfGITPD = df[df['Queue'] == 'GITPD']
    anzahl_palten = dfGITPD['Pal_ID'].count()
    st.write(f'Anzahl Paletten: {anzahl_palten}')
    # create df with Pal_ID, Teilbar_durch, Teilhöhe, height_PAL
    dfPal = dfGITPD[['Pal_ID', 'Teilbar_durch', 'Teilhöhe', 'height_PAL', 'AUFPACKEN_JA_NEIN', 'GEEIGNET_UNTERBAU']]
    
    # Berechne die Stapelung
    stapel_details, unverbrauchte_paletten = berechne_stapeln(dfPal)
    st.write('unverbrauchte_paletten')
    st.write(unverbrauchte_paletten)
    st.write('stapel_details')
    st.write(stapel_details)
    
    

    
