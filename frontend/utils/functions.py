import streamlit as st
import time
from streamlit_cookies_controller import CookieController
import requests
import os
from dotenv import load_dotenv

controller = CookieController() #Me sirve para guardar el token en las cookies, ya que streamlit borra el session_state cada vez que actualizo

def require_login():
    if not st.session_state.get("token"):
        token=controller.get("token")
        if token:
            st.session_state["token"]=token
        else:
            st.warning("Debés iniciar sesión para acceder a esta página")
            time.sleep(1)
            st.switch_page("app.py")
            st.stop()

def save_token(token):
    st.session_state["token"] = token
    controller.set("token",token)

def logout():
    st.session_state.clear()
    controller.remove("token")
    st.switch_page("app.py")

def get_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

#Guardo en Caché todas las marcas
@st.cache_data(ttl=30, show_spinner=False)
def get_brands():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    return requests.get(f"{API_URL}/brands", headers=get_headers()).json()

#Guardo en Caché todas los proveedores
@st.cache_data(ttl=30, show_spinner=False)
def get_providers():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    return requests.get(f"{API_URL}/providers", headers=get_headers()).json()

#Guardo en Caché todos los productos
@st.cache_data(ttl=30, show_spinner=False)
def get_products():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    return requests.get(f"{API_URL}/products", headers=get_headers()).json()
