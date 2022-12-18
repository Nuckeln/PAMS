import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path

names =  ["Martin", "admin", "Norbert", 'MichaelK','Markus']
usernames = ["martin", "admin", "norbert", "michaelk", "markus"]
password = ["hannah", "Merle25-", "schlangenleder","unterfluhrschleppkettenfördersystem",'Bayern1']

hasched_passwords = stauth.Hasher(password).generate()
file_path = Path(__file__).parent / "passwords.pk1"

with file_path.open("wb") as file:
    pickle.dump(hasched_passwords, file)


