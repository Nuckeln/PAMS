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
user
Test
klarname
Testo
Passwort
Testrer


✦ Um Microsoft SSO (Single Sign-On) in Ihrer Streamlit-App zu implementieren, müssen wir die bestehende Authentifizierung (wahrscheinlich streamlit-authenticator) durch einen OAUTH2-Flow mit der Microsoft Identity Platform (Azure AD / Entra ID) ersetzen.

  Hier ist der Fahrplan, was zu tun ist:

  1. Vorbereitungen im Azure Portal (Azure Entra ID)
  Bevor wir Code schreiben, muss die App bei Microsoft "bekannt" gemacht werden:
   1. App Registration erstellen: In Azure Entra ID eine neue Registrierung anlegen.
   2. Redirect URI setzen: Wichtig! Sie müssen definieren, wohin Microsoft den User nach dem Login zurückschickt.
       * Lokal: http://localhost:8501
       * Produktion: https://ihre-app-url.com
   3. Secrets generieren: Einen "Client Secret" erstellen.
   4. IDs notieren: Wir brauchen drei Werte:
       * Application (client) ID
       * Directory (tenant) ID
       * Client Secret

  2. Python Umgebung & Dependencies
  Wir benötigen eine Bibliothek, die das Authentifizierungsprotokoll übernimmt. Der Standard ist die offizielle Microsoft-Bibliothek:
   * `msal` (Microsoft Authentication Library for Python) installieren.
   * Alternativ kann man Wrapper nutzen, aber msal ist am stabilsten.

  3. Konfiguration
  Die IDs und Secrets dürfen nicht hardcodiert werden. Wir müssen sie in .streamlit/secrets.toml (lokal) und in den Azure App Service Environment Variables (Produktion) hinterlegen.

  4. Anpassung der Logik in Main.py
  Der Ablauf im Code wird sich wie folgt ändern:

   1. Start: App prüft st.session_state, ob ein Token vorhanden ist.
   2. Kein Token:
       * App generiert eine Login-URL via msal.
       * Zeigt einen "Mit Microsoft anmelden"-Link/Button an.
   3. Callback (Der knifflige Teil in Streamlit):
       * Der User kommt von Microsoft zurück (die Seite lädt neu).
       * Wir müssen st.query_params auslesen, um den code zu finden, den Microsoft mitschickt.
       * Diesen code tauschen wir im Hintergrund gegen einen Access Token und die User-Infos (E-Mail, Name) ein.
   4. Erfolg:
       * Token und User-Infos werden in st.session_state gespeichert.
       * Die URL-Parameter werden bereinigt (st.experimental_set_query_params oder ähnlich), damit der Code nicht in der Adresszeile bleibt.
       * Die App zeigt den geschützten Inhalt.

  Soll ich starten?
  Wenn Sie Zugriff auf das Azure Portal haben, wäre der erste Schritt, die App Registration durchzuführen und mir die Tenant ID und Client ID (keine Secrets hier posten!) zu geben oder diese lokal in Ihre secrets.toml einzutragen.

  Soll ich Ihnen erst einmal eine Vorlage für die secrets.toml erstellen und das Paket msal installieren?

> also hätte wir weiter eine UserTablle in welcher die Rechte liegen?

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  ReadFile Data/.../berechtigungen_user.csv                                                                                                                                                                                                                                                                                                                                                         │
│                                                                                                                                                                                                                                                                                                                                                                                                      │
│                                                                                                                                                                                                                                                                                                                                                                                                      │
│ ✓  ReadFile Main.py                                                                                                                                                                                                                                                                                                                                                                                  │
│                                                                                                                                                                                                                                                                                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  ReadFile Data_Class/MMSQL_connection.py                                                                                                                                                                                                                                                                                                                                                           │
│                                                                                                                                                                                                                                                                                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ Ja, genau. Die User-Tabelle bleibt bestehen und ist essenziell.

  Der Unterschied liegt in der Aufgabenteilung:

   1. Microsoft (SSO): Übernimmt die Authentifizierung ("Wer ist das?").
       * Microsoft bestätigt: "Dieser Benutzer ist wirklich martin.wolf@bat.com und hat sich erfolgreich angemeldet."
   2. Ihre User-Tabelle: Übernimmt die Autorisierung ("Was darf der?").
       * Ihre App nimmt die E-Mail von Microsoft, schaut in der User-Tabelle nach und sieht: "Ah, martin.wolf@bat.com hat Rechte-Level 4 (Admin)."

  Was sich ändert:
   * Das Passwort wird nicht mehr in Ihrer Datenbank benötigt (bzw. ignoriert).
   * Der Login-Prozess prüft nicht mehr "Benutzername + Passwort" gegen Ihre Datenbank, sondern prüft, ob die E-Mail von Microsoft in Ihrer Datenbank existiert.

  Nächste Schritte:
  Bevor wir den Code anfassen, benötigen Sie:
   1. Eine App Registration in Azure Entra ID (ich kann Ihnen sagen, welche Einstellungen dort nötig sind).
   2. Die Bibliothek `msal` muss installiert werden (pip install msal), um mit Microsoft zu kommunizieren.

  Soll ich Ihnen die Einstellungen für das Azure Portal auflisten?

> Ja bitte liste auf

✦ Hier sind die Schritte und Einstellungen, die Sie im Azure Portal vornehmen müssen:

  1. Eine neue "App Registration" erstellen
   1. Gehen Sie zu portal.azure.com (https://portal.azure.com).
   2. Suchen Sie nach "Microsoft Entra ID" (früher Azure Active Directory).
   3. Wählen Sie links "App registrations" und klicken Sie oben auf "+ New registration".
   4. Name: z.B. PAMS-Streamlit-SSO
   5. Supported account types: Wählen Sie "Accounts in this organizational directory only" (Single Tenant), da dies eine interne Firmen-App ist.
   6. Redirect URI: Wählen Sie im Dropdown "Web" und geben Sie vorerst http://localhost:8501 ein (für die lokale Entwicklung). Später fügen wir hier die Produktions-URL hinzu.
   7. Klicken Sie auf "Register".

  2. Authentication (Wichtig für den Rückweg)
   1. Klicken Sie links im Menü auf "Authentication".
   2. Stellen Sie sicher, dass unter "Web" Ihre Redirect URIs korrekt sind.
   3. Scrollen Sie zu "Implicit grant and hybrid flows": Diese sollten deaktiviert bleiben (wir nutzen den sichereren "Authorization Code Flow").
   4. Speichern Sie, falls Sie Änderungen vorgenommen haben.

  3. Certificates & Secrets (Das "Passwort" für Ihre App)
   1. Klicken Sie links auf "Certificates & secrets".
   2. Klicken Sie auf "+ New client secret".
   3. Beschreibung: Streamlit Secret | Ablauf: 180 Tage (oder nach Firmenvorgabe).
   4. WICHTIG: Kopieren Sie den Value (Wert) des Secrets sofort. Er wird nur dieses eine Mal angezeigt. (Nicht die Secret ID kopieren!).

  4. API Permissions (Rechte abfragen)
   1. Klicken Sie auf "API permissions".
   2. Standardmäßig ist meist User.Read (Delegated) bereits eingetragen. Das reicht aus, um Name und E-Mail des Benutzers zu erhalten.
   3. Klicken Sie ggf. auf "Grant admin consent for [Ihr Firmenname]", damit Benutzer nicht einzeln bestätigen müssen (falls Sie die Berechtigung dazu haben).

  ---

  Diese Werte müssen Sie notieren:
  Diese drei Werte benötigen wir für die Konfiguration:
   * Application (client) ID: (Zu finden auf der "Overview"-Seite)
   * Directory (tenant) ID: (Zu finden auf der "Overview"-Seite)
   * Client Secret Value: (Den Wert, den Sie gerade in Schritt 3 kopiert haben)

  Ausblick: So sieht die Speicherung aus
  In Ihrer .streamlit/secrets.toml Datei werden wir das später so anlegen:

   1 [microsoft_auth]
   2 client_id = "IHRE_CLIENT_ID"
   3 tenant_id = "IHRE_TENANT_ID"
   4 client_secret = "IHR_SECRET_VALUE"
   5 redirect_uri = "http://localhost:8501"

  Sobald Sie die App registriert haben und bereit sind, installieren wir msal und passen die Main.py an. Geben Sie einfach Bescheid!

 1 open file (ctrl+g to view) | 1 GEMINI.md file                                                                                               