from fastapi import Depends, APIRouter, HTTPException,Form,UploadFile,File
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from modules.db import get_db
from modules.exceptions import handle_integrity_error
from modules.mail import create_preview,send_mail
from sqlalchemy import text,bindparam
from backend.models.models import SentCreate,SentResponse,MailPreviewCreate,MailPreviewResponse,SentHistoryResponse

router = APIRouter()

#Crea una preview del mail, que el usuario luego deberá validar/editar
@router.post("/mail/preview",response_model=MailPreviewResponse)
def mail_preview(mail:MailPreviewCreate,db: Session=Depends(get_db)):
    query_1=text("SELECT p.Product_Name,p.Serial_Number,b.Brand_Name FROM PRODUCT p " \
    "INNER JOIN BRAND b ON p.ID_Brand = b.ID WHERE p.ID=:id")
    product=db.execute(query_1,{"id":mail.id_product}).fetchone()
    if product is None:
        raise HTTPException(
                status_code=404,
                detail="El producto no se ha encontrado")
    product_name=product._mapping["product_name"]
    serial_number=product._mapping["serial_number"]
    brand_name=product._mapping["brand_name"]
    query_2=text("SELECT Email FROM PROVIDER WHERE ID=:id")
    provider=db.execute(query_2,{"id":mail.id_provider}).fetchone()
    if provider is None:
        raise HTTPException(
                status_code=404,
                detail="El proveedor no se ha encontrado")
    email=provider._mapping["email"]
    if mail.file_ids:
        query_3=text("SELECT File_Path FROM PRODUCT_FILE WHERE ID in :ids").bindparams(bindparam("ids", expanding=True))#le indica que ids es un parametro a expandir, una lista
        pictures=db.execute(query_3,{"ids":mail.file_ids}).fetchall()
        if len(pictures) != len(mail.file_ids):#el fetchall no devuelve None, a lo sumo una lista vacía []
            raise HTTPException(
                status_code=404,
                detail="No se han encontrado fotos")
        pictures_list=[row._mapping["file_path"] for row in pictures]
    else:
        pictures_list=None
    query_4=text("SELECT Mail_Template FROM PROVIDER_TEMPLATE WHERE ID= :id")
    template=db.execute(query_4,{"id":mail.id_template}).fetchone()
    if template is None:
        raise HTTPException(
                status_code=404,
                detail="No se ha encontrado el template")
    template=template._mapping["mail_template"]

    subject=f"Producto: {product_name} ({brand_name})"

    body=create_preview(template=template,product_name=product_name,brand_name=brand_name,serial_number=serial_number,case_type=mail.case_type,invoice=mail.invoice)
    preview=MailPreviewResponse(id_product=mail.id_product,id_provider=mail.id_provider,invoice=mail.invoice,case_type=mail.case_type,body_content=body,
                                image_urls=pictures_list,subject=subject,to_email=email)
    return preview

#Envía el mail validado por el usuario y guarda registro en DB
@router.post("/mail/send",response_model=SentResponse)
def send(id_product: int=Form(...),id_provider: int=Form(...),invoice: Optional[str]=Form(None),case_type:str=Form(...),body_content:str=Form(...),subject:str=Form(...),excel:Optional[UploadFile]=File(None),to_email:str=Form(...),image_urls:Optional[list[str]]=Form(None),db: Session=Depends(get_db)):
    mail=SentCreate(id_product=id_product,id_provider=id_provider,invoice=invoice,case_type=case_type,body_content=body_content,subject=subject)
    excel_bytes=excel.file.read() if excel else None
    try:
        send_mail(to_email=to_email,subject=mail.subject,body=mail.body_content,image_urls=image_urls,excel_bytes=excel_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        query=text("INSERT INTO SENT (ID_Product,ID_Provider,Provider_Email,Invoice,Case_Type,Subject_Email,Body_Content) VALUES(:id_product,:id_provider,:provider_email,:invoice,:case_type,:subject,:body) RETURNING ID,Created_at")
        sent=db.execute(query,{"id_product":mail.id_product,"id_provider":mail.id_provider,"provider_email":to_email,"invoice":mail.invoice,"case_type":mail.case_type,"subject":mail.subject,"body":mail.body_content}).fetchone()
        sent_id=sent._mapping["id"]
        created_at=sent._mapping["created_at"]
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    sent=SentResponse(id_sent=sent_id,sent_at=created_at)
    return sent

#Consulta a la DB todos los mails enviados
@router.get("/mail/sent",response_model=list[SentHistoryResponse])
def get_mails(db:Session=Depends(get_db)):
    query=text("SELECT s.ID,s.Created_at,s.Subject_Email,s.Provider_Email,prod.Product_Name,prov.Provider_Name FROM SENT s " \
    "INNER JOIN PRODUCT prod on s.ID_Product=prod.ID " \
    "INNER JOIN PROVIDER prov on s.ID_Provider=prov.ID " \
    "ORDER BY s.Created_at")
    all_sent=db.execute(query).fetchall()
    all_sent_list=[]
    if len(all_sent)>0:
        for row in all_sent:
            all_sent_list.append(SentHistoryResponse(id_sent=row._mapping["id"],sent_at=row._mapping["created_at"],subject=row._mapping["subject_email"],email_provider=row._mapping["provider_email"],product_name=row._mapping["product_name"],provider_name=row._mapping["provider_name"]))
    return all_sent_list
