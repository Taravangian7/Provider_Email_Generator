from fastapi import FastAPI, Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from modules.db import get_db
from backend.routers import brands,providers,products,mails

app=FastAPI()

@app.get("/test")
def test(db: Session=Depends(get_db)): #No pasas get_db() porque sino la estarías ejecutando ahí mismo, vos le pasas la funcion a Depends y FastAPI ejecuta cuando necesita
    result=db.execute(text("Select 1")).fetchone()
    return{"db_connection":"ok","result":result[0]}

app.include_router(brands.router)
app.include_router(providers.router)
app.include_router(products.router)
app.include_router(mails.router)