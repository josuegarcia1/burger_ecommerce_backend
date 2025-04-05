from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            is_google_auth=False
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def add_pending_operation(self, operation: dict):
        # Implementar según tu sistema de operaciones pendientes
        pass