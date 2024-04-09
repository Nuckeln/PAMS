import pandas as pd
import streamlit_authenticator as stauth
from Data_Class.SQL import read_table, updateTable
import streamlit as st


def login():

    df = read_table('user')
    usernames = df['username'].tolist()
    names = df['name'].tolist()
    passwords = df['password'].tolist()
    funktionen = df['function'].tolist()
    rechte = df['rechte'].tolist()
    credentials = {"usernames":{}}
    

    # Extract the values from the DataFrame and add them to the 'credentials' dictionary.
    for uname,name,pwd,funktion,rechte in zip(usernames,names,passwords,funktionen,rechte):
        user_dict = {"name": name, "password": pwd, "function": funktion, "rechte": rechte}
        credentials["usernames"].update({uname: user_dict})
    
    authenticator = stauth.Authenticate(credentials, "PamsReportingTool", "random_key",
                                            cookie_expiry_days=30)
    authenticator.login()
    st.session_state.user = name
    st.session_state.rechte = df.loc[df['name'] == name, 'rechte'].iloc[0]
    return authenticator

def logout():
    
    authenticator = login()
    authenticator.logout('Logout', 'main')
    
    if st.session_state.user is None:
        st.success("Logout successful!", key='logout_success')
        st.session_state.rechte = 0
        st.session_state.user = ''
        st.session_state.password = ''
        st.rerun()

if __name__ == "__main__":
    login()




