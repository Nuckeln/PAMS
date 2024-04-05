import streamlit as st
import streamlit_authenticator as stauth
from Data_Class.SQL import read_table, updateTable
      

class Login:
    

    def __init__(self):
        self.usernames = []
        self.names = []
        self.passwords = []
        self.funktionen = []
        self.rechte = []
        self.credentials = {}
        self.authenticator = None

    def Login(self):

        df = read_table('user')
        self.usernames = df['username'].tolist()
        self.user = ''
        self.names = df['name'].tolist()
        self.passwords = df['password'].tolist()
        self.funktionen = df['function'].tolist()
        self.rechte = df['rechte'].tolist()
        self.credentials = {"usernames":{}}
        self.authentication_status = self

        # Extract the values from the DataFrame and add them to the 'credentials' dictionary.
        for uname,name,pwd,funktion,rechte in zip(self.usernames,self.names,self.passwords,self.funktionen,self.rechte):
            user_dict = {"name": name, "password": pwd, "function": funktion, "rechte": rechte}
            self.credentials["usernames"].update({uname: user_dict})

        self.authenticator = stauth.Authenticate(self.credentials, "PamsReportingTool", "random_key",
                                            cookie_expiry_days=30)
        name, authentication_status, usernames= self.authenticator.login(location='main',max_concurrent_users=20,max_login_attempts=10,clear_on_submit=True)
        if authentication_status == True:
            st.session_state.user = name
            st.session_state.rechte = df.loc[df['name'] == name, 'rechte'].iloc[0]
            return authentication_status, st.session_state.user, st.session_state.rechte
        if authentication_status == False:
            return authentication_status, st.session_state.user, st.session_state.rechte
    def Logout(self):
        self.authenticator.logout('Logout', 'main')
        if self.user is None:
            st.success("Logout successful!", key='logout_success')
            self.authentication_status = False
            st.rerun()
    def newPasswort(self):

        df = read_table('user')
        self.usernames = df['username'].tolist()
        self.names = df['name'].tolist()
        self.passwords = df['password'].tolist()
        self.funktionen = df['function'].tolist()
        self.rechte = df['rechte'].tolist()
        self.credentials = {"usernames":{}}

        neupassword = st.text_input("neues password:",key='neus_password_anlegen')
    
        X = st.button("Speichere neues Passwort",key='speichere_neues_passwort')
        if X:
            pw = stauth.Hasher(neupassword)._hash(neupassword)
            # replace password in df with new password
            df.loc[df['name'] == self.user, 'password'] = pw
            # update table with new password
            
            updateTable(df,'user')
            st.success("Passwort erfolgreich geändert! Bitte Logge dich aus")
    def newPasswort_Admin(self):

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




        
