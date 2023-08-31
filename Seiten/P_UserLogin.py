import streamlit as st
import streamlit_authenticator as stauth
# from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
# from Data_Class.SQL_Neu import updateTable
from Data_Class.sql import read_table, updateTable

class Login:
    def __init__(self):
        self.usernames = []
        self.names = []
        self.passwords = []
        self.funktionen = []
        self.rechte = []

        self.credentials = {}
        self.authenticator = None
        st.session_state = None


    def Login(self):
        # Initialize the 'rechte' attribute of session_state.


        df = read_table('user')
        self.usernames = df['username'].tolist()
        self.names = df['name'].tolist()
        self.passwords = df['password'].tolist()
        self.funktionen = df['function'].tolist()
        self.rechte = df['rechte'].tolist()
        self.credentials = {"usernames":{}}

        # Extract the values from the DataFrame and add them to the 'credentials' dictionary.
        for uname,name,pwd,funktion,rechte in zip(self.usernames,self.names,self.passwords,self.funktionen,self.rechte):
            user_dict = {"name": name, "password": pwd, "function": funktion, "rechte": rechte}
            self.credentials["usernames"].update({uname: user_dict})

        self.authenticator = stauth.Authenticate(self.credentials, "cokkie_name", "random_key",
                                            cookie_expiry_days=30)
        name, authentication_status, usernames= self.authenticator.login("Login", 'main')
        if authentication_status == True:
            st.session_state.user = name
            st.session_state.rechte = df.loc[df['name'] == name, 'rechte'].iloc[0]
        if authentication_status == False:
            st.error("Login fehlgeschlagen!")

        return authentication_status
    
    def Logout(self):
    
        self.authenticator.logout('Logout', 'main')
        if st.session_state.user is None:
            st.success("Logout successful!", key='logout_success')
            # clear cookies
            #reload page
            st.experimental_rerun()

    def newPasswort(self):
        with st.expander("Passwort ändern",expanded=False):
            df = read_table('user')
            self.usernames = df['username'].tolist()
            self.names = df['name'].tolist()
            self.passwords = df['password'].tolist()
            self.funktionen = df['function'].tolist()
            self.rechte = df['rechte'].tolist()
            self.credentials = {"usernames":{}}

            st.write('du Bist eingeloggt als: ', st.session_state.user)
            st.write('dein Username ist: ', df.loc[df['name'] == st.session_state.user, 'username'].iloc[0])
            # st.write('deine Rechte sind: ', st.session_state.rechte)
            # st.write('deine Funktion ist: ', df.loc[df['name'] == st.session_state.user, 'function'].iloc[0])

            neupassword = st.text_input("neues password:",key='neus_password_anlegen')
        
            X = st.button("Speichere neues Passwort",key='speichere_neues_passwort')
            if X:
                pw = stauth.Hasher(neupassword)._hash(neupassword)
                # replace password in df with new password
                df.loc[df['name'] == st.session_state.user, 'password'] = pw
                # update table with new password
                
                updateTable(df,'user')
                st.success("Passwort erfolgreich geändert! Bitte Logge dich aus")
    def newPasswort_Admin(self):
        with st.expander("Passwort ändern",expanded=False):
            df = read_table('user')
            self.usernames = df['username'].tolist()
            self.names = df['name'].tolist()
            self.passwords = df['password'].tolist()
            self.funktionen = df['function'].tolist()
            self.rechte = df['rechte'].tolist()
            self.credentials = {"usernames":{}}

            sel_user = st.selectbox('Wähle User aus', self.names)

            neupassword = st.text_input("password",key='neus_password_anlegen')
        
            X = st.button("Speichere neues Passwort",key='speichere_neues_passwort')
            if X:
                pw = stauth.Hasher(neupassword)._hash(neupassword)
                # replace password in df with new password
                df.loc[df['name'] == sel_user, 'password'] = pw
                # update table with new password
                
                updateTable(df,'user')
                st.success("Passwort erfolgreich geändert! Bitte Logge dich aus")                
                # clear cookies




        
