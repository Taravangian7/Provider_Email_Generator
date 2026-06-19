from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,Depends

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")#Permite verificar contraseña hasheada
def verify_password(username,plain_password) -> bool:
    hashed_password=os.getenv("USER_PASSWORD")
    user=os.getenv("USER_USERNAME")
    if user==username:
        if pwd_context.verify(plain_password,hashed_password):
            return (True,"Loggin exitoso")
        else:
            return (False,"Contraseña incorrecta")
    else:
        return (False,"No se encuentra el usuario")
    
def create_token(username):
    payload={"sub": username, "exp": datetime.now(timezone.utc)+ timedelta(hours=8)}
    secret=os.getenv("SECRET_KEY")
    token=jwt.encode(payload,secret,"HS256")
    return token
    
def verify_token(token)->bool:
    secret=os.getenv("SECRET_KEY")
    try:
        payload=jwt.decode(token=token,key=secret,algorithms=["HS256"])
        return payload["sub"] #Devuelve el nombre de usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

#esta función va a ejecutarse cada vez que se llama a un endpoint. Busca en el header el token y verifica que sea válido.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")#TokenUrl es para que desde /docs fastAPI sepa donde mandar las credenciales cuando te queres autenticar(y de donde obtener el token)
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)