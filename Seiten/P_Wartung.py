
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

class Wartung:

    def page():
        st.header("Wartungsarbeiten")
        st.subheader("Genießt das Wochenende!")

        img = Image.open('Data/img/muede.jpeg', mode='r')
        st.image(img, use_column_width=True)