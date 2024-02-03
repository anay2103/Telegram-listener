import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

BOT_NAME = os.getenv('BOT_NAME')
BOT_TOKEN = os.getenv('BOT_TOKEN')

CLIENT_SESSION = os.getenv('CLIENT_SESSION')
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
    return 'redis://%s:%s' % (
        os.getenv('REDIS_HOST', 'localhost'),
        os.getenv('REDIS_PORT', '6379')
    )
