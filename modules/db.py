from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL") #Cargo mi url de conexión
engine = create_engine(DATABASE_URL) #Creo standard de comunicación con postgre
SessionLocal = sessionmaker(bind=engine) #Establece una session en postgre

def get_db():
    db = SessionLocal() #Abre la session establecida anteriormente
    try:
        yield db #get_db() abre y entrega la session (con el yield), pero la función no continúa hasta que el endpoint que la llamó termine de ejecutarse
    finally:
        db.close() #Cierra la session, pase lo que pase
