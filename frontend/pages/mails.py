import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,save_token,logout

require_login()
st.title("Mensajes")

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()