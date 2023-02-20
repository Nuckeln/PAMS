import streamlit as st
import streamlit_authenticator as stauth
from Data_Class.SQL import datenLadenUser

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
        st.session_state.rechte = None


    def Login(self):
        # Initialize the 'rechte' attribute of session_state.
        st.session_state.rechte = None

        df = datenLadenUser()
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
                                            cookie_expiry_days=1)
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




        
