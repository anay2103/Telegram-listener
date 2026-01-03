"""Сервис для работы с API hh.ru."""

from bot.hh.client import HHClient
from bot.hh.schemas import Document, VacancyDetailResponse, VacancyListResponse


class HHService:
    """Сервис для работы с вакансиями hh.ru."""

    def __init__(self, client: HHClient) -> None:
        """Инициализация сервиса.

        Args:
            client: HTTP-клиент для работы с API hh.ru
        """
        self.client = client

    async def get_vacancies(
        self,
        text: str = 'python developer',
        period: int = 2,
        professional_role: int = 96,
        page: int = 0,
        per_page: int = 100,
    ) -> VacancyListResponse:
        """Получение списка вакансий.

        Args:
            text: Текст для поиска вакансий
            period: Период поиска в днях
            professional_role: ID профессиональной роли
            page: Номер страницы (начиная с 0)
            per_page: Количество вакансий на странице

        Returns:
            Ответ API со списком вакансий
        """
        response = await self.client.get(
            '/vacancies',
            params={
                'text': text,
                'period': period,
                'professional_role': professional_role,
                'page': page,
                'per_page': per_page,
            },
        )
        return VacancyListResponse(**response)

    async def get_vacancy_detail(self, vacancy_id: str) -> Document:
        """Получение детальной информации о вакансии.

        Args:
            vacancy_id: ID вакансии

        Returns:
            Ответ API с детальной информацией о вакансии
        """
        response = await self.client.get(f'/vacancies/{vacancy_id}')
        return VacancyDetailResponse.from_source(response)
