import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path

names =  ["Martin", "admin", "Norbert", 'MichaelK']
usernames = ["martin", "admin", "norbert", "michaelk"]
password = ["hannah", "Merle25-", "schlangenleder","unterfluhrschleppkettenfördersystem"]

hasched_passwords = stauth.Hasher(password).generate()
file_path = Path(__file__).parent / "passwords.pk1"

with file_path.open("wb") as file:
    pickle.dump(hasched_passwords, file)


