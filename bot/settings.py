import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

BOT_NAME = os.getenv('BOT_NAME')
BOT_TOKEN = os.getenv('BOT_TOKEN')

CLIENT_SESSION = os.getenv('CLIENT_SESSION')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
CHROMA_HOST = os.getenv('CHROMA_HOST', 'localhost')
CHROMA_PORT = os.getenv('CHROMA_PORT', 8000)
CHROMA_COLLECTION = os.getenv('CHROMA_COLLECTION', 'bot_vacancies')
CHROMA_EMBEDDING_MODEL = os.getenv('CHROMA_EMBEDDING_MODEL', 'text-embedding-3-large')

HH_BASE_URL = os.getenv('HH_BASE_URL', 'https://api.hh.ru/')
HH_USER_AGENT = os.getenv('HH_USER_AGENT')


# количество отправляемых ботом сообщений в секунду
MESSAGE_RATE_LIMIT = 20
# период sleep после получения FloodWaitError
FLOOD_WAIT_THRESHOLD = 15 * 60


def build_postgres_uri():
    return 'postgresql+asyncpg://%s:%s@%s:%s/%s' % (
        os.getenv('POSTGRES_USER', 'myuser'),
        os.getenv('POSTGRES_PASSWORD', 'myuser'),
        os.getenv('POSTGRES_HOST', 'localhost'),
        os.getenv('POSTGRES_PORT', '5432'),
        os.getenv('POSTGRES_DB', 'bot'),
    )


def build_redis_uri():
    return 'redis://%s:%s/%s' % (
        os.getenv('REDIS_HOST', 'localhost'),
        os.getenv('REDIS_PORT', '6379'),
        os.getenv('REDIS_DB', '0'),
    )
