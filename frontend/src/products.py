import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers,get_brands,get_products,get_providers,get_product_providers,get_product_files
import time

#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.dialog("Carga Masiva")
def product_excel_upload():
    st.markdown("""
    ### 📋 Formato requerido del Excel

    Antes de subir el archivo, verificá que:

    · La primera fila contenga los encabezados  
    · Existan las columnas **Producto, Serial Number y Marca**  
    · Las Marcas ingresadas ya existan en el sistema

    Ejemplo:

    | Producto | Serial Number | Marca
    |---|---|---|
    | Televisor | D5DS56ASD | LG |
    | Teléfono | JH54546JH | Samsung |
    """)
    excel_file_product = st.file_uploader("Subir Excel", type=["xlsx"])
    col1,col_empty,col2 = st.columns([4,4,3])
    if col1.button("Cargar Marcas", type="primary"):
        if not excel_file_product:
            st.error("Debe cargarse un excel")
        else:
            excel_file_bytes = excel_file_product.read()
            send_file={"product_excel": excel_file_bytes}
            response = requests.post(f"{API_URL}/products/bulk-insert",files=send_file,headers=headers)
            if response.status_code==200:
                st.success("Productos Agregados")
                time.sleep(0.5)
                st.cache_data.clear()
                st.rerun()
            else:
                error=response.json()["detail"]
                st.error(error)
    if col2.button("Cancelar"):
        st.rerun()

if st.session_state.get("last_page") != "products":
    if st.session_state.get("selected_product_id"):
        del st.session_state["selected_product_id"]

if st.session_state.get("selected_product_id"):
    #Si se pierde el id del producto en el session_state, redirijo a página producto
    product_id = st.session_state.get("selected_product_id")
    
    #Para resetear el UploadFile una vez cargada la foto:
    if "uploaded_foto" not in st.session_state:
        st.session_state["uploaded_foto"] = 0

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


    with st.spinner("Cargando..."):
        providers_data = get_providers()
        product_providers_data=get_product_providers(id_product=product_id)
        product_files_data=get_product_files(id_product=product_id)

    st.title("Gestionar proveedores")

    with st.form("Ingresar nuevo Proveedor"):
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
    # Headers
    col1, col2, col3 = st.columns([4,4,1])
    col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PROVEEDOR</p>", unsafe_allow_html=True)
    col2.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>EMAIL</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)

    for provider in product_providers_data:
        col1, col2, col3 = st.columns([4, 4, 1])
        col1.write(provider["provider_name"])
        col2.write(provider["email"])
        if col3.button("🗑️", key=f"delprov_{product_id}_{provider['id']}"):
            unassign_provider(provider_name=provider["provider_name"],id_product=product_id,id_provider=provider["id"])
        st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)

    st.title("Agregar fotos")

    with st.form("Ingresar nueva foto"):
        st.write(f"Producto: **{st.session_state.get("selected_product_name")}** ({st.session_state.get("selected_product_brand")})")
        uploaded_file = st.file_uploader("Subir foto", type=["jpg", "jpeg", "png", "webp"],key=f"upload_foto_{product_id}_{st.session_state["uploaded_foto"]}")
        submit1 = st.form_submit_button("Ingresar", key=f"insert_picture_{product_id}")
    if submit1:
        if uploaded_file is None:
            st.error("Selecciona un archivo")
        else:
            response = requests.post(f"{API_URL}/products/{product_id}/files",files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},headers=headers)
            if response.status_code==200:
                st.success("Foto cargada correctamente")
                st.session_state["uploaded_foto"]+=1
                time.sleep(0.5)
                st.cache_data.clear()
                st.rerun()
            else:
                error=response.json()["detail"]
                st.error(error)

    # Headers
    col1, col2, col3 = st.columns([4,4,1])
    col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>URL</p>", unsafe_allow_html=True)
    col2.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>TIPO</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)
    for file in product_files_data:
        col1, col2, col3 = st.columns([4, 4, 1])
        col1.write(file["file_path"])
        col2.write(file["file_type"])
        if col3.button("🗑️", key=f"delfile_{product_id}_{file['id_file']}"):
            delete_file(id_file=file['id_file'],id_product=file['id_product'])
        st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)
    if st.button("← Volver a productos"):
        del st.session_state["selected_product_id"]
        st.rerun()

else:
    st.session_state["last_page"] = "products"
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
                data=response.json()
                st.session_state["selected_product_id"]=data["id"]
                st.session_state["selected_product_name"] = data["product_name"]
                st.session_state["selected_product_brand"] = data["brand_name"]
                st.cache_data.clear()
                st.rerun()
            else:
                error=response.json()["detail"]
                st.error(error)

    st.caption("Carga Masiva")    
    if st.button(label="Carga masiva con excel"):
        product_excel_upload() 

    st.title("Gestionar Producto")

    search = st.text_input("Buscar producto", placeholder="Escribí un nombre...")
    filtered = [b for b in products_data if search.strip().lower() in b["product_name"].lower()]
    # Headers
    col1, col2, col3,col4,col5,col6 = st.columns([3,3,3,1,1,1])
    col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PRODUCTO</p>", unsafe_allow_html=True)
    col2.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>SERIAL NUMBER</p>", unsafe_allow_html=True)
    col3.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>MARCA</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)

    for product in filtered:
        col1, col2,col3, col4, col5,col6 = st.columns([3,3,3,1, 1, 1])
        col1.write(product["product_name"])
        col2.write(product["serial_number"])
        col3.write(product["brand_name"])
        if col4.button("📋", key=f"detail_{product['id']}"):
            st.session_state["selected_product_id"] = product["id"]
            st.session_state["selected_product_name"] = product["product_name"]
            st.session_state["selected_product_brand"] = product["brand_name"]
            st.rerun()
        if col5.button("✏️", key=f"edit_{product['id']}"):
            edit_product(product_name=product["product_name"],serial_number=product["serial_number"],id=product["id"],brand_name=product["brand_name"],brand_options=brand_options)
        if col6.button("🗑️", key=f"del_{product['id']}"):
            confirm_delete(name=product["product_name"],id=product["id"])
        st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)
