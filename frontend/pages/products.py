import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,logout,get_headers,get_brands,get_products
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

#Para popup edición del Producto
@st.dialog("Editar producto")
def edit_product(id,brand_name,product_name,serial_number,brand_options):
    new_name = st.text_input("Nombre", value=product_name)
    new_serial = st.text_input("Serial Number", value=serial_number)
    brand_list = list(brand_options.keys())
    current_index = brand_list.index(brand_name) if brand_name in brand_list else 0
    selected_brand = st.selectbox(
    "Marca",
    options=list(brand_options.keys()),
    index=current_index,
    placeholder="Escribí o seleccioná una marca..."
)
    if st.button("Guardar"):
        if(new_name==product_name and new_serial==serial_number and selected_brand==brand_name):
            st.rerun()
        elif not new_name.strip():
            st.error("Debe ingresar un nombre de producto")
        elif not new_serial.strip():
            st.error("Debe ingresar un serial number")
        else:
            id_brand=brand_options[selected_brand]
            edited_product=requests.put(f"{API_URL}/products/{id}",json={"product_name":new_name,"serial_number":new_serial,"id_brand":id_brand},headers=headers)
            if edited_product.status_code==200:
                #st.success("Se ha modificado el Producto")
                st.cache_data.clear()
                st.rerun()
            else:
                error=edited_product.json()["detail"]
                st.error(error)

#Confirmar borrar producto
@st.dialog("Confirmar eliminación")
def confirm_delete(id, name):
    st.write(f"¿Estás seguro que querés eliminar el producto: **{name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        deleted_product = requests.delete(f"{API_URL}/products/{id}", headers=headers)
        if deleted_product.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_product.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()


with st.spinner("Cargando..."):
    products_data=get_products()
    brands_data = get_brands()
brand_options = {b["brand_name"]: b["id"] for b in brands_data}

st.title("Ingresar nuevo Producto")

with st.form("Ingresar nuevo Producto"):
    product_name = st.text_input("Nombre")
    serial_number = st.text_input("Serial Number")
    selected_brand = st.selectbox(
    "Marca",
    options=list(brand_options.keys()),
    index=None,
    placeholder="Escribí o seleccioná una marca..."
)
    submit = st.form_submit_button("Ingresar", key=f"insert_product")
if submit:
    if selected_brand is None:
        st.error("Selecciona una Marca")
    elif not product_name.strip():
        st.error("Debe ingresar un nombre de producto")
    elif not serial_number.strip():
        st.error("Debe ingresar un serial number")
    else:
        id_brand=brand_options[selected_brand]
        response = requests.post(f"{API_URL}/products",json={"product_name": product_name,"serial_number":serial_number,"id_brand":id_brand},headers=headers)
        if response.status_code==200:
            st.success("Producto agregado")
            time.sleep(0.5)
            st.cache_data.clear()
            st.rerun()
        else:
            error=response.json()["detail"]
            st.error(error)

st.title("Gestionar Producto")

search = st.text_input("Buscar producto", placeholder="Escribí un nombre...")
filtered = [b for b in products_data if search.strip().lower() in b["product_name"].lower()]

for product in filtered:
    col1, col2,col3, col4, col5,col6 = st.columns([4,4,4,1, 1, 1])
    col1.write(product["product_name"])
    col2.write(product["serial_number"])
    col3.write(product["brand_name"])
    if col4.button("📋", key=f"detail_{product['id']}"):
        st.session_state["selected_product_id"] = product["id"]
        st.session_state["selected_product_name"] = product["product_name"]
        st.session_state["selected_product_brand"] = product["brand_name"]
        st.switch_page("pages/_product_detail.py")
    if col5.button("✏️", key=f"edit_{product['id']}"):
        edit_product(product_name=product["product_name"],serial_number=product["serial_number"],id=product["id"],brand_name=product["brand_name"],brand_options=brand_options)
    if col6.button("🗑️", key=f"del_{product['id']}"):
        confirm_delete(name=product["product_name"],id=product["id"])
    st.divider()
