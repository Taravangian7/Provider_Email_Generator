import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers,get_providers,get_templates,get_product_files,get_provider_products
import time

#Marco como última pestaña visitada(Para comportamiento de Products)
st.session_state["last_page"] = "mails"

load_dotenv(override=True)
API_URL = os.getenv("API_URL", "http://localhost:8000")

headers = get_headers()

with st.sidebar:
    st.divider()
    gmail_status = requests.get(f"{API_URL}/google/status", headers=get_headers())
    if gmail_status.status_code == 200 and gmail_status.json().get("connected"):
        email = gmail_status.json().get("email")
        st.markdown(f"""
            <div style='font-size:12px; color:#888; margin-bottom:4px;'>Gmail conectado</div>
            <div style='font-size:13px; color:#ccc; margin-bottom:8px;'>{email}</div>
        """, unsafe_allow_html=True)
        if st.button("Desconectar Gmail", use_container_width=True):
            requests.delete(f"{API_URL}/google/disconnect", headers=get_headers())
            st.rerun()
    else:
        if st.button("Conectar Gmail", use_container_width=True):
            auth_response = requests.get(f"{API_URL}/google/authorize", headers=get_headers())
            auth_url = auth_response.json()["auth_url"]
            st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
    if st.button("Cerrar sesión", use_container_width=True):
        logout()

def clear_preview():
    if "preview_data" in st.session_state:
        del st.session_state["preview_data"]
    for key in list(st.session_state.keys()):
        if key.startswith("foto_"):
            del st.session_state[key]

#Para resetear el form una vez enviado el mail:
if "form_key_send" not in st.session_state:
    st.session_state["form_key_send"] = 0

#Hago todos los gets acá así me carga toda la página a la vez
with st.spinner("Cargando..."):
    providers_data=get_providers()
    
st.title("Mensajes")

provider_options = {b["provider_name"]: b["id"] for b in providers_data}
selected_provider = st.selectbox(
        "Elegir Proveedor",
        options=list(provider_options.keys()),
        index=None,
        placeholder="¿A quién querés enviar el mail?",
        on_change=clear_preview
)
if not selected_provider:
    clear_preview()
if selected_provider:
    templates_data=get_templates(id=provider_options[selected_provider])
    products_data=get_provider_products(id_provider=provider_options[selected_provider])
    with st.form(f"Generar nuevo mensaje {selected_provider} {st.session_state["form_key_send"]}"):
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
                try:
                    response=requests.post(f"{API_URL}/mail/preview",json={"id_product":product_id,"id_provider":provider_id,"id_template":template_id,"invoice":invoice,"case_type":case_type,"file_ids":None},headers=headers)
                    if response.status_code==200:
                        st.session_state["preview_data"]=response.json()
                    else:
                        error=response.json()["detail"]
                        st.error(error)
                except:
                    st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")
if st.session_state.get("preview_data"):
    with st.form(f"enviar email {selected_provider}"):
        preview = st.session_state["preview_data"]
        product_files_data = get_product_files(id_product=preview['id_product'])
        subject = st.text_input(label="Asunto", value=preview["subject"])
        st.caption(f"destinatario: {preview["to_email"]}")
        
        # Columna principal y columna lateral
        col_body, col_side = st.columns([3, 1])
        
        with col_body:
            body_final = st.text_area("", height=300, 
                                    value=preview["body_content"],
                                    label_visibility="collapsed")
        
        with col_side:
            st.markdown("<p style='color: gray; font-size: 16px; margin: 0;'>Insertar Excel</p>", unsafe_allow_html=True)
            excel_file = st.file_uploader("", type=["xlsx"])
            st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)
            #foto y checkbox
            if len(product_files_data) > 0:
                st.markdown("<p style='color: gray; font-size: 16px; margin: 200;'>Insertar Fotos</p>", unsafe_allow_html=True)
                for file in product_files_data[:3]:
                    col_foto,col_check=st.columns([3,1])
                    with col_foto:
                            st.image(image=file["file_path"], width=100)
                    with col_check:
                        st.checkbox("", key=f"foto_{file['id_file']}")
            else:
                st.markdown("<p style='color: gray; font-size: 16px; margin: 200;'>No hay Fotos</p>", unsafe_allow_html=True)
            if len(product_files_data) > 3:
                with st.expander(f"Ver {len(product_files_data) - 3} más"):
                    for file in product_files_data[3:]:
                        col_foto, col_check = st.columns([3, 1])
                        with col_foto:
                            st.image(file["file_path"], width=100)
                        with col_check:
                            st.checkbox("", key=f"foto_{file['id_file']}")
        # Enviar abajo a la izquierda
        col_btn, col_empty = st.columns([1, 3])
        with col_btn:
            sent_email = st.form_submit_button("Enviar", type="primary")
        if sent_email:
            if not gmail_status.json().get("connected"):
                st.error("Debés conectar tu cuenta de Gmail antes de enviar.")
            else:
                image_urls = [
                    f["file_path"] for f in product_files_data
                    if st.session_state.get(f"foto_{f['id_file']}")
                ]
                if excel_file:
                    excel_file_bytes = excel_file.read()
                    send_file={"excel": excel_file_bytes}
                else:
                    send_file= None
                try:
                    sent=requests.post(f"{API_URL}/mail/send",data={"id_product":preview['id_product'],"id_provider":preview['id_provider'],"invoice":preview['invoice'],"case_type":preview["case_type"],"body_content":body_final,"subject":subject,"to_email":preview["to_email"],"image_urls":image_urls},files=send_file ,headers=headers)
                    if sent.status_code==200:
                        st.success("Mail enviado")
                        st.session_state["form_key_send"] += 1 #Al enviar mail, queda preseleccionado el provider pero resetea form
                        time.sleep(0.5)
                        clear_preview()
                        st.rerun()
                    else:
                        error=sent.json()["detail"]
                except requests.exceptions.RequestException:
                    st.error("Error al conectar con el servidor. Intentá de nuevo en unos segundos.")