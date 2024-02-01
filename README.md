| :bowtie: `:bowtie:` | :smile: `:smile:` | :laughing: `:laughing:` |
### MD EDIT <https://www.heise.de/mac-and-i/downloads/65/1/1/6/7/1/0/3/Markdown-CheatSheet-Deutsch.pdf>
# Kurzbeschreibung
Auswertung und grafische Darstellung der Logistikprozesse am Standort sowie die Möglichkeit der Datenerfassung (z.B. Fehlverladungen)
# ToDo 

Paletten anzeigen ('')

pipreqs "/Users/martinwolf/Python/PAMS 2.0"
Successfully saved requirements file in   /Users/martinwolf/Python/PAMS 2.0/requirements.txt

ll

Check if SKU in DFOrder if not stWarning Stammdaten 

LS 3202491346

## Code 
        Python 3.10.7
## Notwendige Module
        
pip install openpyxl  
pip install extract-msg (Mails auslesen und anzeigen) #
pip install eml-parser (Mails auslesen und anzeigen) #
pip install streamlit <https://docs.streamlit.io/library/api-reference>  
pip install streamlit-option-menu (für main menu)  
pip install pyodbc (für Datenbankverbindung)
pip install streamlit-authenticator==0.1.5 (für Login)  
pip install pandas <https://pandas.pydata.org/docs/reference/index.html#api>  
pip install numpy <https://numpy.org/install/>  
pip install pickle <https://docs.python.org/3/library/pickle.html>  
pip install pyarrow
pip install fastparquet (Datenkompression)
# Funktionen:
Notwendig zum Release: 
## Home:  
    Live Tagesübersicht  
## Mitarbeiter:  
    Durchschnitt über alle Mitarbeiter  :white_check_mark:  
    Auswertung Mitarbeiter Picks am Tag mit Zeitachse   :white_check_mark:
    Heatmap der Lagerbereiche  :white_check_mark:
    Heatmap der SKU Zugriffe  :white_check_mark:
## Auftragsübersicht / DDS :  
    Lieferschein Volumen pro Kunde  
    Übertagungszeitraum vs. Volumen  
    Anteile der Zugriffe pro LS  
## Einstellungen
    Dataframe User bearbeiten :smile:
    lt22 hochladen und brechen :smile: 
## Vorstellbare Funktionen:  
    Kunden Forecast in Picks (Stichwort Python ARIMA-MODELL)  
    Datenerfassung Fehlverladung  
    Auswertung Fehlverladung  
    Datenerfassung Arbeitsanweisungen  
    Reminder Funktion für AA und Schulungsnachweisen  
## Benötigte Daten:  
    Excel User übersicht OneID Name Funktion  
    LT22 aus SAP Layout spezifikationen noch ablegen 
    VL06o Liste aller Bestellungen mit Inhalt   
    Datenbank abfrage von EDV über erstellte Label  
    Datenbankabfrage Stammdaten  

## Pip requirements.txt
pip install pipreqs
pipreqs /path/to/project


# FAQ LINKS

streamlit to exe <https://discuss.streamlit.io/t/streamlit-deployment-as-an-executable-file-exe-for-windows-macos-and-android/6812?page=2>
streamlit to exe <https://discuss.streamlit.io/t/streamlit-wasm-electron-desktop-app/31655>
