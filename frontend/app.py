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

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

pages = [
    st.Page("src/mails.py", title="Correos", icon="✉️"),
    st.Page("src/brands.py", title="Marcas", icon="🏷️"),
    st.Page("src/providers.py", title="Proveedores", icon="🏢"),
    st.Page("src/products.py", title="Productos", icon="📦"),
    st.Page("src/templates.py", title="Plantillas", icon="📝"),
    st.Page("src/history.py", title="Historial", icon="📋"),
]

#Si tengo el token en las coockies del navegador se lo paso al state de streamlit.
if not st.session_state.get("token"):
    with st.spinner(""):
        #if "initialized" not in st.session_state:
        #    st.session_state["initialized"] = True
        #    time.sleep(1)
        #    st.rerun()
        token = controller.get("token")
        if token:
            st.session_state["token"] = token
        else:
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
                response = requests.post(f"{API_URL}/auth/login",data={"username": user, "password": password})
                if response.status_code==200:
                    token=response.json()["access_token"]
                    save_token(token=token)
                    st.rerun()
                else:
                    error=response.json()["detail"]
                    st.error(error)
            except:
                st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")
    st.stop()

# Si hay token, mostrar navegación

pg = st.navigation(pages, position="sidebar")
pg.run()