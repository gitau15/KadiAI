from sentence_transformers import SentenceTransformer

from app.core.config import settings


class Embedder:
    def __init__(self):
        if settings.use_local_embedding:
            self._model = SentenceTransformer(settings.local_embedding_model)
        else:
            from zhipuai import ZhipuAI
            self._client = ZhipuAI(api_key=settings.zhipu_api_key)
            self._model_name = settings.embedding_model

    async def embed(self, text: str) -> list[float]:
        if settings.use_local_embedding:
            embedding = self._model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        else:
            response = self._client.embeddings.create(
                model=self._model_name,
                input=text,
            )
            return response.data[0].embedding
