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

@app.on_event("startup")
def on_startup():
    print("[STARTUP] Pre-warming SentenceTransformers embedding model...")
    try:
        from app.services.embedding_service import embedding_service
        embedding_service._get_model()
        print("[STARTUP] Embedding model pre-warmed and ready.")
    except Exception as e:
        print(f"[STARTUP WARNING] Could not pre-warm embedding model: {e}")

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

# Serve Frontend Static Build in Production (if present)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return None
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to TalentLens AI Backend",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health"
        }

