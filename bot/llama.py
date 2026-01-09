from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from bot import settings

Settings.embed_model = OpenAIEmbedding(model=settings.CHROMA_EMBEDDING_MODEL)
Settings.llm = OpenAI(temperature=0, model='gpt-5-nano')
Settings.chunk_size = 512
