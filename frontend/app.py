import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
#Lo hago con try/excepto para evitar que en la primera carga salga pantalla de error (no llega a cargar modulos antes de renderizar)
try:
    from utils.functions import save_token, controller, is_token_expired
except Exception:
    st.rerun()
    st.stop()

#Formato HTML Global
st.markdown("""
<style>
/* Importar fuente más refinada */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* Tipografía global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Títulos principales — más livianos y elegantes */
h1 {
    font-weight: 500 !important;
    font-size: 1.8rem !important;
    letter-spacing: -0.02em !important;
    color: #E8E8E8 !important;
}

h2 {
    font-weight: 400 !important;
    font-size: 1.2rem !important;
    letter-spacing: -0.01em !important;
    color: #C0C0C0 !important;
}

/* Caption más sutil */
small, .caption {
    font-size: 0.75rem !important;
    color: #666 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* Botones más refinados */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s ease !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Formularios con borde más sutil */
.stForm {
    border: 1px solid #2A2A2A !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
}

/* Dividers más finos */
hr {
    border-color: #222 !important;
    margin: 0.3rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

pages = [
    st.Page("src/mails.py", title="Enviar Correo", icon="✉️"),
    st.Page("src/brands.py", title="Marcas", icon="🏷️"),
    st.Page("src/providers.py", title="Proveedores", icon="🏢"),
    st.Page("src/products.py", title="Productos", icon="📦"),
    st.Page("src/templates.py", title="Plantillas", icon="📝"),
    st.Page("src/history.py", title="Historial", icon="📋"),
]

#Si tengo el token en las coockies del navegador se lo paso al state de streamlit.
token = controller.get("token")
if token:
    st.session_state["token"] = token
else:
    st.session_state.pop("token", None) 
    retries= st.session_state.get("cookie_retries",0)
    if retries<3:
        st.session_state["cookie_retries"]=retries+1
        time.sleep(1)
        st.rerun()
        st.stop()
    pg = st.navigation(pages, position="hidden")
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

if st.session_state.get("token") and is_token_expired():
    st.session_state.clear()
    if controller.get("token"):
        controller.remove("token")
    st.rerun()

if not st.session_state.get("token"):
    #Despierto el back:
    try:
        requests.get(f"{API_URL}/health", timeout=10)
    except:
        pass
    st.title("Mensajería Automática")
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login = st.form_submit_button("Login")
    if login:
        if not user or not password:
            st.error("Ingresar usuario y contraseña")
        else:
            try:
                response = requests.post(f"{API_URL}/auth/login",data={"username": user, "password": password},timeout=10)
                if response.status_code==200:
                    token=response.json()["access_token"]
                    save_token(token=token)
                    st.rerun()
                else:
                    error=response.json()["detail"]
                    st.error(error)
            except requests.exceptions.RequestException:
                st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")
    st.stop()

# Si hay token, mostrar navegación

pg = st.navigation(pages, position="sidebar")
pg.run()