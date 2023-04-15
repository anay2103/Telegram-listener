"""Обработчик исключений."""
import functools
from asyncio.exceptions import TimeoutError
from typing import Any, Callable

from asyncpg.exceptions import UniqueViolationError
from telethon.events import common
from pydantic.error_wrappers import ValidationError


def bot_exceptions(func: Callable) -> Callable:
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
        except Exception:
            await event.client.set_state(sender.id, None)   # сбрасываем state пользователя
            await event.respond('Упс...Кажется у нас авария. Все починим!')
            raise
        else:
            return res
    return wrapper
