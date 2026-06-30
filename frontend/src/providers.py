import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers,get_providers,validate_email
import time

#Marco como última pestaña visitada(Para comportamiento de Products)
st.session_state["last_page"] = "providers"

#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

#Para popup edición del Proveedor
@st.dialog("Editar proveedor")
def edit_provider(id,name,email):
    new_name = st.text_input("Nombre", value=name)
    new_email = st.text_input("Email", value=email)
    if st.button("Guardar"):
        if (new_name==name and new_email==email):
            st.rerun()
            #st.warning("Sin modificaciones")
        elif not new_name.strip():
            st.error("Debe ingresar un nombre de proveedor")
        elif not validate_email(email=new_email):
            st.error("Debe ingresar un email válido xxxx@xxx.xxx")
        else:
            edited_provider=requests.put(f"{API_URL}/providers/{id}",json={"provider_name":new_name,"email":new_email},headers=headers)
            if edited_provider.status_code==200:
                #st.success("Se ha modificado el Proveedor")
                st.cache_data.clear()
                st.rerun()
            else:
                error=edited_provider.json()["detail"]
                st.error(error)

#Confirmar borrar proveedor
@st.dialog("Confirmar eliminación")
def confirm_delete(id, name):
    st.write(f"¿Estás seguro que querés eliminar al proveedor: **{name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        deleted_provider = requests.delete(f"{API_URL}/providers/{id}", headers=headers)
        if deleted_provider.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_provider.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()

#Carga masiva excel
@st.dialog("Carga Masiva")
def provider_excel_upload():
    st.markdown("""
    ### 📋 Formato requerido del Excel

    Antes de subir el archivo, verificá que:

    · La primera fila contenga los encabezados  
    · Existan las columnas **Proveedor y Email**

    Ejemplo:

    | Proveedor | Email |
    |---|---|
    | Sony Central | centralsony@gmail.com |
    | Tecno SRL | srltecno@outlook.com |
    """)
    excel_file_provider = st.file_uploader("Subir Excel", type=["xlsx"])
    col1,col_empty,col2 = st.columns([4,4,3])
    if col1.button("Cargar Proveedores", type="primary"):
        if not excel_file_provider:
            st.error("Debe cargarse un excel")
        else:
            excel_file_bytes = excel_file_provider.read()
            send_file={"provider_excel": excel_file_bytes}
            response = requests.post(f"{API_URL}/providers/bulk-insert",files=send_file,headers=headers)
            if response.status_code==200:
                st.success("Proveedores Agregados")
                time.sleep(0.5)
                st.cache_data.clear()
                st.rerun()
            else:
                error=response.json()["detail"]
                st.error(error)
    if col2.button("Cancelar"):
        st.rerun()

with st.spinner("Cargando..."):
    providers_data=get_providers()
    
st.title("Ingresar nuevo Proveedor")

with st.form("Ingresar nuevo Proveedor"):
    provider_name = st.text_input("Nombre")
    email = st.text_input("Email")
    submit = st.form_submit_button("Ingresar", key=f"insert_provider")
if submit:
    if not provider_name.strip():
        st.error("Debe ingresar un nombre de proveedor")
    elif not validate_email(email=email):
        st.error("Debe ingresar un email válido xxxx@xxx.xxx")
    else:
        response = requests.post(f"{API_URL}/providers",json={"provider_name": provider_name,"email":email},headers=headers)
        if response.status_code==200:
            st.success("Proveedor agregado")
            time.sleep(0.5)
            st.cache_data.clear()
            st.rerun()
        else:
            error=response.json()["detail"]
            st.error(error)

st.caption("Carga Masiva")    
if st.button(label="Carga masiva con excel"):
    provider_excel_upload()  

st.title("Gestionar Proveedores")
#providers_data=get_providers()
search = st.text_input("Buscar proveedor", placeholder="Escribí un nombre...")
filtered = [b for b in providers_data if search.strip().lower() in b["provider_name"].lower()]

# Headers
col1, col2, col3, col4 = st.columns([5, 5, 1, 1])
col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PROVEEDOR</p>", unsafe_allow_html=True)
col2.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>EMAIL</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)


for provider in filtered:
    col1, col2, col3, col4 = st.columns([5,5, 1, 1])
    col1.write(provider["provider_name"])
    col2.write(provider["email"])
    if col3.button("✏️", key=f"edit_{provider['id']}"):
        edit_provider(name=provider["provider_name"],email=provider["email"],id=provider["id"])
    if col4.button("🗑️", key=f"del_{provider['id']}"):
        confirm_delete(name=provider["provider_name"],id=provider["id"])
    st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)
