from fastapi import FastAPI
from app.api.main import api_router
from app.core.config import settings
from app.db.session import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)