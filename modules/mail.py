from typing import Optional
import smtplib
import os
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def create_preview(template:str,product_name:str,brand_name:str,serial_number:str,case_type:str,invoice:Optional[str]=None):
    variables={"product_name":product_name,
               "brand_name":brand_name,
               "serial_number":serial_number,
               "case_type":case_type,
               "invoice": invoice or ""}
    body=template.format(**variables)
    return body

def send_mail(to_email:str, subject:str, body:str, image_urls:list[str], excel_bytes:bytes):
    # 1. Crear el contenedor del mail
    mail = MIMEMultipart()
    mail["From"] = os.getenv("OUTLOOK_EMAIL")
    mail["To"] = to_email
    mail["Subject"] = subject

    # 2. Agregar el cuerpo de texto
    mail.attach(MIMEText(body, "plain"))

    # 3. Si hay imágenes, las descargo de Cloudinary y las adjunto
    if image_urls:
        for url in image_urls:
            response = requests.get(url)
            image_part = MIMEBase("application", "octet-stream")
            image_part.set_payload(response.content)
            encoders.encode_base64(image_part)
            filename = url.split("/")[-1]
            image_part.add_header("Content-Disposition", f"attachment; filename={filename}")
            mail.attach(image_part)

    # 4. Si hay Excel, lo adjunto directamente (ya tengo los bytes)
    if excel_bytes:
        excel_part = MIMEBase("application", "octet-stream")
        excel_part.set_payload(excel_bytes)
        encoders.encode_base64(excel_part)
        excel_part.add_header("Content-Disposition", "attachment; filename=planilla.xlsx")
        mail.attach(excel_part)

    # 5. Conectar al servidor y enviar
    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    server.login(os.getenv("OUTLOOK_EMAIL"), os.getenv("OUTLOOK_PASSWORD"))
    server.send_message(mail)
    server.quit()