import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
import pandas as pd
import yaml
from yaml import SafeLoader
from Data_Class.SQL import datenLadenUser

class Login:

    def Login(self):
        df = datenLadenUser()
        usernames = df['username'].tolist()
        names = df['name'].tolist()
        passwords = df['password'].tolist()

        credentials = {"usernames":{}}
                
        for uname,name,pwd in zip(usernames,names,passwords):
            user_dict = {"name": name, "password": pwd}
            credentials["usernames"].update({uname: user_dict})
                
        authenticator = stauth.Authenticate(credentials, "cokkie_name", "random_key", cookie_expiry_days=1)

        name, authentication_status, usernames= authenticator.login("Login", 'main')
        if authentication_status == False:
            st.error("Login fehlgeschlagen")
        if authentication_status == None:
            st.info("Bitte loggen Sie sich ein")
        if authentication_status == True:
            #erfolgreich geladen dann Code ausführen!
            return authentication_status


        # output==>
        #{'usernames': {'user1': {'name': 'name1', 'password': 'pwd1'}, 'user2': {'name': 'name2', 'password': 'pwd2'}}}