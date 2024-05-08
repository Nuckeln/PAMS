ST.Columns

Erstellt für jede Zahl eine Spalte und die Breite jeder Spalte ist proportional zur angegebenen Zahl. Zahlen können Ints oder Floats sein, sie müssen jedoch positiv sein.
Beispielsweise erstellt st.beta_columns([3, 1, 2]) drei Spalten, wobei die erste Spalte dreimal so breit wie die zweite und die letzte Spalte doppelt so breit ist.


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

/Library/Python_local/Devin


export OPENAI_API_KEY="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"
export WORKSPACE_DIR="/Library/Python_local/Devin/OpenDevin/"
python -m pip install -r requirements.txt
uvicorn opendevin.server.listen:app --port 3000


[12:37] Michael Kolb
ftps://waws-prod-db3-259.ftp.azurewebsites.windows.net/site/wwwroot

WA-PP-NE-CMES-REPORTING-SUPERDEPOTUI-prod\$WA-PP-NE-CMES-REPORTING-SUPERDEPOTUI-prod

YJgBiL9xf10SlhFmvEYjMcEPunwEkAWHQrNefzenhycvm9kLoQkAn1ZLvzev



Wir haben ein Datenframe mit Paletten welche in der Höhe teilbar sind. ich möchte diese Paletten nun solange auf andere stapeln bis keine mehr zum Teilen übrig sind.
Es gibt aber auch bedingungen 
Wir wollen so wenig stapelvorgänge wie möglich durchführen hierzu nehmen wir erstmal die GEEIGNET_UNTERBAU = True um diese im ganzen zu verwenden dann teilen wir die AUFPACKEN_JA_NEIN = True und stapeln soviele Teile wie möglich mit einmal auf die Pal_ID bis diese die Max Höhe von 270 cm erreicht hat. Wenn die Pal_ID welche wir zum stapeln verwendet haben verbraucht ist nehmen wir die nächte bis entweder keine GEEIGNET_UNTERBAU = True mehr vorhanden sind dann bis AUFPACKEN_JA_NEIN = True vorhanden sind dann versuche noch die bisher nicht verwendetetn GEEIGNET_UNTERBAU aufzuteilen bis wir eine Optimierte Anzahl an Paletten übrig haben. 
Die Bisherige Palettenhöhe muss beachtet werden. 

Pal_ID: Die ID der Palette.
Teilbar_durch: Anzahl Teile Pro Palette
Teilhöhe: Die Höhe eines Abschnitts der Palette.
height_PAL: Die bisherige Gesamthöhe der Palette.
AUFPACKEN_JA_NEIN: Ob die Palette aufgepackt werden kann (Wahrheitswert).
GEEIGNET_UNTERBAU: Ob die Palette als Unterbau geeignet ist (Wahrheitswert).


User muss doch genau wissen wieviele Teile er von Pal_ID "A" auf Pal_ID "B" er staplen muss und welche Pal_ID am Schluss verbraucht worden ist sowie die höhe der Teile welche er aufstapelt und die am schluss erreichte höhe der Palette. 

Hier ein Beispiel aus den Daten so sollte die Ausgabe aussehen

PAL_ID 

16220638-6cf8-4279-a6a8-31b3c15b6c2b aufteilen in 8 Teile 
    je 2 Teile (Höhe der teile) auf Pal_ID XXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    je 1 Teil  (Höhe der teile) auf Pal_ID XXXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    je x Teile (Höhe der teile) auf Pal_ID XXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    '' usw.

16220638-6cf8-4279-dsff-31b3c15b6c2b aufteilen in 6 Teile 
    je 2 Teile (Höhe der teile) auf Pal_ID XXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    je 1 Teil (Höhe der teile) auf Pal_ID XXXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    je x Teile (Höhe der teile) auf Pal_ID XXXX Ausgangshöhe = 189,23 neue Höhe = XXX 
    '' usw.

Folgende PAL_ID werden nicht verwendet und bleiben unversehrt

16220638-6cf8-4279-dsff-31b3c15b6c2b 