import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from fastembed import TextEmbedding
from typing import List, Dict, Any
import uuid

class QdrantManager:
    _instance = None
    _client = None
    _embedding_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantManager, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        self._client = QdrantClient(path="data/qdrant")
        self.collection_name = "knowledge_base"

        # We initialize the model here, but keep in mind that fastembed downloads the model on first use.
        self._embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-large")

        # Ensure collection exists
        try:
            self._client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            # multilingual-e5-small has 384 dimensions
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )

    async def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Run in thread pool
        def _embed():
            return list(self._embedding_model.embed(texts))

        embeddings = await asyncio.to_thread(_embed)
        return [emb.tolist() for emb in embeddings]

    async def add_document(self, text: str, payload: Dict[str, Any] = None):
        if payload is None:
            payload = {}
        payload["text"] = text

        embeddings = await self._embed_texts([text])
        vector = embeddings[0]

        def _upsert():
            self._client.upsert(
                collection_name=self.collection_name,
                points=[
                    {
                        "id": str(uuid.uuid4()),
                        "vector": vector,
                        "payload": payload
                    }
                ]
            )
        await asyncio.to_thread(_upsert)

    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        embeddings = await self._embed_texts([query])
        vector = embeddings[0]

        def _search():
            return self._client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit
            )

        search_results = await asyncio.to_thread(_search)
        return [hit.payload for hit in search_results]

qdrant_manager = QdrantManager()
