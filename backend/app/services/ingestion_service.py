import os
import hashlib
import re
from typing import List, Dict, Any, Tuple
import pymupdf  # PyMuPDF
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.core.config import settings

class IngestionService:
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def extract_document_pages(file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Extract pages with page numbers and text"""
        ext = os.path.splitext(filename)[1].lower()
        pages = []
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            pages.append({"page_number": 1, "text": content})
        elif ext == ".pdf":
            doc = pymupdf.open(file_path)
            for idx, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages.append({"page_number": idx + 1, "text": text})
        else:
            raise ValueError(f"Unsupported file format '{ext}' for knowledge base.")
        return pages

    @staticmethod
    def clean_text(text: str) -> str:
        # Standardize whitespace and remove repetitive header/footers
        text = re.sub(r'\r\n|\r', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @classmethod
    def chunk_document(
        cls,
        pages: List[Dict[str, Any]],
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ) -> List[Dict[str, Any]]:
        """
        Chunk documents preserving paragraph boundaries and page citations.
        """
        chunks = []
        # Approximate tokens as ~4 chars per token for chunking window
        char_chunk_size = chunk_size * 4
        char_overlap = chunk_overlap * 4

        current_chunk_text = ""
        current_chunk_pages = []
        chunk_index = 0

        for page in pages:
            p_num = page["page_number"]
            clean_p = cls.clean_text(page["text"])
            paragraphs = clean_p.split("\n\n")

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if len(current_chunk_text) + len(para) < char_chunk_size:
                    current_chunk_text += ("\n\n" if current_chunk_text else "") + para
                    if p_num not in current_chunk_pages:
                        current_chunk_pages.append(p_num)
                else:
                    # Flush current chunk
                    if current_chunk_text:
                        chunks.append({
                            "chunk_index": chunk_index,
                            "text": current_chunk_text,
                            "page_number": current_chunk_pages[0] if current_chunk_pages else p_num,
                            "page_range": f"{current_chunk_pages[0]}-{current_chunk_pages[-1]}" if len(current_chunk_pages) > 1 else str(p_num)
                        })
                        chunk_index += 1

                    # Compute overlap from end of current text
                    if char_overlap > 0 and len(current_chunk_text) > char_overlap:
                        overlap_text = current_chunk_text[-char_overlap:]
                        current_chunk_text = overlap_text + "\n\n" + para
                    else:
                        current_chunk_text = para
                    current_chunk_pages = [p_num]

        if current_chunk_text:
            chunks.append({
                "chunk_index": chunk_index,
                "text": current_chunk_text,
                "page_number": current_chunk_pages[0] if current_chunk_pages else 1,
                "page_range": f"{current_chunk_pages[0]}-{current_chunk_pages[-1]}" if len(current_chunk_pages) > 1 else "1"
            })

        return chunks

    @classmethod
    def ingest_document(
        cls,
        file_path: str,
        filename: str,
        role_id: str,
        source_name: str
    ) -> Dict[str, Any]:
        file_hash = cls.calculate_file_hash(file_path)
        pages = cls.extract_document_pages(file_path, filename)
        if not pages:
            raise ValueError(f"No readable text found in document: {filename}")

        chunks = cls.chunk_document(pages)
        if not chunks:
            raise ValueError("Failed to create text chunks from document.")

        texts = [c["text"] for c in chunks]
        chunk_ids = [f"{role_id}_{file_hash[:10]}_{c['chunk_index']}" for c in chunks]
        metadatas = [
            {
                "role_id": role_id,
                "source_name": source_name,
                "filename": filename,
                "page_number": c["page_number"],
                "page_range": c["page_range"],
                "content_hash": file_hash[:16],
                "chunk_id": chunk_ids[i]
            }
            for i, c in enumerate(chunks)
        ]

        # Generate embeddings in batch
        embeddings = embedding_service.embed_batch(texts)

        # Store in ChromaDB collection for this role
        vector_store.add_chunks(
            role_id=role_id,
            chunk_ids=chunk_ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return {
            "file_hash": file_hash,
            "total_chunks": len(chunks),
            "chunk_ids": chunk_ids
        }

ingestion_service = IngestionService()

