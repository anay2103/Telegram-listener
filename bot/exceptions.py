"""Обработчик исключений."""

import functools
import logging
from asyncio.exceptions import TimeoutError
from typing import Any, Callable

from pydantic import ValidationError
from telethon.events import common


def exception_handler(func: Callable) -> Callable:
    """Декоратор для хэндлеров сообщений, обрабатывающий исключения."""

    @functools.wraps(func)
    async def wrapper(event: common.EventCommon) -> Any:
        if not isinstance(event, common.EventCommon):
            raise ValueError('Event parameter must be a subclass of telethon.events.common.EventCommon')
        try:
            res = await func(event)
        except ValidationError:
            await event.respond(f'Недопустимое значение для {event.message.text}')
        except TimeoutError as t_err:
            logging.info(t_err, exc_info=True)
            await event.respond('Недождался ответа...:( Попробуйте заново.')
        except Exception as err:
            await event.respond('Упс...Кажется у нас авария. Все починим!')
            logging.error(err, exc_info=True)
        else:
            return res

    return wrapper
