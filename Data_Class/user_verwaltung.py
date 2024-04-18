import streamlit as st
import bcrypt
import pandas as pd
from Data_Class.SQL import save_table_to_SQL, read_table

def create_DB_table():
    tablename = "PAMS_users"
    #erstelle ein Dataframe mit den Spalten User, PW, Rechte, Funktion
    df = pd.DataFrame(columns=["User", "PW", "Rechte", "Funktion"])
    #erstelle User Admin
    hashed_pw = hash_password("Hannah24-")
    user_data = {"User": "admin", "PW": hashed_pw, "Rechte": 3, "Funktion": "admin"}
    df = pd.concat([df, pd.DataFrame([user_data])])
    #speichere das Dataframe in der SQL Datenbank
    save_table_to_SQL(df, tablename)


def hash_password(password):
    # Hashen des Passworts mit bcrypt, inklusive Salt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def register_user(username, password, rights=0, function="none"):
    hashed_pw = hash_password(password)
    user_data = {"User": username, "PW": hashed_pw, "Rechte": rights, "Funktion": function}
    df = pd.DataFrame([user_data])
    save_table_to_SQL(df, "PAMS_users")

def check_credentials(username, password):
    users_df = read_table("PAMS_users")
    if isinstance(users_df, pd.DataFrame):
        users = users_df.to_dict('records')
    else:
        return False  # Oder handle den Fehler entsprechend

    for user in users:
        if user["User"] == username and bcrypt.checkpw(password.encode(), user["PW"].encode()):
            return True
    return False

def st_page_login():
    st.title("Login und Registrierung")
    users_df = read_table("PAMS_users")

    # Überprüfen, ob users_df tatsächlich ein DataFrame ist und dann in eine Liste von Dictionaries umwandeln
    if isinstance(users_df, pd.DataFrame):
        users = users_df.to_dict('records')
    else:
        st.error("Fehler beim Laden der Benutzerdaten.")
        st.stop()

    if st.button("DB Tabelle erstellen"):
        create_DB_table()

    with st.form("Login"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        login_submit = st.form_submit_button("Login")

    if login_submit:
        user_found = next((user for user in users if user['User'] == username), None)
        if user_found and bcrypt.checkpw(password.encode(), user_found['PW'].encode()):
            st.success("Erfolgreich eingeloggt")
            st.rerun()
        else:
            st.error("Falsche Anmeldedaten")

    with st.form("Register"):
        new_username = st.text_input("Neuer Benutzername", key="new_user")
        new_password = st.text_input("Neues Passwort", type="password", key="new_pass")
        register_submit = st.form_submit_button("Neuen User registrieren")

    if register_submit:
        # Überprüfen, ob der Benutzername bereits existiert
        existing_user = next((user for user in users if user['User'] == new_username), None)
        if not existing_user:
            register_user(new_username, new_password)
            st.success("Benutzer erfolgreich registriert")
        else:
            st.error("Benutzername bereits vergeben")
