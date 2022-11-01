import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path

names =  ["Martin", "admin", "Norbert"]
usernames = ["martin", "admin", "norbert"]
password = ["hannah", "admin", "schlangenleder"]

hasched_passwords = stauth.Hasher(password).generate()
file_path = Path(__file__).parent / "passwords.pk1"

with file_path.open("wb") as file:
    pickle.dump(hasched_passwords, file)
