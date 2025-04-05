from fastapi import HTTPException, status
from app.db.repositories.auth import AuthRepository
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash, verify_password
from app.utils.aws_client import AWSClient

class AuthService:
    def __init__(self, db):
        self.repo = AuthRepository(db)
        self.aws_client = AWSClient()

    async def register_user(self, user_create: UserCreate):
        existing_user = self.repo.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_create.password)
        db_user = UserInDB(
            **user_create.dict(),
            hashed_password=hashed_password
        )
        
        created_user = self.repo.create_user(db_user)
        
        try:
            if await self.aws_client.is_online():
                await self.aws_client.create_user(created_user)
        except Exception as e:
            self.repo.add_pending_operation({
                'type': 'create_user',
                'data': created_user.dict()
            })
        
        return created_user

    async def authenticate_user(self, email: str, password: str):
        user = self.repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def authenticate_google(self, token: str):
        google_user = await self.aws_client.verify_google_token(token)
        if not google_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        user = self.repo.get_user_by_email(google_user.email)
        if not user:
            user = self.repo.create_user(UserInDB(
                email=google_user.email,
                full_name=google_user.full_name,
                is_google_auth=True
            ))
            
            try:
                if await self.aws_client.is_online():
                    await self.aws_client.create_user(user)
            except Exception:
                self.repo.add_pending_operation({
                    'type': 'create_user',
                    'data': user.dict()
                })
        
        return user