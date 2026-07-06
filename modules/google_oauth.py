import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import requests as http_requests

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

#Establezco conexión con Google
def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )

_flow_store = {}
#Me conecto. Obtengo código de google para cambiar por token refresh
def get_authorization_url():
    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    _flow_store[state] = flow
    return auth_url

#Cambio código por token
def exchange_code_for_tokens(code, state):
    flow = _flow_store.pop(state, None)
    if not flow:
        flow = get_flow()
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Forzar refresh para obtener access token activo
    credentials.refresh(Request())
    
    print(f"Token: {credentials.token}")
    
    # Obtener email
    response = http_requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    print(f"Userinfo status: {response.status_code}")
    print(f"Userinfo body: {response.json()}")
    
    email = response.json().get("email")
    
    return {
        "refresh_token": credentials.refresh_token,
        "email": email
    }
#Obtengo credenciales para mandar mail (dura 1 hora)
def get_credentials_from_refresh_token(refresh_token):
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES
    )

def send_mail_google(refresh_token, to_email, subject, body, image_urls=None, excel_bytes=None):
    credentials = get_credentials_from_refresh_token(refresh_token)
    service = build('gmail', 'v1', credentials=credentials)

    mail = MIMEMultipart()
    mail['To'] = to_email
    mail['Subject'] = subject
    mail.attach(MIMEText(body, 'plain', 'utf-8'))

    if image_urls:
        for url in image_urls:
            r = http_requests.get(url)
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(r.content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{url.split("/")[-1]}"')
            mail.attach(part)

    if excel_bytes:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(excel_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="planilla.xlsx"')
        mail.attach(part)

    raw = base64.urlsafe_b64encode(mail.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()