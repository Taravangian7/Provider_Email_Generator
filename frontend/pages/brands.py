import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,save_token,logout,get_headers

#Verifico tener token de acceso, en caso de estar en el state de la web se lo paso al state de streamlit
require_login()
#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

#Para popup edición de Marca
@st.dialog("Editar marca")
def edit_brand(id,name):
    new_name = st.text_input("Nombre", value=name)
    if st.button("Guardar"):
        edited_brand=requests.put(f"{API_URL}/brands/{id}",json={"brand_name":new_name},headers=headers)
        if edited_brand.status_code==200:
            st.success("Se ha modificado la Marca")
            st.cache_data.clear()
            st.rerun()
        else:
            error=edited_brand.json()["detail"]
            st.error(error)

#Confirmar borrar marca
@st.dialog("Confirmar eliminación")
def confirm_delete(id, name):
    st.write(f"¿Estás seguro que querés eliminar **{name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        deleted_brand = requests.delete(f"{API_URL}/brands/{id}", headers=headers)
        if deleted_brand.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_brand.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()

#Guardo en Caché todas las marcas
@st.cache_data(ttl=30, show_spinner=False)
def get_brands():
    return requests.get(f"{API_URL}/brands", headers=get_headers()).json()

st.title("Ingresar nueva Marca")

with st.form("Ingresar nueva Marca"):
    brand_name = st.text_input("Nombre")
    submit = st.form_submit_button("Ingresar", key=f"insert_brand")
if submit:
    response = requests.post(f"{API_URL}/brands",json={"brand_name": brand_name},headers=headers)
    if response.status_code==200:
        st.success("Marca agregada")
        st.cache_data.clear()
        st.rerun()
    else:
        error=response.json()["detail"]
        st.error(error)

st.title("Gestionar Marcas")
brands_data=get_brands()
search = st.text_input("Buscar marca", placeholder="Escribí un nombre...")
filtered = [b for b in brands_data if search.strip().lower() in b["brand_name"].lower()]

for brand in filtered:
    col1, col2, col3 = st.columns([8, 1, 1])
    col1.write(brand["brand_name"])
    if col2.button("✏️", key=f"edit_{brand['id']}"):
        edit_brand(name=brand["brand_name"],id=brand["id"])
    if col3.button("🗑️", key=f"del_{brand['id']}"):
        confirm_delete(name=brand["brand_name"],id=brand["id"])
    st.divider()
