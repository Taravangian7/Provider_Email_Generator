import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers
from datetime import datetime

#Aumento el ancho de esta página
st.markdown("""
<style>
.block-container {
    max-width: 80%;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

#Marco como última pestaña visitada(Para comportamiento de Products)
st.session_state["last_page"] = "history"

#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

#Obtengo histórico y guardo en caché
@st.cache_data(ttl=30, show_spinner=False)
def get_historical():
    try:
        response=requests.get(f"{API_URL}/mail/sent", headers=get_headers()).json()
    except:
        response=[]
    return response


with st.spinner("Cargando..."):
    mails=get_historical()

st.title("Mensajes enviados")

search_provider = st.text_input("Buscar proveedor", placeholder="Escribí un nombre...")
search_product = st.text_input("Buscar producto", placeholder="Escribí un nombre...")
filtered = [b for b in mails if search_provider.strip().lower() in b["provider_name"].lower() and search_product.strip().lower() in b["product_name"].lower()]

#HTML PARA BARRA LATERAL
st.markdown("""
<style>
.mail-container {
    max-height: 600px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="mail-container">', unsafe_allow_html=True)

# Headers
col1, col2, col3,col4,col5 = st.columns([2,2,3,4,4])
col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>FECHA</p>", unsafe_allow_html=True)
col2.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PROVEEDOR</p>", unsafe_allow_html=True)
col3.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PRODUCTO</p>", unsafe_allow_html=True)
col4.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>ASUNTO</p>", unsafe_allow_html=True)
col5.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>EMAIL</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)

for mail in filtered:
    col1, col2, col3, col4, col5 = st.columns([2,2,3,4,4])
    fecha = datetime.fromisoformat(mail["sent_at"].replace("Z", "+00:00"))
    fecha_formateada = fecha.strftime("%d/%m/%Y %H:%M")
    col1.write(fecha_formateada)
    col2.write(mail["provider_name"])
    col3.write(mail["product_name"])
    col4.write(mail["subject"])
    col5.write(mail["email_provider"])

    st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)