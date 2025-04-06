from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.security import create_access_token, get_password_hash
from app.db.session import get_db
from app.schemas.user import UserCreate, UserInDB, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    return await service.register_user(user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/google", response_model=Token)
async def login_google(token: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = await service.authenticate_google(token)
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}