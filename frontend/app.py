import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Sistema de carga y notificaciones")

response = requests.get(f"{API_URL}/brands")

if response.status_code == 200:
    st.success("Conexión con el backend exitosa")
    data=response.json()
    st.write(data)
else:
    st.error("No se pudo conectar con el backend")