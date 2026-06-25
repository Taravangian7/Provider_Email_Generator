import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,logout,get_headers,get_providers
import time

#Verifico tener token de acceso, en caso de estar en el state de la web se lo paso al state de streamlit
require_login()
#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

#Si se pierde el id del producto en el session_state, redirijo a página producto
product_id = st.session_state.get("selected_product_id")
if product_id is None:
    st.warning("Seleccioná un producto desde la lista")
    st.switch_page("pages/products.py")
    st.stop()

#Confirmar desasociar proveedor
@st.dialog("Confirmar eliminación")
def unassign_provider(id_product,id_provider, provider_name):
    st.write(f"¿Estás seguro que querés desasociar al proveedor: **{provider_name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, desasociar", type="primary"):
        deleted_provider = requests.delete(f"{API_URL}/products/{id_product}/providers/{id_provider}", headers=headers)
        if deleted_provider.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_provider.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()

#Confirmar borrar foto
@st.dialog("Confirmar eliminación")
def delete_file(id_product,id_file):
    st.write(f"¿Estás seguro que querés eliminar esta foto?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        deleted_file = requests.delete(f"{API_URL}/products/{id_product}/files/{id_file}", headers=headers)
        if deleted_file.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_file.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()

#Guardo en Caché todos los productos
@st.cache_data(ttl=30, show_spinner=False)
def get_product_providers(id_product):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    return requests.get(f"{API_URL}/products/{id_product}/providers", headers=get_headers()).json()

#Guardo en Caché todas las imágenes
@st.cache_data(ttl=30, show_spinner=False)
def get_product_files(id_product):
    load_dotenv()
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    return requests.get(f"{API_URL}/products/{id_product}/files", headers=get_headers()).json()

with st.spinner("Cargando..."):
    providers_data = get_providers()
    product_providers_data=get_product_providers(id_product=product_id)
    product_files_data=get_product_files(id_product=product_id)

st.title("Gestionar proveedores")

with st.form("Ingresar nuevo Producto"):
    provider_options = {b["provider_name"]: b["id"] for b in providers_data}
    st.write(f"Producto: **{st.session_state.get("selected_product_name")}** ({st.session_state.get("selected_product_brand")})")
    selected_provider = st.selectbox(
    "Asignar Proveedor",
    options=list(provider_options.keys()),
    index=None,
    placeholder="Escribí o seleccioná un proveedor..."
)
    submit = st.form_submit_button("Ingresar", key=f"insert_provider_{product_id}")
if submit:
    if selected_provider is None:
        st.error("Selecciona un proveedor")
    else:
        id_provider=provider_options[selected_provider]
        response = requests.post(f"{API_URL}/products/{product_id}/providers",json={"id_provider": id_provider},headers=headers)
        if response.status_code==200:
            st.success("Proveedor asociado")
            time.sleep(0.5)
            st.cache_data.clear()
            st.rerun()
        else:
            error=response.json()["detail"]
            st.error(error)

for provider in product_providers_data:
    col1, col2, col3 = st.columns([4, 4, 1])
    col1.write(provider["provider_name"])
    col2.write(provider["email"])
    if col3.button("🗑️", key=f"delprov_{product_id}_{provider['id']}"):
        unassign_provider(provider_name=provider["provider_name"],id_product=product_id,id_provider=provider["id"])
    st.divider()

st.title("Agregar fotos")

with st.form("Ingresar nueva foto"):
    st.write(f"Producto: **{st.session_state.get("selected_product_name")}** ({st.session_state.get("selected_product_brand")})")
    uploaded_file = st.file_uploader("Subir foto", type=["jpg", "jpeg", "png", "webp"])
    submit1 = st.form_submit_button("Ingresar", key=f"insert_picture_{product_id}")
if submit1:
    if uploaded_file is None:
        st.error("Selecciona un archivo")
    else:
        response = requests.post(f"{API_URL}/products/{product_id}/files",files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},headers=headers)
        if response.status_code==200:
            st.success("Foto cargada correctamente")
            time.sleep(0.5)
            st.cache_data.clear()
            st.rerun()
        else:
            error=response.json()["detail"]
            st.error(error)

for file in product_files_data:
    col1, col2, col3 = st.columns([4, 4, 1])
    col1.write(file["file_path"])
    col2.write(file["file_type"])
    if col3.button("🗑️", key=f"delfile_{product_id}_{file['id_file']}"):
        delete_file(id_file=file['id_file'],id_product=file['id_product'])
    st.divider()