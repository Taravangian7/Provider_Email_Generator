from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from modules.db import get_db
from modules.auth import get_current_user
from backend.routers import brands,providers,products,mails,auth,google_oauth


app=FastAPI()

@app.get("/test")
def test(db: Session=Depends(get_db),user=Depends(get_current_user)): #No pasas get_db() porque sino la estarías ejecutando ahí mismo, vos le pasas la funcion a Depends y FastAPI ejecuta cuando necesita
    result=db.execute(text("Select 1")).fetchone()
    return{"db_connection":"ok","result":result[0]}

#Para cada ruteo se incluye la verificación del token. Si es inválido salta el error y no se ejecuta el endpoint
app.include_router(brands.router,dependencies=[Depends(get_current_user)])
app.include_router(providers.router,dependencies=[Depends(get_current_user)])
app.include_router(products.router,dependencies=[Depends(get_current_user)])
app.include_router(mails.router,dependencies=[Depends(get_current_user)])
app.include_router(google_oauth.router)
app.include_router(auth.router)