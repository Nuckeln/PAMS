import streamlit as st
import streamlit_authenticator as stauth #pip install streamlit-authenticator==0.1.5 
import pickle 
from pathlib import Path

# streamlit run "/Users/martinwolf/Documents/VS Code/SD-Auswertung/Neue Funktionen/Login/login.py"
# DOKU https://github.com/mkhorasani/Streamlit-Authenticator
class Login:

    def Login(self):
# ----- Login -----
        names =  ["Martin", "admin", "Norbert"]
        usernames = ["martin", "admin", "norbert"]
        file_path = Path(__file__).parent / "passwords.pk1"
        with file_path.open("rb") as file:
            hasched_passwords = pickle.load(file)

        authenticator = stauth.Authenticate(names,usernames,hasched_passwords,
        "cookienameSuperdepot","abcdef",cookie_expiry_days=2)

        name, authentication_status, usernames= authenticator.login("Login", 'main')

        if authentication_status == False:
            st.error("Login fehlgeschlagen")
        if authentication_status == None:
            st.info("Bitte loggen Sie sich ein")
        if authentication_status == True:
            #erfolgreich geladen dann Code ausführen!
            return authentication_status
    