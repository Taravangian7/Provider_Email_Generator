from pydantic import BaseModel,Field,EmailStr
from typing import Optional
from datetime import datetime

class BrandCreate(BaseModel):
    brand_name:str = Field(...,min_length=1,description="Nombre de la Marca")

class BrandResponse(BaseModel):
    id:int = Field(...,description="ID de la Marca")
    brand_name:str = Field(...,min_length=1,description="Nombre de la Marca")

class ProductCreate(BaseModel):
    product_name:str = Field(...,min_length=1,description="Nombre del Producto")
    serial_number:str = Field(...,min_length=1,description="Serial del Producto")
    id_brand:int = Field(...,description="ID de la Marca")

class ProductResponse(BaseModel):
    id:int = Field(...,description="ID del Producto")
    product_name:str = Field(...,min_length=1,description="Nombre del Producto")
    serial_number:str = Field(...,min_length=1,description="Serial del Producto")
    id_brand:int = Field(...,description="ID de la Marca")
    brand_name: str = Field(...,description="Nombre de la Marca")

class ProviderCreate(BaseModel):
    provider_name:str = Field(...,min_length=1,description="Nombre del Proveedor")
    email:EmailStr = Field(...,description="Email del Proveedor")

class ProviderResponse(BaseModel):
    id:int = Field(...,description="ID del Proveedor")
    provider_name:str = Field(...,min_length=1,description="Nombre del Proveedor")
    email:EmailStr = Field(...,description="Email del Proveedor")

class TemplateCreate(BaseModel):
    template_name:str = Field(...,min_length=1,description="Nombre del Template")
    template_body: Optional[str] = Field(None, description="Plantilla")

class TemplateResponse(BaseModel):
    id_template:int = Field(...,description="ID del Template")
    id_provider:int = Field(...,description="ID del Proveedor")
    template_name:str = Field(...,min_length=1,description="Nombre del Template")
    template_body: Optional[str] = Field(None, description="Plantilla")

class ProductProviderCreate(BaseModel):
    id_provider: int = Field(...,description="ID del Proveedor")

class ProductFileResponse(BaseModel):
    id_product:int = Field(...,description="ID del Producto")
    id_file:int = Field(...,description="ID del Archivo")
    file_type:str = Field(...,min_length=1,description="Tipo de Archivo")
    file_path:str = Field(...,min_length=1,description="Path del archivo")

class SentCreate(BaseModel):
    id_product:int = Field(...,description="ID del Producto")
    id_provider:int = Field(...,description="ID del Proveedor")
    invoice :Optional[str] = Field(None, description="Facturas")
    case_type :str = Field(...,min_length=1,description="Caso Stock o Cliente")
    body_content:str = Field(...,min_length=1,description="Contenido del Mail")
    subject:str= Field(...,min_length=1,description="Asunto del Mail")

class SentResponse(BaseModel):
    id_sent:int = Field(...,description="ID del Mensaje")
    sent_at: datetime = Field(..., description="Fecha y hora del envío")

class MailPreviewCreate(BaseModel):
    id_product:int = Field(...,description="ID del Producto")
    id_provider:int = Field(...,description="ID del Proveedor")
    id_template:int = Field(...,description="ID del Template")
    invoice :Optional[str] = Field(None, description="Facturas")
    case_type :str = Field(...,min_length=1,description="Caso Stock o Cliente")
    file_ids:Optional[list[int]] = Field(None,description="IDs de fotos seleccionadas")

class MailPreviewResponse(BaseModel):
    id_product:int = Field(...,description="ID del Producto")
    id_provider:int = Field(...,description="ID del Proveedor")
    invoice :Optional[str] = Field(None, description="Facturas")
    case_type :str = Field(...,min_length=1,description="Caso Stock o Cliente")
    body_content:str = Field(...,min_length=1,description="Contenido del Mail")
    image_urls: Optional[list[str]] = Field(None, description="URLs de fotos seleccionadas")
    subject: str = Field(..., description="Asunto del mail")
    to_email: str = Field(..., description="Email del destinatario")

class SentHistoryResponse(BaseModel):
    id_sent:int = Field(...,description="ID de mail")
    sent_at:datetime = Field(...,description="Fecha de envío")
    subject: str = Field(...,description="Asunto del mail")
    product_name:str = Field(...,description="Nombre del producto")
    provider_name:str = Field(...,description="Nombre del proveedor")
    email_provider: EmailStr = Field(...,description="Email del proveedor")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"