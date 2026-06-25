import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import require_login,logout,get_headers,get_products,get_providers,get_templates

require_login()

headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

def clear_preview():
    if "preview_data" in st.session_state:
        del st.session_state["preview_data"]
    if "excel_bytes" in st.session_state:
        del st.session_state["excel_bytes"]

#Para popup edición de Marca
@st.dialog("Editar marca")
def edit_brand(id,name):
    new_name = st.text_input("Nombre", value=name)
    if st.button("Guardar"):
        if new_name==name:
            st.rerun()
        else:
            edited_brand=requests.put(f"{API_URL}/brands/{id}",json={"brand_name":new_name},headers=headers)
            if edited_brand.status_code==200:
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

#Hago todos los gets acá así me carga toda la página a la vez
with st.spinner("Cargando..."):
    providers_data=get_providers()
    products_data=get_products()
    
st.title("Mensajes")

provider_options = {b["provider_name"]: b["id"] for b in providers_data}
selected_provider = st.selectbox(
        "Elegir Proveedor",
        options=list(provider_options.keys()),
        index=None,
        placeholder="¿A quién querés enviar el mail?",
        on_change=clear_preview
)
if selected_provider:
    templates_data=get_templates(id=provider_options[selected_provider])
    with st.form(f"Generar nuevo mensaje {selected_provider}"):
        product_options = {f"{b["product_name"]} {b["brand_name"]} ({b["serial_number"]})": b["id"] for b in products_data}
        selected_product = st.selectbox(
            "Elegir Producto",
            options=list(product_options.keys()),
            index=None,
            placeholder="Escribí o seleccioná un producto..."
        )
        template_options = {b["template_name"]: [b["id_template"],b["template_body"]] for b in templates_data}
        selected_template = st.selectbox(
            "Elegir Template",
            options=list(template_options.keys()),
            index=None,
            placeholder="Escribí o seleccioná un template..."
        )
        case_type = st.radio(
        "Tipo de caso",
        options=["cliente", "stock"],
        index=0
        )
        invoice_input = st.text_input("Factura / Invoice", placeholder="Opcional...")
        submit = st.form_submit_button("Ingresar", key="create_preview")
        if submit:
            if selected_product is None:
                st.error("Debes seleccionar un producto")
            elif selected_template is None:
                st.error("Debes seleccionar una plantilla")
            elif "{invoice}" in template_options[selected_template][1] and not invoice_input.strip():
                st.error("Esta plantilla contiene una factura a autocompletar. Ingrese una")
            else:
                invoice = invoice_input if invoice_input.strip() else None
                product_id=product_options[selected_product]
                template_id=template_options[selected_template][0]
                provider_id=provider_options[selected_provider]
                response=requests.post(f"{API_URL}/mail/preview",json={"id_product":product_id,"id_provider":provider_id,"id_template":template_id,"invoice":invoice,"case_type":case_type,"file_ids":None},headers=headers)
                if response.status_code==200:
                    st.session_state["preview_data"]=response.json()
                else:
                    error=response.json()["detail"]
                    st.error(error)
if st.session_state.get("preview_data"):
    preview = st.session_state["preview_data"]
    product_files_data = requests.get(f"{API_URL}/products/{preview['id_product']}/files", headers=headers).json()

    subject=st.text_input(label="Asunto ",value=preview["subject"])
    st.text(preview["to_email"])
    body_final=st.text_area(label="Mensaje",value=preview["body_content"])
    for file in product_files_data:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(file["file_path"], width=150)
        with col2:
            selected = st.checkbox("Adjuntar", key=f"foto_{file['id_file']}")
    image_urls = [
        f["file_path"] for f in product_files_data
        if st.session_state.get(f"foto_{f['id_file']}")
    ]
    excel_file = st.file_uploader("Adjuntar planilla Excel", type=["xlsx"])
    if excel_file:
        st.session_state["excel_bytes"] = excel_file.read()