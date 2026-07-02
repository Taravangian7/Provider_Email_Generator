import streamlit as st
import time
from streamlit_cookies_controller import CookieController
import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime, timedelta,timezone
import base64
import json

controller = CookieController() #Me sirve para guardar el token en las cookies, ya que streamlit borra el session_state cada vez que actualizo

def is_token_expired():
    token = st.session_state.get("token")
    if not token:
        return True
    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)  # padding base64
        data = json.loads(base64.b64decode(payload))
        exp = data.get("exp", 0)
        return datetime.now(timezone.utc).timestamp() > exp
    except:
        return True
    
def save_token(token):
    st.session_state["token"] = token
    controller.set("token",token, expires=datetime.now() + timedelta(hours=8))

def logout():
    st.session_state.clear()
    controller.remove("token")
    st.rerun()

def get_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

#Guardo en Caché todas las marcas
@st.cache_data(ttl=30, show_spinner=False)
def get_brands():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/brands", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todas los proveedores
@st.cache_data(ttl=30, show_spinner=False)
def get_providers():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/providers", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todos los productos
@st.cache_data(ttl=30, show_spinner=False)
def get_products():
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/products", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todas las plantillas
@st.cache_data(ttl=30, show_spinner=False)
def get_templates(id:int):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/providers/{id}/templates", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todos los proveedores asociados a un producto
@st.cache_data(ttl=30, show_spinner=False)
def get_product_providers(id_product):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/products/{id_product}/providers", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todos los productos asociados a un proveedor
@st.cache_data(ttl=30, show_spinner=False)
def get_provider_products(id_provider):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/providers/{id_provider}/products", headers=get_headers()).json()
    except:
        response=[]
    return response

#Guardo en Caché todas las imágenes
@st.cache_data(ttl=30, show_spinner=False)
def get_product_files(id_product):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    try:
        response=requests.get(f"{API_URL}/products/{id_product}/files", headers=get_headers()).json()
    except:
        response=[]
    return response

#Validar formato Email
def validate_email(email:str)->bool:
    return re.match(r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", email)

