"""HTTP-клиент для API hh.ru."""

import logging
from typing import Any, Optional

import httpx

from bot import settings


class HHClient:
    """HTTP-клиент для работы с API hh.ru."""

    BASE_URL = 'https://api.hh.ru'

    def __init__(
        self,
        base_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """Инициализация клиента.

        Args:
            base_url: Базовый URL API (по умолчанию https://api.hh.ru)
            user_agent: User-Agent заголовок (обязателен для API hh.ru)
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url or settings.HH_BASE_URL
        self.user_agent = user_agent or settings.HH_USER_AGENT
        self.timeout = timeout
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={'User-Agent': self.user_agent},
        )

    async def __aenter__(self) -> 'HHClient':
        """Асинхронный контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Асинхронный контекстный менеджер - выход."""
        await self.close()

    async def close(self) -> None:
        """Закрытие HTTP-клиента."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Выполнение HTTP-запроса.

        Args:
            method: HTTP-метод (GET, POST, PUT, DELETE и т.д.)
            endpoint: Эндпоинт API (например, '/vacancies')
            params: Query-параметры
            json: JSON-тело запроса
            headers: Дополнительные заголовки

        Returns:
            Ответ API в виде словаря

        Raises:
            httpx.HTTPStatusError: При ошибке HTTP-статуса
            httpx.RequestError: При ошибке запроса
        """
        request_headers = dict(headers) if headers else {}
        # Гарантируем, что User-Agent всегда присутствует
        request_headers['User-Agent'] = self.user_agent
        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f'HTTP error {e.response.status_code} for {method} {endpoint}: {e.response.text}')
            raise
        except httpx.RequestError as e:
            logging.error(f'Request error for {method} {endpoint}: {e}')
            raise

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """GET-запрос.

        Args:
            endpoint: Эндпоинт API
            params: Query-параметры
            headers: Дополнительные заголовки

        Returns:
            Ответ API в виде словаря
        """
        return await self._request('GET', endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """POST-запрос.

        Args:
            endpoint: Эндпоинт API
            json: JSON-тело запроса
            params: Query-параметры
            headers: Дополнительные заголовки

        Returns:
            Ответ API в виде словаря
        """
        return await self._request('POST', endpoint, json=json, params=params, headers=headers)

    async def put(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """PUT-запрос.

        Args:
            endpoint: Эндпоинт API
            json: JSON-тело запроса
            params: Query-параметры
            headers: Дополнительные заголовки

        Returns:
            Ответ API в виде словаря
        """
        return await self._request('PUT', endpoint, json=json, params=params, headers=headers)

    async def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """DELETE-запрос.

        Args:
            endpoint: Эндпоинт API
            params: Query-параметры
            headers: Дополнительные заголовки

        Returns:
            Ответ API в виде словаря
        """
        return await self._request('DELETE', endpoint, params=params, headers=headers)
