import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db.init_db import init_db
from app.api.endpoints import api_router

# Ensure directory paths exist
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs(settings.KNOWLEDGE_BASE_DIR, exist_ok=True)

# Create Database tables
Base.metadata.create_all(bind=engine)

# Initialize seed data
with SessionLocal() as db:
    init_db(db)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent AI-Powered Role-Based Candidate Screening System with Grounded RAG Architecture.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to TalentLens AI Backend",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

