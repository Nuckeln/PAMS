# Kurzbeschreibung
Auswertung und grafische Darstellung der Logistikprozesse am Standort sowie die Möglichkeit der Datenerfassung (z.B. Fehlverladungen)
 
## Notwendige Module
Module:
        Streamlit 
        Pandas 
        Numpy 
        pyodbc (SQL) 

## Installation
        pip install streamlit-option-menu
        pip install openpyxl

## Zu Implementierende Funktionen:
Notwendig zum Release: 
Das aktuelle Wetter in der Sidebar! (Einfach nur zum Lernen API) 
Hey, kommt man eventuell an Live Temp aus dem Depot? 
Home: 
    Live Tagesübersicht 
Mitarbeiter: 
    Durchschnitt über alle Mitarbeiter 
    Auswertung Mitarbeiter Picks am Tag mit Zeitachse 
    Auswertung Wochenleistung 
Auftragsübersicht / DDS : 
    Lieferschein Volumen pro Kunde 
    Übertagungszeitraum vs. Volumen 
    Anteile der Zugriffe pro LS 
Artikelübersichten (ABC Analyse): 
    Heatmap der Lagerbereiche 
    Heatmap der SKU Zugriffe 
Vorstellbare Funktionen: 
    Kunden Forecast in Picks (Stichwort Python ARIMA-MODELL) 
    Datenerfassung Fehlverladung 
    Auswertung Fehlverladung 
    Datenerfassung Arbeitsanweisungen 
    Reminder Funktion für AA und Schulungsnachweisen 

Codebasis: 
        Python 3.10.7
Module:
        Streamlit
        Pandas
        Numpy
        pyodbc (SQL)

        pip install streamlit-option-menu
        pip install openpyxl
        
Benötigte Daten: 
    Excel User übersicht OneID Name Funktion 
    LT22 aus SAP Layout spezifikationen noch ablegen
    VL06o Liste aller Bestellungen mit Inhalt 
        Kann eventuell ersetzt werden aus den vorhandenen IDOCS? M.KOLB 
    Datenbank abfrage von EDV über erstellte Label
    Datenbankabfrage Stammdaten

Beschreibung Live Tagesübersicht:

Oben: 
Überschrift
Aktuelles Auftragsvolumen Pick Tag heute und morgen Anzeigen in getrennten Kreisdiagrammen
Aufteilung nach Depots, inkl. Deadline 
    Stichwort Progressbar statt Kreisdiagramme? 
in Colums aufteilen Durchschnittliche Pickleistung der letzten Tage, benötigte Pick Leistung bis Deadline, 
fertig voraussichtlich  bis.

Auftragsvolumen gesamt auf Zeitachse nach Verfügbarkeit (Erstellung LS + XX Zeit)
Aufteilung nach Kunden (Balkendiagramm)

Gedankliche Umsetzung: 
Autorefresh 
Laden der Systemzeit in eine Variable
Laden des benötigten Dataframes
Filtern des df nach Systemzeit + morgen

Seitenaufbau 
Headline
Columns 2 
Col1 Offen, Fertig
Col2  Tagespicks im Schnitt, Zielzeit
Anlegen st.bar (Auftragsvol) / Unterscheidung Depot 
Columns 2
col1 st.Bar Aufteilung nach Kunden
col2 st.Bar Aufteilung nach Zeitachse Ls Verfügbarkeit

Deploy: https://discuss.streamlit.io/t/streamlit-deployment-as-an-executable-file-exe-for-windows-macos-and-android/6812?page=2
https://discuss.streamlit.io/t/streamlit-wasm-electron-desktop-app/31655
