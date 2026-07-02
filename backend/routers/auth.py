from fastapi import Depends, APIRouter, HTTPException
from modules.auth import verify_password,create_token
from backend.models.models import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/auth/login",response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access,message=verify_password(form_data.username,form_data.password)
    if access:
        token=create_token(form_data.username)
        token=TokenResponse(access_token=token)
        return token
    else:
        raise HTTPException(status_code=401,
                            detail=message)
    

@router.get("/health")
def health():
    return {"status": "ok"}