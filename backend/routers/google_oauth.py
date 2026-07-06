from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from modules.db import get_db
from modules.auth import get_current_user
from modules.google_oauth import get_authorization_url, exchange_code_for_tokens
import os

router = APIRouter(prefix="/google", tags=["google"])

@router.get("/authorize")
def authorize():
    url = get_authorization_url()
    return {"auth_url": url}

@router.get("/callback")
def callback(code: str, state: str, db: Session = Depends(get_db)):
    try:
        tokens = exchange_code_for_tokens(code, state)
        refresh_token = tokens["refresh_token"]
        email = tokens["email"]

        if not refresh_token:
            raise HTTPException(status_code=400, detail="No se pudo obtener el refresh token")

        # Verificar si ya existe un token para ese email
        existing = db.execute(
            text("SELECT id FROM GOOGLE_TOKEN WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing:
            # Actualizar el token existente
            db.execute(
                text("UPDATE GOOGLE_TOKEN SET refresh_token = :token WHERE email = :email"),
                {"token": refresh_token, "email": email}
            )
        else:
            # Insertar nuevo token
            db.execute(
                text("INSERT INTO GOOGLE_TOKEN (refresh_token, email) VALUES (:token, :email)"),
                {"token": refresh_token, "email": email}
            )

        db.commit()
        # Redirigir al frontend una vez autorizado
        return RedirectResponse(url=os.getenv("FRONTEND_URL", "http://localhost:8501"))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en callback: {str(e)}")

#Si encuentra registro en la tabla de GOOGLE_TOKEN, al ser UNICO USUARIO, se entiende conectado.
@router.get("/status", dependencies=[Depends(get_current_user)])
def get_status(db: Session = Depends(get_db)):
    token = db.execute(
        text("SELECT email FROM GOOGLE_TOKEN LIMIT 1")
    ).fetchone()
    if token:
        return {"connected": True, "email": token._mapping["email"]}
    return {"connected": False, "email": None}

#Borra el usuario. Al ser UNICO USUARIO borro toda la tabla.
@router.delete("/disconnect", dependencies=[Depends(get_current_user)])
def disconnect(db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM GOOGLE_TOKEN"))
    db.commit()
    return {"disconnected": True}