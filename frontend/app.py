import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,save_token,logout

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Mensajería Automática")

if st.session_state.get("token"):
    st.switch_page("pages/mails.py")
else:
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login = st.form_submit_button("Login")
    if login:
        response = requests.post(f"{API_URL}/auth/login",data={"username": user, "password": password})
        if response.status_code==200:
            token=response.json()["access_token"]
            save_token(token=token)
            st.switch_page("pages/mails.py")
        else:
            error=response.json()["detail"]
            st.error(error)