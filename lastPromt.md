Hi wir müssen an der Lagerbestands-Übersicht arbeiten das öffnen der Page ist sehr langsam, das Daten Vorbereiten dauert scheinbar, können wir daran noch Optimieren? Und ich brauche in jedem Bereich ein Popup unter dem Historischen Diagram in welchem ich mir den gefilterten (Tag und Fachbereich) Bestand ansehen kann. 

Dann müssen aber auch die Filter noch angepasst werden auf folgende Logiken 

Grundsätzlich bildet die Spalte CreationTimestamp den Tag des Bestandreports ab. 

DIET 

Anzeigen in Karton 
StockInventoryGermany Filtern auf 

Fachbereich = DIET
Lagerzone = Blocklager 
Summe aus MengeVerkaufseinheit

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = DIET
Lagerzone = Blocklager 
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone

Leaf 

Anzeigen in Karton 
StockInventoryGermany Filtern auf 

Fachbereich = Leaf
Lagerzone = Blocklager 
Summe aus MengeVerkaufseinheit

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = Leaf
Lagerzone = Blocklager 
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone

C&F 

Anzeigen in Paletten 
StockInventoryGermany Filtern auf 

Fachbereich = C&F
Lagerzone = Regallager 
Anzahl Spalten Zählen 

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = C&F
Lagerzone = Regallager 
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone

EXPORT

Anzeigen in Paletten 
StockInventoryGermany Filtern auf 

Fachbereich = Finished Goods Export
Lagerzone = Hochregallager und  Regallager und Blocklager 
Anzahl Spalten Zählen 

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = Finished Goods Export
Lagerzone = Hochregallager und  Regallager und Blocklager 
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone


DOMESTIC


Anzeigen in Paletten 
StockInventoryGermany Filtern auf 

Fachbereich = Domestic Deutschland
Lagerzone = Blocklager und Regallager
StandortGeografisch = Bayreuth
Anzahl Spalten Zählen 

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = Domestic Deutschland
StandortGeografisch = Bayreuth
Lagerzone = Blocklager und Regallager
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone

Für die Kühne und Nagel Läger gilt 

Anzeigen in Paletten 
StockInventoryGermany Filtern auf 

Fachbereich = Domestic Deutschland
Lagerzone = Paletten Zone
StandortGeografisch = das jeweilige DEPOT Main, Hamburg, München, Duisburg oder Berlin
Anzahl Spalten Zählen 

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

Fachbereich = Domestic Deutschland
Lagerzone = Paletten Zone
StandortGeografisch = das jeweilige DEPOT Main, Hamburg, München, Duisburg oder Berlin
Duplicate aus Lagerzone entfernen 
Summe aus MaxKapazitaetLagerzone



Hi schau mal die Map passt noch nicht die Koordinaten scheinen Verzogen zu sein? 

Bitte sehe dir das Bild an und wir haben nur diese ausliefernden Depots wird müssen das zusammenfassen in der Übersicht das Passiert aktuell nicht denke ich 
DEPOT_NAME_MAPPING = {
    "BE5": "Bielefeld",
    "BF5": "Bielefeld",
    "ECH": "DE52 - München",
    "GNM": "DE53 - Berlin",
    "GRE": "Bielefeld",
    "HA5": "DE55 - Hannover",
    "HH5": "DE54 - Hamburg",
    "HRO": "DE54 - Hamburg",
    "KIE": "DE54 - Hamburg",
    "LE5": "DE57 - Schkeuditz",
    "MA5": "Mainz",
    "MU5": "DE52 - München",
    "NU5": "DE52 - München",
    "PTD": "DE53 - Berlin",
    "Rheine": "DE56 - Duisburg",
    "ROW": "DE54 - Hamburg",
    "ST5": "DE59 - Gärtringen",
    "STB": "DE52 - München",
    "STW": "DE52 - München"
}
