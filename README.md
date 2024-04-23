#Dokumentation: PAMS Report-Tool
1. Einführung
Das PAMS Report-Tool ist eine webbasierte Anwendung, entwickelt mit Streamlit, zur Überwachung, Verwaltung und Berichterstattung von Depotaktivitäten. Es bietet verschiedene Benutzerzugriffsstufen, um den unterschiedlichen Anforderungen von Administratoren, Managern und anderen Mitarbeitern gerecht zu werden.

2. Hauptfunktionen
Depot Live Status: Zeigt den aktuellen Status und Live-Informationen des Depots.
LC Monitor: Überwacht und steuert die Ladekapazitäten.
Depot Reports: Erzeugt Berichte über Depotaktivitäten.
Forecast: Prognostiziert zukünftige Depotanforderungen und -kapazitäten.
Lagerverwaltung: Verwaltet den Lagerbestand und die Lagerplatzverteilung.
Admin: Spezielle administrative Funktionen für die Depotverwaltung.
3. Module und Technologien
Streamlit: Das Herzstück der Anwendung, ermöglicht schnelle Entwicklungen von Web-Apps.
Streamlit Navigation Bar: Wird verwendet, um eine benutzerfreundliche Navigationsleiste zu integrieren.
Streamlit Authenticator: Verwaltet die Benutzerauthentifizierung und Sicherheit.
Pandas: Dient der Datenmanipulation und -analyse.
Bcrypt: Bietet Sicherheitsfunktionen, insbesondere das Hashing von Passwörtern.
4. Sicherheitsmaßnahmen
Benutzerauthentifizierung: Nutzt streamlit_authenticator für eine sichere Anmeldung und Sitzungsverwaltung.
Passwort-Hashing: Verwendet bcrypt für sicheres Speichern der Passwörter.
Versteckte Streamlit-Komponenten: Durch CSS-Modifikationen werden unnötige oder sensible UI-Elemente versteckt.
5. Benutzerverwaltung
Zugriffsrechte: Unterschiedliche Zugriffsrechte (von Admin bis Gast), die den Benutzern verschiedene Funktionen und Sichtbarkeiten gewähren.
Benutzerregistrierung: Ein Registrierungsprozess ermöglicht es neuen Benutzern, Konten zu erstellen, die dann von Admins freigeschaltet werden müssen.
6. Installation und Start
Abhängigkeiten installieren:
bash
Copy code
pip install streamlit streamlit_authenticator pandas bcrypt
Anwendung starten:
bash
Copy code
streamlit run main.py
7. Zukünftige Verbesserungen
Integration einer Zwei-Faktor-Authentifizierung für erhöhte Sicherheit.
Weiterentwicklung der Berichtsgenerierungsfunktionen für detailliertere Analysen.
Verbesserung der Benutzeroberfläche für eine noch intuitivere Benutzererfahrung.

# BAT FARBEN:

#0e2b63 darkBlue
#004f9f MidBlue
#00b1eb LightBlue
#ef7d00 Orange
#ffbb00 Yellow
#ffaf47 Green
#afca0b lightGreen
#5a328a Purple
#e72582 Pink


