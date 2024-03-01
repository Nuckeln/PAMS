
import streamlit as st 
import pandas as pd
import numpy as np
import datetime






# Filename

sel_Name = 'CC-BROMWE-en'

# Suche in allen Ordnern hier /Users/martinwolf/Library/CloudStorage/OneDrive-FreigegebeneBibliotheken–BAT eine Datei die ein Teil des Namens enthält
# und gib mir den Pfad zurück
def find_files(sel_Name):
    import os
    matching_files = []
    for root, dirs, files in os.walk('/Users/martinwolf/Library/CloudStorage/OneDrive-FreigegebeneBibliotheken–BAT'):
        for file in files:
            if sel_Name in file:
                matching_files.append(os.path.join(root, file))
    return matching_files

matching_files = find_files(sel_Name)
start_cal_Time = datetime.datetime.now()
print(start_cal_Time)
for file in matching_files:
    resolut_Time = datetime.datetime.now() - start_cal_Time
    print(resolut_Time)
    print(file)
resolut_Time = datetime.datetime.now() - start_cal_Time
print(resolut_Time)