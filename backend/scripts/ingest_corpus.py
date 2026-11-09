import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.db.init_db import init_db
from app.models.entities import Role, KnowledgeDocument
from app.services.ingestion_service import ingestion_service
from app.core.config import settings

def ingest_directory(role_id: str, directory_path: str):
    # Ensure tables created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            print(f"Error: Role '{role_id}' not found in database.")
            return

        if not os.path.exists(directory_path):
            print(f"Directory '{directory_path}' does not exist.")
            return

        files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.pdf', '.txt'))]
        if not files:
            print(f"No PDF or TXT files found in '{directory_path}'.")
            return

        print(f"\n=======================================================")
        print(f"Starting Knowledge Ingestion for Role: {role.name} ({role_id})")
        print(f"Found {len(files)} document(s) in {directory_path}")
        print(f"=======================================================\n")

        for filename in files:
            file_path = os.path.join(directory_path, filename)
            source_name = os.path.splitext(filename)[0].replace("_", " ")
            file_hash = ingestion_service.calculate_file_hash(file_path)

            # Check existing
            existing = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.role_id == role_id,
                KnowledgeDocument.file_hash == file_hash
            ).first()

            if existing and existing.ingestion_status == "indexed":
                print(f"[SKIP] '{filename}' is already indexed with {existing.total_chunks} chunks.")
                continue

            print(f"[INGESTING] '{filename}' (Source: {source_name})...")
            try:
                res = ingestion_service.ingest_document(
                    file_path=file_path,
                    filename=filename,
                    role_id=role_id,
                    source_name=source_name
                )

                if existing:
                    existing.total_chunks = res["total_chunks"]
                    existing.ingestion_status = "indexed"
                else:
                    new_doc = KnowledgeDocument(
                        role_id=role_id,
                        filename=filename,
                        source_name=source_name,
                        file_hash=file_hash,
                        ingestion_status="indexed",
                        total_chunks=res["total_chunks"]
                    )
                    db.add(new_doc)
                db.commit()
                print(f"[SUCCESS] '{filename}' successfully ingested -> {res['total_chunks']} chunks stored in ChromaDB.")
            except Exception as e:
                print(f"[FAILED] Error ingesting '{filename}': {e}")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest role knowledge documents into ChromaDB.")
    parser.add_argument("--role", required=False, default="all", choices=["all", "ai_ml_engineer", "data_science", "backend_engineer"], help="Role ID or 'all'")
    parser.add_argument("--dir", required=False, help="Directory containing PDFs or TXTs (defaults to role folder)")
    args = parser.parse_args()

    roles_to_ingest = ["ai_ml_engineer", "backend_engineer", "data_science"] if args.role == "all" else [args.role]
    for r in roles_to_ingest:
        target_dir = args.dir if (args.dir and args.role != "all") else os.path.join(settings.KNOWLEDGE_BASE_DIR, r)
        ingest_directory(r, target_dir)
