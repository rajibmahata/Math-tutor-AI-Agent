"""RAG Service — Curriculum knowledge base with Qdrant vector search."""

import uuid
import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation for curriculum-aligned responses."""

    EMBEDDING_MODEL = "text-embedding-3-small"
    VECTOR_SIZE = 1536  # text-embedding-3-small → 1536 dimensions
    COLLECTION_NAME = "curriculum"
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    TOP_K = 5
    SIMILARITY_THRESHOLD = 0.7

    def __init__(self):
        self._qdrant: Optional[QdrantClient] = None
        self._openai: Optional[AsyncOpenAI] = None

    @property
    def qdrant(self) -> QdrantClient:
        if not self._qdrant:
            kwargs = {"host": settings.qdrant_host, "port": settings.qdrant_port}
            if settings.qdrant_api_key:
                kwargs["api_key"] = settings.qdrant_api_key
            self._qdrant = QdrantClient(**kwargs)
        return self._qdrant

    @property
    def openai(self) -> AsyncOpenAI:
        if not self._openai:
            self._openai = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai

    async def initialize(self):
        """Initialize Qdrant collection if it doesn't exist."""
        try:
            collections = self.qdrant.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)

            if not exists:
                self.qdrant.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")

    # =========================================================================
    # Ingestion
    # =========================================================================

    async def ingest_document(
        self,
        title: str,
        content: str,
        grade: str,
        language: str,
        topic_id: Optional[str] = None,
        source: str = "ncert",
        content_type: str = "textbook",
    ) -> int:
        """Ingest a curriculum document into Qdrant. Returns chunk count."""
        await self.initialize()

        chunks = self._chunk_text(content, self.CHUNK_SIZE, self.CHUNK_OVERLAP)
        if not chunks:
            return 0

        embeddings = await self._generate_embeddings(chunks)

        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = uuid.uuid4()
            points.append(PointStruct(
                id=str(point_id),
                vector=embedding,
                payload={
                    "title": title,
                    "text": chunk,
                    "grade": grade,
                    "language": language,
                    "topic_id": topic_id or "",
                    "source": source,
                    "content_type": content_type,
                    "chunk_index": i,
                },
            ))

        # Batch upsert
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.qdrant.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch,
            )

        logger.info(f"Ingested {len(chunks)} chunks from '{title}'")
        return len(chunks)

    async def ingest_curriculum_batch(
        self,
        documents: list[dict],
    ) -> int:
        """Ingest multiple curriculum documents. Returns total chunks."""
        total = 0
        for doc in documents:
            chunks = await self.ingest_document(
                title=doc.get("title", "Untitled"),
                content=doc["content"],
                grade=doc.get("grade", "1"),
                language=doc.get("language", "en"),
                topic_id=doc.get("topic_id"),
                source=doc.get("source", "ncert"),
                content_type=doc.get("content_type", "textbook"),
            )
            total += chunks
        return total

    # =========================================================================
    # Retrieval
    # =========================================================================

    async def retrieve(
        self,
        query: str,
        grade: Optional[str] = None,
        language: str = "en",
        topic_id: Optional[str] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> list[dict]:
        """Search the curriculum knowledge base."""
        await self.initialize()

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Build filter
        must_conditions = []
        if grade:
            must_conditions.append(FieldCondition(
                key="grade", match=MatchValue(value=grade)
            ))
        if language:
            must_conditions.append(FieldCondition(
                key="language", match=MatchValue(value=language)
            ))

        qdrant_filter = Filter(must=must_conditions) if must_conditions else None

        # Search
        results = self.qdrant.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
            score_threshold=similarity_threshold,
        )

        return [
            {
                "text": hit.payload.get("text", ""),
                "title": hit.payload.get("title", ""),
                "grade": hit.payload.get("grade", ""),
                "language": hit.payload.get("language", ""),
                "topic_id": hit.payload.get("topic_id", ""),
                "source": hit.payload.get("source", ""),
                "score": hit.score,
            }
            for hit in results
        ]

    async def enrich_prompt(
        self,
        base_prompt: str,
        query: str,
        grade: str,
        language: str = "en",
    ) -> str:
        """Enrich a prompt with relevant curriculum context."""
        chunks = await self.retrieve(
            query=query,
            grade=grade,
            language=language,
            top_k=3,
        )

        if not chunks:
            return base_prompt

        context_text = "\n\n---\n\n".join([
            f"[Source: {chunk['source']}, Grade {chunk['grade']}]: {chunk['text']}"
            for chunk in chunks
        ])

        return f"""{base_prompt}

## RELEVANT CURRICULUM CONTEXT

The following is from the official curriculum for Grade {grade}:

{context_text}

Use this curriculum context to ensure your teaching is accurate and aligned with what the student is expected to learn.
"""

    # =========================================================================
    # Embedding
    # =========================================================================

    async def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = await self.openai.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=texts,
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self._generate_embeddings([text])
        return embeddings[0]

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks at natural boundaries."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break

            # Try to break at paragraph, then sentence, then word boundary
            chunk = text[start:end]
            # Prefer paragraph breaks
            para_break = chunk.rfind("\n\n")
            if para_break > chunk_size // 2:
                end = start + para_break
            else:
                # Try sentence break
                for punct in [". ", "? ", "! ", "\n"]:
                    sent_break = chunk.rfind(punct)
                    if sent_break > chunk_size // 2:
                        end = start + sent_break + 1
                        break

            chunks.append(text[start:end].strip())
            start = max(start + 1, end - overlap)

        return chunks


# Singleton
rag_service = RAGService()
