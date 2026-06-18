from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from modules.db import get_db
from modules.exceptions import handle_integrity_error
from sqlalchemy import text
from backend.models.models import ProviderCreate,ProviderResponse,TemplateCreate,TemplateResponse

router = APIRouter()

@router.get("/providers",response_model=list[ProviderResponse])
def providers(db: Session=Depends(get_db)): 
    all_providers=db.execute(text("Select ID,Provider_Name,Email From PROVIDER")).fetchall()
    provider_list= []
    for row in all_providers:
        provider_list.append(ProviderResponse(id=row._mapping["id"],provider_name=row._mapping["provider_name"],email=row._mapping["email"]))
    return provider_list

@router.post("/providers",response_model=ProviderResponse)
def new_provider(provider:ProviderCreate,db: Session=Depends(get_db)):
    query=text("INSERT INTO PROVIDER (Provider_Name,Email) VALUES (:provider_name, :email) RETURNING ID, Provider_Name, Email;")
    try:
        insert_provider=db.execute(query,{"provider_name":provider.provider_name,"email":provider.email}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    provider= ProviderResponse(id=insert_provider._mapping["id"],provider_name=insert_provider._mapping["provider_name"],email=insert_provider._mapping["email"])
    return provider

@router.put("/providers/{id}",response_model=ProviderResponse)
def modify_provider(id:int, provider:ProviderCreate,db: Session=Depends(get_db)):
    query=text("UPDATE PROVIDER SET Provider_Name = :provider_name, Email = :email WHERE ID = :id RETURNING ID, Provider_Name, Email;")
    try:
        update_provider=db.execute(query,{"provider_name":provider.provider_name,"email":provider.email,"id":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if update_provider is None:
            raise HTTPException(
                status_code=404,
                detail="El proveedor no se ha encontrado en la base de datos")
    provider= ProviderResponse(id=update_provider._mapping["id"],provider_name=update_provider._mapping["provider_name"],email=update_provider._mapping["email"])
    return provider

@router.delete("/providers/{id}",response_model=ProviderResponse)
def delete_provider(id:int,db: Session=Depends(get_db)):
    query=text("DELETE FROM PROVIDER WHERE ID = :id RETURNING ID, Provider_Name, Email;")
    try:
        delete_provider=db.execute(query,{"id":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if delete_provider is None:
            raise HTTPException(
                status_code=404,
                detail="El proveedor no se ha encontrado en la base de datos")
    provider= ProviderResponse(id=delete_provider._mapping["id"],provider_name=delete_provider._mapping["provider_name"],email=delete_provider._mapping["email"])
    return provider

@router.get("/providers/{id}/templates",response_model=list[TemplateResponse])
def templates(id:int, db: Session=Depends(get_db)):
    query= text("Select ID,Template_Name,Mail_Template From PROVIDER_TEMPLATE WHERE ID_Provider= :id_provider") 
    all_templates=db.execute(query,{"id_provider":id}).fetchall()
    template_list= []
    for row in all_templates:
        template_list.append(TemplateResponse(id_template=row._mapping["id"],id_provider=id,template_name=row._mapping["template_name"],template_body=row._mapping["mail_template"]))
    return template_list

@router.post("/providers/{id}/templates",response_model=TemplateResponse)
def new_template(id:int, template:TemplateCreate,db: Session=Depends(get_db)):
    query=text("INSERT INTO PROVIDER_TEMPLATE (ID_Provider,Template_Name,Mail_Template) VALUES (:id,:template_name,:mail_template) RETURNING ID, Template_Name, Mail_Template;")
    try:
        insert_template=db.execute(query,{"id":id,"template_name":template.template_name,"mail_template":template.template_body}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    template= TemplateResponse(id_template=insert_template._mapping["id"],id_provider=id,template_name=insert_template._mapping["template_name"],template_body=insert_template._mapping["mail_template"])
    return template

@router.put("/providers/{id}/templates/{id_template}",response_model=TemplateResponse)
def modify_template(id:int,id_template:int,template:TemplateCreate,db: Session=Depends(get_db)):
    query=text("UPDATE PROVIDER_TEMPLATE SET Template_Name = :template_name, Mail_Template = :mail_template WHERE ID = :id RETURNING Template_Name, Mail_Template;")
    try:
        update_template=db.execute(query,{"template_name":template.template_name,"mail_template":template.template_body,"id":id_template}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if update_template is None:
            raise HTTPException(
                status_code=404,
                detail="El template no se ha encontrado en la base de datos")
    template= TemplateResponse(id_template=id_template,id_provider=id,template_name=update_template._mapping["template_name"],template_body=update_template._mapping["mail_template"])
    return template

@router.delete("/providers/{id}/templates/{id_template}",response_model=TemplateResponse)
def delete_template(id:int,id_template:int,db: Session=Depends(get_db)):
    query=text("DELETE FROM PROVIDER_TEMPLATE WHERE ID = :id RETURNING Template_Name, Mail_Template;")
    try:
        delete_template=db.execute(query,{"id":id_template}).fetchone()
        db.commit()
    except IntegrityError as e: #Va por buenas prácticas pero no se dispara nunca. Solo existiría un error si el template tuviera una relación on delete restrict con otra tabla
        db.rollback()
        raise handle_integrity_error(e)
    if delete_template is None:
            raise HTTPException(
                status_code=404,
                detail="El template no se ha encontrado en la base de datos")
    template= TemplateResponse(id_template=id_template,id_provider=id,template_name=delete_template._mapping["template_name"],template_body=delete_template._mapping["mail_template"])
    return template