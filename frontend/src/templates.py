import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.functions import logout,get_headers,get_providers,get_templates
import time

#Marco como última pestaña visitada(Para comportamiento de Products)
st.session_state["last_page"] = "templates"

#Configuro headers de endpoints para mandar el token
headers = get_headers()

with st.sidebar:
        if st.button("Cerrar sesión"):
            logout()

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

#Nuevo Template
st.markdown("""
<style>
div[data-testid="stDialog"] div[role="dialog"] {
    width: 700px;
    max-width: 90vw;
}
</style>
""", unsafe_allow_html=True)
@st.dialog("Nueva Plantilla")
def new_template(provider_id):
    # El texto del template se guarda en session_state para poder modificarlo
    if "template_body" not in st.session_state or st.session_state.get("reset_template"):
        st.session_state["template_body"] = ""
        st.session_state["reset_template"] = False
        if "template_name" in st.session_state:
            st.session_state["template_name"] = ""
    template_name=st.text_input(label="Nombre de la Plantila",placeholder="Inserte un nombre...",key="template_name")
    # Botones de variables — cada uno agrega al texto actual
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("+ Producto"):
        st.session_state["template_body"] += "{product_name}"
    if col2.button("+ Serial"):
        st.session_state["template_body"] += "{serial_number}"
    if col3.button("+ Marca"):
        st.session_state["template_body"] += "{brand_name}"
    if col4.button("+ Factura"):
        st.session_state["template_body"] += "{invoice}"
    if col5.button("+ Caso"):
        st.session_state["template_body"] += "{case_type}"
    # El text_area usa el valor del session_state
    body = st.text_area("Cuerpo del mail", key="template_body", height=200)
    commit_template=st.button(label="Guardar",key="save_template")
    if commit_template:
        save_template=requests.post(f"{API_URL}/providers/{provider_id}/templates",json={"template_name":template_name,"template_body":body},headers=headers)
        if save_template.status_code==200:
            st.cache_data.clear()
            st.rerun()
        else:
            error=save_template.json()["detail"]
            st.error(error)

#Editar Template
@st.dialog("Editar Plantilla")
def edit_template(old_body,old_template_name,id_provider,id_template):
    # El texto del template se guarda en session_state para poder modificarlo
    if "template_body_edited" not in st.session_state or st.session_state.get("reset_template"):
        st.session_state["template_body_edited"] = old_body
        st.session_state["reset_template"] = False
        if "template_name_edited" in st.session_state:
            st.session_state["template_name_edited"] = old_template_name
    template_name=st.text_input(label="Nombre de la Plantila",value=old_template_name,key="template_name_edited")
    # Botones de variables — cada uno agrega al texto actual
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("+ Producto"):
        st.session_state["template_body_edited"] += "{product_name}"
    if col2.button("+ Serial"):
        st.session_state["template_body_edited"] += "{serial_number}"
    if col3.button("+ Marca"):
        st.session_state["template_body_edited"] += "{brand_name}"
    if col4.button("+ Factura"):
        st.session_state["template_body_edited"] += "{invoice}"
    if col5.button("+ Caso"):
        st.session_state["template_body_edited"] += "{case_type}"
    # El text_area usa el valor del session_state
    body = st.text_area("Cuerpo del mail", key="template_body_edited", height=200)
    commit_template=st.button(label="Guardar",key="save_template_edited")
    if commit_template:
        if (template_name==old_template_name and body==old_body):
            st.rerun()
        else:
            save_template=requests.put(f"{API_URL}/providers/{id_provider}/templates/{id_template}",json={"template_name":template_name,"template_body":body},headers=headers)
            if save_template.status_code==200:
                st.cache_data.clear()
                st.rerun()
            else:
                error=save_template.json()["detail"]
                st.error(error)

#Confirmar borrar template
@st.dialog("Confirmar eliminación")
def confirm_delete(id_provider,id_template, name):
    st.write(f"¿Estás seguro que querés eliminar el template **{name}**?")
    col1, col2 = st.columns(2)
    if col1.button("Sí, eliminar", type="primary"):
        deleted_template = requests.delete(f"{API_URL}/providers/{id_provider}/templates/{id_template}", headers=headers)
        if deleted_template.status_code == 200:
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(deleted_template.json()["detail"])
    if col2.button("Cancelar"):
        st.rerun()

with st.spinner("Cargando..."):
    providers=get_providers()

st.title("Plantillas")

providers_option={a["provider_name"]:[a["id"],a["email"]] for a in providers}
selected_provider=st.selectbox(
    "Proveedor",
    options=list(providers_option.keys()),
    index=None,
    placeholder="Escribí o seleccioná un proveedor..."
)
if selected_provider:
    provider_id=providers_option[selected_provider][0]
    provider_email=providers_option[selected_provider][1]
    insert_template=st.button(label="Crear nueva Plantilla",key=f"new_template_{provider_id}")
    if insert_template:
        st.session_state["reset_template"] = True
        new_template(provider_id=provider_id)

    templates=get_templates(id=provider_id)
    if templates:
        st.title("Gestionar plantillas")

        # Headers
        col1, col2, col3 = st.columns([8,1,1])
        col1.markdown("<p style='color: gray; font-size: 12px; margin: 0;'>PLANTILLA</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 4px 0; border-color: #555;'>", unsafe_allow_html=True)
        for template in templates:
            col1, col2, col3 = st.columns([8, 1, 1])
            col1.write(template["template_name"])
            if col2.button("✏️", key=f"edit_template_{template['id_template']}"):
                st.session_state["reset_template"] = True
                edit_template(id_template=template["id_template"],old_body=template["template_body"],old_template_name=template["template_name"],id_provider=template["id_provider"])
            if col3.button("🗑️", key=f"del_template_{template['id_template']}"):
                confirm_delete(id_template=template["id_template"],id_provider=template["id_provider"],name=template["template_name"])
            st.markdown("<hr style='margin: 4px 0; border-color: #333;'>", unsafe_allow_html=True)