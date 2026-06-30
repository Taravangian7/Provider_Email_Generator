from fastapi import Depends, APIRouter, HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from modules.db import get_db
from modules.exceptions import handle_integrity_error
from sqlalchemy import text
from backend.models.models import BrandCreate,BrandResponse
import pandas as pd

router = APIRouter()

@router.get("/brands",response_model=list[BrandResponse])
def brands(db: Session=Depends(get_db)): #No pasas get_db() porque sino la estarías ejecutando ahí mismo, vos le pasas la funcion a Depends y FastAPI ejecuta cuando necesita
    all_brands=db.execute(text("Select ID,Brand_Name From BRAND")).fetchall()
    brand_list= []
    for row in all_brands:
        brand_list.append(BrandResponse(id=row._mapping["id"],brand_name=row._mapping["brand_name"]))
    return brand_list

@router.post("/brands",response_model=BrandResponse)
def new_brand(brand:BrandCreate,db: Session=Depends(get_db)):
    query=text("INSERT INTO BRAND (Brand_Name) VALUES (:brand_name) RETURNING ID, Brand_Name;")
    try:
        insert_brand=db.execute(query,{"brand_name":brand.brand_name.strip().title()}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    brand= BrandResponse(id=insert_brand._mapping["id"],brand_name=insert_brand._mapping["brand_name"])
    return brand

@router.put("/brands/{id}",response_model=BrandResponse)
def modify_brand(id:int, brand:BrandCreate,db: Session=Depends(get_db)):
    query=text("UPDATE BRAND SET Brand_Name = :brand_name WHERE ID = :id RETURNING ID, Brand_Name;")
    try:
        update_brand=db.execute(query,{"brand_name":brand.brand_name.strip().title(),"id":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if update_brand is None:
            raise HTTPException(
                status_code=404,
                detail="La marca no se ha encontrado en la base de datos")
    brand= BrandResponse(id=update_brand._mapping["id"],brand_name=update_brand._mapping["brand_name"])
    return brand

@router.delete("/brands/{id}",response_model=BrandResponse)
def delete_brand(id:int,db: Session=Depends(get_db)):
    query=text("DELETE FROM BRAND WHERE ID = :id RETURNING ID, Brand_Name;")
    try:
        delete_brand=db.execute(query,{"id":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if delete_brand is None:
            raise HTTPException(
                status_code=404,
                detail="La marca no se ha encontrado en la base de datos")
    brand= BrandResponse(id=delete_brand._mapping["id"],brand_name=delete_brand._mapping["brand_name"])
    return brand

#bulk insert
@router.post("/brands/bulk-insert",response_model=bool)
def new_brand_bulk(brand_excel:UploadFile=File(...),db: Session=Depends(get_db)):
    try:
        df=pd.read_excel(brand_excel.file)
    except:
        raise HTTPException(status_code=400, detail="El archivo no es un Excel válido")
    if "Marca" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="El excel debe contener la columna Marca"
        )
    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="El excel está vacío"
        )
    try:    
        brands=[]
        for _,brand in df.iterrows():
            new_brand=BrandCreate(brand_name=brand["Marca"])
            brands.append(new_brand)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error procesando excel: {str(e)}"
        )
    
    query = text("""
        INSERT INTO BRAND (Brand_Name)
        VALUES (:brand_name)
    """)
    brands_data = [{"brand_name": brand.brand_name.strip().title()} for brand in brands]
    try:
        db.execute(query, brands_data)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    return True