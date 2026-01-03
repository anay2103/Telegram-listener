import chromadb
from chromadb.api import ClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from bot import settings

API_KEY_ENV_VAR = 'OPENAI_API_KEY'


def get_client() -> ClientAPI:
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    client.heartbeat()
    return client


def get_chromadb_collection() -> chromadb.Collection:
    client = get_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=OpenAIEmbeddingFunction(  # type: ignore
            model_name=settings.CHROMA_EMBEDDING_MODEL,
            api_key_env_var=API_KEY_ENV_VAR,
        ),
    )
