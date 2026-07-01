import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers,get_brands
import time

#Marco como última pestaña visitada(Para comportamiento de Products)
st.session_state["last_page"] = "brands"

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
        if not new_name.strip():
            st.error("Debe ingresar un nombre de marca")
        else:
            if new_name==name:
                st.rerun()
            else:
                try:
                    edited_brand=requests.put(f"{API_URL}/brands/{id}",json={"brand_name":new_name},headers=headers)
                    if edited_brand.status_code==200:
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        error=edited_brand.json()["detail"]
                        st.error(error)
                except:
                    st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")

#Confirmar borrar marca
@st.dialog("Confirmar eliminación")
def confirm_delete(id, name):
    st.write(f"¿Estás seguro que querés eliminar **{name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        try:
            deleted_brand = requests.delete(f"{API_URL}/brands/{id}", headers=headers)
            if deleted_brand.status_code == 200:
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(deleted_brand.json()["detail"])
        except:
                st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")
    if col2.button("Cancelar"):
        st.rerun()

#Carga masiva excel
@st.dialog("Carga Masiva")
def brand_excel_upload():
    st.markdown("""
    ### 📋 Formato requerido del Excel

    Antes de subir el archivo, verificá que:

    · La primera fila contenga los encabezados  
    · Exista una columna llamada **Marca**

    Ejemplo:

    | Marca |
    |---|
    | Nike |
    | Adidas |
    """)
    excel_file_brand = st.file_uploader("Subir Excel", type=["xlsx"])
    col1,col_empty,col2 = st.columns([4,4,3])
    if col1.button("Cargar Marcas", type="primary"):
        if not excel_file_brand:
            st.error("Debe cargarse un excel")
        else:
            excel_file_bytes = excel_file_brand.read()
            send_file={"brand_excel": excel_file_bytes}
            try:
                response = requests.post(f"{API_URL}/brands/bulk-insert",files=send_file,headers=headers)
                if response.status_code==200:
                    st.success("Marcas Agregadas")
                    time.sleep(0.5)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    error=response.json()["detail"]
                    st.error(error)
            except:
                st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")
    if col2.button("Cancelar"):
        st.rerun()

#Hago todos los gets acá así me carga toda la página a la vez
with st.spinner("Cargando..."):
    brands_data=get_brands()
st.title("Ingresar nueva Marca")

with st.form("Ingresar nueva Marca"):
    brand_name = st.text_input("Nombre")
    submit = st.form_submit_button("Ingresar", key=f"insert_brand")
if submit:
    if not brand_name.strip():
        st.error("Debe ingresar un nombre de marca")
    else:
        try:
            response = requests.post(f"{API_URL}/brands",json={"brand_name": brand_name},headers=headers)
            if response.status_code==200:
                st.success("Marca agregada")
                time.sleep(0.5)
                st.cache_data.clear()
                st.rerun()
            else:
                error=response.json()["detail"]
                st.error(error)
        except:
            st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")

#st.caption("Carga Masiva")  
st.markdown("<p style='font-size:0.75rem; color:#555; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;'>Carga masiva</p>", unsafe_allow_html=True)  
if st.button(label="Carga masiva con excel"):
    brand_excel_upload()       

st.title("Gestionar Marcas")
search = st.text_input("Buscar marca", placeholder="Escribí un nombre...")
filtered = [b for b in brands_data if search.strip().lower() in b["brand_name"].lower()]

# Headers
col1, col2, col3 = st.columns([10,1,1])
col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>MARCA</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)

for brand in filtered:
    col1, col2, col3 = st.columns([10, 1, 1])
    col1.write(brand["brand_name"])
    if col2.button("✏️", key=f"edit_{brand['id']}"):
        edit_brand(name=brand["brand_name"],id=brand["id"])
    if col3.button("🗑️", key=f"del_{brand['id']}"):
        confirm_delete(name=brand["brand_name"],id=brand["id"])
    st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)
