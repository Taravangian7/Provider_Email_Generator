from fastapi import Depends, APIRouter, HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from modules.db import get_db
from modules.storage import upload_file,delete_cloudinary_file
from modules.exceptions import handle_integrity_error
from sqlalchemy import text
from backend.models.models import ProductCreate,ProductResponse,ProviderResponse,ProductProviderCreate,ProductFileResponse

router = APIRouter()

@router.get("/products",response_model=list[ProductResponse])
def products(db: Session=Depends(get_db)): 
    all_products=db.execute(text("Select p.ID,p.Product_Name,p.Serial_Number,p.ID_Brand,b.Brand_Name " \
    "From PRODUCT p INNER JOIN BRAND b on p.ID_Brand = b.ID")).fetchall()
    product_list= []
    for row in all_products:
        product_list.append(ProductResponse(id=row._mapping["id"],product_name=row._mapping["product_name"],serial_number=row._mapping["serial_number"],id_brand=row._mapping["id_brand"],brand_name=row._mapping["brand_name"]))
    return product_list

@router.get("/products/{id}",response_model=ProductResponse)
def product(id:int, db: Session=Depends(get_db)): 
    query = text("Select p.ID,p.Product_Name,p.Serial_Number,p.ID_Brand,b.Brand_Name From PRODUCT p " \
    "INNER JOIN BRAND b on p.ID_Brand = b.ID "\
    "WHERE p.ID = :id ")
    one_product=db.execute(query,{"id": id}).fetchone()
    if one_product is None:
        raise HTTPException(
            status_code=404,
            detail="El producto no se ha encontrado en la base de datos")
    one_product=ProductResponse(id=one_product._mapping["id"],product_name=one_product._mapping["product_name"],serial_number=one_product._mapping["serial_number"],id_brand=one_product._mapping["id_brand"],brand_name=one_product._mapping["brand_name"])
    return one_product

@router.post("/products",response_model=ProductResponse)
def new_product(product:ProductCreate,db: Session=Depends(get_db)):
    query=text("WITH New_Product as(INSERT INTO PRODUCT (Product_Name,Serial_Number,ID_Brand) VALUES (:product_name, :serial_number, :id_brand) RETURNING ID,Product_Name,Serial_Number,ID_Brand) " \
    "SELECT New_Product.ID,New_Product.Product_Name,New_Product.Serial_Number,New_Product.ID_Brand,b.Brand_Name FROM New_Product " \
    "INNER JOIN BRAND b on New_Product.ID_Brand = b.ID")
    try:
        insert_product=db.execute(query,{"product_name":product.product_name,"serial_number":product.serial_number,"id_brand":product.id_brand}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    product= ProductResponse(id=insert_product._mapping["id"],product_name=insert_product._mapping["product_name"],serial_number=insert_product._mapping["serial_number"],id_brand=insert_product._mapping["id_brand"],brand_name=insert_product._mapping["brand_name"])
    return product

@router.put("/products/{id}",response_model=ProductResponse)
def modify_product(id:int, product:ProductCreate,db: Session=Depends(get_db)):
    query=text("WITH Modify_Product as(UPDATE PRODUCT SET Product_Name = :product_name,Serial_Number = :serial_number,ID_Brand= :id_brand WHERE ID = :id_product RETURNING Product_Name,Serial_Number,ID_Brand) " \
    "SELECT Modify_Product.Product_Name,Modify_Product.Serial_Number,Modify_Product.ID_Brand,b.Brand_Name FROM Modify_Product " \
    "INNER JOIN BRAND b on Modify_Product.ID_Brand = b.ID")
    try:
        update_product=db.execute(query,{"product_name":product.product_name,"serial_number":product.serial_number,"id_brand":product.id_brand,"id_product":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if update_product is None:
            raise HTTPException(
                status_code=404,
                detail="El producto no se ha encontrado en la base de datos")
    product= ProductResponse(id=id,product_name=update_product._mapping["product_name"],serial_number=update_product._mapping["serial_number"],id_brand=update_product._mapping["id_brand"],brand_name=update_product._mapping["brand_name"])
    return product

@router.delete("/products/{id}",response_model=ProductResponse)
def delete_product(id:int,db: Session=Depends(get_db)):
    query=text("WITH Delete_Product as(DELETE FROM PRODUCT WHERE ID = :id_product RETURNING Product_Name,Serial_Number,ID_Brand) " \
    "SELECT Delete_Product.Product_Name,Delete_Product.Serial_Number,Delete_Product.ID_Brand,b.Brand_Name FROM Delete_Product " \
    "INNER JOIN BRAND b on Delete_Product.ID_Brand = b.ID")
    try:
        delete_product=db.execute(query,{"id_product":id}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if delete_product is None:
            raise HTTPException(
                status_code=404,
                detail="El producto no se ha encontrado en la base de datos")
    product= ProductResponse(id=id,product_name=delete_product._mapping["product_name"],serial_number=delete_product._mapping["serial_number"],id_brand=delete_product._mapping["id_brand"],brand_name=delete_product._mapping["brand_name"])
    return product

@router.get("/products/{id}/providers",response_model=list[ProviderResponse])
def product_provider(id:int, db: Session=Depends(get_db)): 
    query = text("Select prov.ID,prov.Provider_Name,prov.Email From PRODUCT_PROVIDER prodprov " \
    "INNER JOIN PROVIDER prov on prodprov.ID_Provider = prov.ID "\
    "WHERE prodprov.ID_Product = :id ")
    all_providers=db.execute(query,{"id": id}).fetchall()
    provider_list= []
    for row in all_providers:
        provider_list.append(ProviderResponse(id=row._mapping["id"],provider_name=row._mapping["provider_name"],email=row._mapping["email"]))
    return provider_list

@router.post("/products/{id}/providers", response_model=ProviderResponse)
def product_provider_post(id:int, provider:ProductProviderCreate, db: Session=Depends(get_db)): 
    query=text("WITH New_Provider as(INSERT INTO PRODUCT_PROVIDER (ID_Product,ID_Provider) VALUES (:id_product, :id_provider) RETURNING ID_Product,ID_Provider) " \
    "SELECT New_Provider.ID_Product,New_Provider.ID_Provider,prov.Provider_Name,prov.Email FROM New_Provider " \
    "INNER JOIN PROVIDER prov on New_Provider.ID_Provider = prov.ID")
    try:
        insert_provider=db.execute(query,{"id_product": id,"id_provider":provider.id_provider}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    provider=ProviderResponse(id=provider.id_provider,provider_name=insert_provider._mapping["provider_name"],email=insert_provider._mapping["email"])
    return provider

@router.delete("/products/{id}/providers/{id_provider}",response_model=ProviderResponse)
def delete_product_provider(id:int,id_provider:int,db: Session=Depends(get_db)):
    query=text("WITH Delete_Product_Provider as(DELETE FROM PRODUCT_PROVIDER WHERE ID_Product = :id_product AND ID_Provider = :id_provider RETURNING ID_Product,ID_Provider) " \
    "SELECT Delete_Product_Provider.ID_Provider,prov.Provider_Name,prov.Email FROM Delete_Product_Provider " \
    "INNER JOIN PROVIDER prov on Delete_Product_Provider.ID_Provider = prov.ID")
    try:
        delete_product_provider=db.execute(query,{"id_product":id,"id_provider":id_provider}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)
    if delete_product_provider is None:
            raise HTTPException(
                status_code=404,
                detail="No se ha encontrado la relación Producto-Provedor")
    provider= ProviderResponse(id=id_provider,provider_name=delete_product_provider._mapping["provider_name"],email=delete_product_provider._mapping["email"])
    return provider

@router.get("/products/{id}/files",response_model=list[ProductFileResponse])
def product_file(id:int, db: Session=Depends(get_db)): 
    query = text("Select ID,File_Type,File_Path From PRODUCT_FILE " \
    "WHERE ID_Product = :id ")
    all_files=db.execute(query,{"id": id}).fetchall()
    file_list= []
    for row in all_files:
        file_list.append(ProductFileResponse(id_product=id,id_file=row._mapping["id"],file_type=row._mapping["file_type"],file_path=row._mapping["file_path"]))
    return file_list

@router.post("/products/{id}/files",response_model=ProductFileResponse)
async def insert_file(id:int,file:UploadFile = File(...), db: Session=Depends(get_db)):
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    file_type=file.content_type
    if file_type in ALLOWED_TYPES:
        file_type = file.content_type.split("/")[1]  # "jpeg", "png", "webp"
    else:
        raise HTTPException(
                status_code=415,
                detail="Formato de foto no válido. Solo se permiten jpeg, png y webp")
    bytes_content = await file.read()
    file_path= await upload_file(bytes_content)
    query= text("INSERT INTO PRODUCT_FILE (ID_Product,File_Type,File_Path) values(:id,:file_type,:file_path) RETURNING ID,File_Type,File_Path")
    try:
        insert_new_file=db.execute(query,{"id":id,"file_type":file_type,"file_path":file_path}).fetchone()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise handle_integrity_error(e)    
    file=ProductFileResponse(id_product=id,id_file=insert_new_file._mapping["id"],file_type=file_type,file_path=file_path)
    return file

@router.delete("/products/{id}/files/{id_file}",response_model=ProductFileResponse)
def delete_file(id:int,id_file:int,db: Session=Depends(get_db)):
    query=text("DELETE FROM PRODUCT_FILE WHERE ID= :id_file AND ID_Product= :id_product RETURNING File_Type,File_Path")
    deleted_file=db.execute(query,{"id_file":id_file,"id_product":id}).fetchone()
    if deleted_file is None:
        raise HTTPException(
                    status_code=404,
                    detail="No se ha encontrado el archivo")
    db.commit()
    file_path=deleted_file._mapping["file_path"]
    delete_cloudinary_file(file_path)
    file=ProductFileResponse(id_file=id_file,id_product=id,file_path=file_path,file_type=deleted_file._mapping["file_type"])    
    return file