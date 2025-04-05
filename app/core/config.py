from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Burger Ecommerce API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./burger_ecommerce.db"
    
    # Auth
    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_REGION: str = "us-east-1"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()