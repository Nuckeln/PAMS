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
Duplicate aus Sensor_ID entfernen 
Summe aus MaxKapazitaetLagerzone

LEAF 

Anzeigen in Karton 
StockInventoryGermany Filtern auf 

Fachbereich = LEAF
Lagerzone = Blocklager 
Summe aus MengeVerkaufseinheit

Maximalwert für die Berechnung der Lagerauslastung
StockConfigGermany Filtern auf 

StockConfigGermany = LEAF
Lagerzone = Blocklager 
Duplicate aus Sensor_ID entfernen 
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
Duplicate aus Sensor_ID entfernen 
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
Duplicate aus Sensor_ID entfernen 
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
Duplicate aus Sensor_ID entfernen 
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
Duplicate aus Sensor_ID entfernen 
Summe aus MaxKapazitaetLagerzone




