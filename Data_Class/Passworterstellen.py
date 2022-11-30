import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
import pandas as pd
from SQL import createnewTable

names =  ["Martin", "admin", "Norbert"]
usernames = ["martin", "admin", "norbert"]
password = ["hannah", "admin", "schlangenleder"]
hasched_passwords = stauth.Hasher(password).generate()

#create df
df = pd.DataFrame()
df['name'] = names
df['username'] = usernames
df['password'] = hasched_passwords

createnewTable(df, 'user')