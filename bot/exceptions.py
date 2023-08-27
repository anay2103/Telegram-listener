"""Обработчик исключений."""
import asyncio
import functools
import logging
from asyncio.exceptions import TimeoutError
from typing import Any, Callable

from asyncpg.exceptions import UniqueViolationError
from pydantic import ValidationError
from telethon.errors import FloodWaitError
from telethon.events import common

logger = logging.getLogger(__name__)


def exception_handler(func: Callable) -> Callable:
    """Декоратор для хэндлеров сообщений, обрабатывающий исключения."""
    @functools.wraps(func)
    async def wrapper(event: common.EventCommon) -> Any:
        if not isinstance(event, common.EventCommon):
            raise ValueError('Event parameter must be a subclass of telethon.events.common.EventCommon')
        sender = await event.get_sender()
        try:
            res = await func(event)
        except ValidationError:
            await event.respond(f'Недопустимое значение для {event.message.text}')
        except TimeoutError:
            await event.client.set_state(sender.id, None)   # сбрасываем state пользователя
            await event.respond('Недождался ответа...:( Попробуйте заново.')
        except UniqueViolationError:
            await event.client.set_state(sender.id, None)   # сбрасываем state пользователя
            await event.respond(f'Такое слово уже добавлено: {event.message.data}')
        except FloodWaitError as err:
            logger.error(f'Sleeping for {err.seconds} on flood wait')
            await asyncio.sleep(err.seconds)
        except Exception:
            await event.client.set_state(sender.id, None)   # сбрасываем state пользователя
            await event.respond('Упс...Кажется у нас авария. Все починим!')
            raise
        else:
            return res
    return wrapper
