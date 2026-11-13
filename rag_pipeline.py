"""
PaperMate AI - RAG Pipeline Module
Handles PDF extraction (PyPDF), recursive chunking, Google Generative AI embeddings,
ChromaDB vector indexing, and conditional intent-based retrieval.
"""

import os
import io
import re
from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Flexible ChromaDB import for maximum environment compatibility
try:
    from langchain_chroma import Chroma
except (ImportError, Exception):
    try:
        from langchain_community.vectorstores import Chroma
    except (ImportError, Exception):
        Chroma = None


class RAGPipeline:
    """
    End-to-end Agentic RAG pipeline managing PDF ingestion, chunking,
    embedding generation, ChromaDB vector indexing, and conditional retrieval.
    """

    def __init__(
        self,
        api_key: str,
        embedding_model: str = "models/text-embedding-004",
        chunk_size: int = 1000,
        chunk_overlap: int = 150
    ):
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize Google Generative AI Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.embedding_model,
            google_api_key=self.api_key
        )

        # Vector store reference and document metadata
        self.vector_store: Optional[Any] = None
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.paper_metadata: Dict[str, Any] = {}

    def extract_text_from_pdf(self, pdf_file: Any, filename: str = "document.pdf") -> Tuple[str, Dict[str, Any]]:
        """
        Extracts raw text and metadata from an uploaded PDF file or file buffer using PyPDF.
        """
        try:
            if isinstance(pdf_file, (str, bytes)):
                stream = io.BytesIO(pdf_file) if isinstance(pdf_file, bytes) else open(pdf_file, "rb")
            else:
                # Streamlit UploadedFile object or file-like object
                stream = pdf_file

            reader = PdfReader(stream)
            num_pages = len(reader.pages)
            extracted_pages: List[str] = []

            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                # Clean up excessive whitespace while preserving paragraphs
                cleaned_text = re.sub(r"[ \t]+", " ", page_text).strip()
                extracted_pages.append(cleaned_text)

            full_text = "\n\n".join(extracted_pages)
            word_count = len(full_text.split())
            char_count = len(full_text)

            metadata = {
                "filename": filename,
                "total_pages": num_pages,
                "word_count": word_count,
                "char_count": char_count,
                "extracted_pages": extracted_pages
            }
            self.paper_metadata = metadata
            return full_text, metadata

        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF '{filename}': {str(e)}")

    def process_and_index_pdf(self, pdf_file: Any, filename: str = "research_paper.pdf") -> Dict[str, Any]:
        """
        Executes the full RAG pipeline:
        1. Extract text and pages via PyPDF.
        2. Chunk text with RecursiveCharacterTextSplitter.
        3. Index chunk embeddings into ChromaDB vector store.
        """
        full_text, metadata = self.extract_text_from_pdf(pdf_file, filename)

        if not full_text.strip():
            raise ValueError(
                "The uploaded PDF contains no extractable text. "
                "It may be a scanned image or protected PDF."
            )

        # Build Document objects per page to maintain citation metadata
        raw_documents: List[Document] = []
        for page_idx, page_text in enumerate(metadata["extracted_pages"]):
            if page_text.strip():
                raw_documents.append(
                    Document(
                        page_content=page_text,
                        metadata={
                            "source": filename,
                            "page": page_idx + 1,
                            "total_pages": metadata["total_pages"]
                        }
                    )
                )

        self.documents = raw_documents

        # Split documents into semantic chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.chunks = splitter.split_documents(raw_documents)

        # Add chunk ID tracking
        for idx, chunk in enumerate(self.chunks):
            chunk.metadata["chunk_id"] = idx

        # Index chunks in ChromaDB
        self._index_in_chroma(self.chunks, collection_name=re.sub(r"[^a-zA-Z0-9_-]", "_", filename)[:40])

        metadata["chunk_count"] = len(self.chunks)
        self.paper_metadata = metadata
        return metadata

    def _index_in_chroma(self, chunks: List[Document], collection_name: str = "paper_collection"):
        """
        Creates or refreshes a ChromaDB vector store for the paper chunks.
        Provides a seamless in-memory fallback if Chroma encounters native SQLite issues.
        """
        try:
            if Chroma is not None:
                # Use in-memory Chroma instance for clean session isolation
                self.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    collection_name=collection_name
                )
            else:
                self.vector_store = FallbackInMemoryVectorStore(chunks, self.embeddings)
        except Exception as e:
            # Fallback gracefully to ensure continuous reliability
            self.vector_store = FallbackInMemoryVectorStore(chunks, self.embeddings)

    def retrieve_context(
        self,
        query: str,
        k: int = 5,
        intent: Optional[str] = None
    ) -> Tuple[str, List[Document]]:
        """
        Agentic Conditional Retrieval:
        Tailors retrieval query formulation and chunk selection based on agent intent.
        """
        if not self.chunks:
            return "No document has been loaded or indexed yet.", []

        # Conditional retrieval query tuning
        effective_query = self._format_conditional_query(query, intent)

        retrieved_docs: List[Document] = []

        if self.vector_store is not None:
            try:
                retrieved_docs = self.vector_store.similarity_search(effective_query, k=k)
            except Exception:
                # Fallback to simple keyword/heuristic search if similarity fails
                retrieved_docs = self._heuristic_search(effective_query, k=k)
        else:
            retrieved_docs = self._heuristic_search(effective_query, k=k)

        # Format retrieved context string with page citations
        formatted_context = self.format_retrieved_docs(retrieved_docs)
        return formatted_context, retrieved_docs

    def _format_conditional_query(self, query: str, intent: Optional[str]) -> str:
        """
        Augments the raw search query conditionally depending on the active agent intent.
        """
        if not intent:
            return query

        intent = intent.lower()
        if intent == "summary":
            return (
                f"{query} abstract introduction problem statement methodology "
                f"key findings results limitations conclusion"
            )
        elif intent == "concepts":
            return (
                f"{query} theoretical concepts algorithms mathematical formulations "
                f"methods technologies datasets contributions"
            )
        elif intent == "slides":
            return (
                f"{query} overview motivation proposed approach system architecture "
                f"experimental results limitations key takeaways"
            )
        elif intent == "viva":
            return (
                f"{query} methodology theoretical assumptions baseline comparisons "
                f"ablation experiments failure modes limitations defense"
            )
        elif intent == "explainer":
            return f"detailed explanation definition intuition mechanism: {query}"

        return query

    def _heuristic_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Lightweight fallback retrieval mechanism when vector similarity is unavailable.
        Uses token overlap matching across chunks.
        """
        keywords = set(re.findall(r"\w+", query.lower()))
        scored_chunks: List[Tuple[float, Document]] = []

        for chunk in self.chunks:
            chunk_words = set(re.findall(r"\w+", chunk.page_content.lower()))
            overlap = len(keywords.intersection(chunk_words))
            scored_chunks.append((overlap, chunk))

        # Sort descending by token overlap
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_chunks[:k]]

    @staticmethod
    def format_retrieved_docs(docs: List[Document]) -> str:
        """
        Formats a list of Document chunks into a clean, readable context string
        with page citations and chunk identifiers.
        """
        if not docs:
            return "No relevant context found in the paper."

        formatted_blocks = []
        for i, doc in enumerate(docs, 1):
            page_num = doc.metadata.get("page", "Unknown")
            source = doc.metadata.get("source", "Document")
            content = doc.page_content.strip()
            block = f"--- [Source: {source} | Page: {page_num} | Chunk #{i}] ---\n{content}"
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)


class FallbackInMemoryVectorStore:
    """
    Lightweight, robust fallback vector store using cosine similarity
    for environments where ChromaDB binary extensions cannot load.
    Ensures zero crashes under any Windows environment.
    """

    def __init__(self, documents: List[Document], embeddings: Any):
        self.documents = documents
        self.embeddings = embeddings
        self._doc_embeddings: Optional[List[List[float]]] = None

    def _ensure_embedded(self):
        if self._doc_embeddings is None:
            texts = [doc.page_content for doc in self.documents]
            try:
                self._doc_embeddings = self.embeddings.embed_documents(texts)
            except Exception:
                self._doc_embeddings = [[0.0] * 768 for _ in texts]

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        try:
            self._ensure_embedded()
            query_embedding = self.embeddings.embed_query(query)

            import numpy as np
            q_vec = np.array(query_embedding, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                q_norm = 1.0

            scores = []
            for idx, doc_vec in enumerate(self._doc_embeddings or []):
                d_vec = np.array(doc_vec, dtype=np.float32)
                d_norm = np.linalg.norm(d_vec)
                if d_norm == 0:
                    d_norm = 1.0
                cosine_sim = float(np.dot(q_vec, d_vec) / (q_norm * d_norm))
                scores.append((cosine_sim, self.documents[idx]))

            scores.sort(key=lambda x: x[0], reverse=True)
            return [doc for score, doc in scores[:k]]
        except Exception:
            # Fallback to text matching
            keywords = set(re.findall(r"\w+", query.lower()))
            scored = []
            for doc in self.documents:
                words = set(re.findall(r"\w+", doc.page_content.lower()))
                scored.append((len(keywords.intersection(words)), doc))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [doc for score, doc in scored[:k]]
