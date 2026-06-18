#Modulo para subir los archivos a Cloudinary
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def upload_file(file:bytes) -> str: #En FastAPI este bytes sera UploadFile
    #Valido la extensión del file en el endpoint
    response=cloudinary.uploader.upload(file)
    file_path=response["secure_url"]
    return file_path

def delete_cloudinary_file(file_path: str):
    try:
        public_id = file_path.split("/")[-1].split(".")[0]
        cloudinary.uploader.destroy(public_id)
    except:
        pass
