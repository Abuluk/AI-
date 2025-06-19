from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine
from db.base import Base
from api.api_v1 import api_router

def create_tables():
    Base.metadata.create_all(bind=engine)

def include_router(app):
    app.include_router(api_router, prefix="/api/v1")

def start_application():
    app = FastAPI(title="Goofish API", version="1.0.0")
    # create_tables()  # Only run this manually during development or use Alembic for migrations
    include_router(app)
    return app

app = start_application()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """
    Root endpoint that confirms the Goofish API is running.
    """
    return {"message": "Goofish API is running"}