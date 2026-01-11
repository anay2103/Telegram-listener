import asyncio

from celery import Task


class AsyncTask(Task):
    """Awaitable task."""

    def __call__(self, *args, **kwargs):
        asyncio.run(super().__call__(*args, **kwargs))
