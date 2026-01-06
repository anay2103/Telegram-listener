from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

from bot import settings

Settings.embed_model = OpenAIEmbedding(model=settings.CHROMA_EMBEDDING_MODEL)
