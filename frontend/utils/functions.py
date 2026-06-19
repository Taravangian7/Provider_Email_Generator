import streamlit as st
import time
from streamlit_cookies_controller import CookieController

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
