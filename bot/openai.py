import logging
from textwrap import dedent
from typing import Optional

import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from bot import schemas, settings


class TextSummary(BaseModel):
    """Модель с параметрами входящего сообщения."""

    is_vacancy: bool
    position: Optional[str] = None
    languages: list[str] = Field(default_factory=list)
    grades: list[schemas.Grades] = Field(default_factory=list)

    @property
    def languages_lower(self) -> list[str]:
        return [lg.lower() for lg in self.languages if lg.lower() in schemas.Languages]


PROMPT = """
Проанализируй текст и перескажи его содержание, используя предоставленную схему.
Описание параметров схемы:
is_vacancy: является ли текст вакансией, да или нет. Обрати внимание, что если в тексте есть хэштег #резюме, 
то текст вероятно является не вакансией, а резюме соискателя.
position: название должности, описанной в вакансии. Если текст не является вакансией, укажи в этом параметре None.
languages: язык программирования, знание которого требуется, для должности, определенной выше в параметре position.
Выбери один из следующих языков: Python, Golang. Не стремись указать все языки, 
укажи лишь те, которые упоминаются в начале текста.
Если упоминания этих языков нет в тексте, не указывай их, а укажи те языки, которые, наоборот, упоминаются в тексте.
grades: уровень должности, описанной в вакансии.
Выбери из один или несколько следующих вариантов:
- junior
- middle
- senior
- techlead
Если в вакансии указана должность intern или стажер, считай что это вакансия уровня junior.
При выборе уровня должности ориентируйся не только на ключевые слова junior, middle, head, lead и т.д. но и на уровень
предлагаемой в вакансии заработной платы.
Например, если в тексте указана заработная плата 700$, это вакансия уровня junior,
так как у специалистов уровня middle, senior, techlead заработная плата обычно выше.
При этом исходи из предположения, что один и тот же уровень зарплаты может быть предложен для смежных должностей:
например, заработная плата 300 тыс. рублей может быть предложена как middle, так и senior специалисту.
Если текст является вакансией, но при этом нельзя сделать заключение об уровне должности, укажи все варианты: 
junior, middle, senior, techlead

Примеры:
    1. Пример 1:
        Текст: [**Переслано из Remote IT (Inflow)**](https://t.me/c/1141029953/10806)**
            Middle+/Senior Node JS Developer \n
            | https://telegra.ph/Middle--Senior-Node-JS-Developer-02-10 #middle #senior #NodeJS #remote #itjob
        Ответ: {
            is_vacancy: true,
            position: "Node JS Developer",
            languages: [Node JS],
            grades: [middle, senior]
        }
    2. Пример 2: 
        Текст: [**Переслано из Python Django Jobs**](https://t.me/c/1750581511/97184)**
            #resume #cv #junior #middle #python #django #fullstack #javascript #nodejs #резюме
            Занятость: полная\nЛокация: Кыргызстан \nКонтакты: @username\nОпыт работы: 3,5 года"
            Стек технологий:
            Front (Strong junior): \n   HTML \n   CSS (Bootstrap, Tailwind)\n   JavaScript (DOM)\n   React (Redux)
            Backend at python (Middle):\n    Python\n    Django (DRF, Channels, Celery, Celery-beat)
        Ответ: {
            is_vacancy: false,
            position: null,
            languages: [],
            grades: [],
        }
    3. Пример 3:
        Текст: [**Переслано из Job for Python**](https://t.me/c/1381822968/4091)**
            Team Lead** at Emerging Travel Group\n**Emerging Travel Group** is a travel technology company 
            that includes six brands: Russian Ostrovok.ru, B2B.Ostrovok, Ostrovok.ru Business trips
            and forms ZenHotels, RateHawk and Roundtrip.\n**Remote work.**\n
            **Stack:** Golang, Python (Django), PostgreSQL.\n[Job description](https://www.emergingtravel.com/career/position/3866839/)",
            **Больше вакансий для технических менеджеров:** @jobfortm"
        Ответ: {
            is_vacancy: true,
            position: [Team Lead],
            languages: [Golang, Python],
            grades [techlead],
        }
    4. Пример 4:
        Текст: [**Переслано из Remote IT (Inflow)**](https://t.me/c/1141029953/10814)**"
            "**Python developer | https://telegra.ph/Python-developer-02-13-6 #python #remote #itjob"
        Ответ: {
            is_vacancy: true,
            position: [Python developer],
            languages: [Python],
            grades: [junior, middle, senior, techlead],
        }
    5. Пример 5:
        Текст: [**Переслано из Job for Python**](https://t.me/c/1381822968/4095)**
            "**🔹**Python-разработчик**\n🔹**Python Developer (LLM)**\n
            в **2ГИС** — международная технологическая компания, которая разрабатывает 
            сервисы для комфортной жизни в городе.\n**Возможность удаленной работы или офисы 
            в Москве, Питере, Новосибирске и других городах.**\nИщет Камилла Сагитова, ее [пост на LinkedIn].",
        Ответ: {
            is_vacancy: true,
            position: Python-разработчик,
            languages: [Python],
            grades: [junior, middle, senior, techlead],
        }    
"""


class OpenAIClient:
    """OpenAI http-клиент."""

    def __init__(self, **kwargs):
        self.openai_cli = AsyncOpenAI(api_key=settings.OPENAI_KEY)
        self.model = 'gpt-4o-mini'
        super().__init__(**kwargs)

    async def ai_request(self, text: str) -> TextSummary:
        """Запрос к LLM-модели на парсинг входящего сообщения."""
        try:
            completion = await self.openai_cli.beta.chat.completions.parse(
                model=self.model,
                temperature=0.2,
                messages=[{'role': 'system', 'content': dedent(PROMPT)}, {'role': 'user', 'content': text}],
                response_format=TextSummary,
            )
            summary = completion.choices[0].message.parsed
            logging.info(f'Got text summary: {summary.model_dump()}')
            return summary
        except openai.RateLimitError as rate_err:
            logging.error(f'Got {rate_err} for {text}')
            # TODO: add email notification
        except openai.APIError as err:
            logging.error(f'Got {err} for {text}')
        summary = TextSummary(is_vacancy=False)
        logging.info(f'Got text summary: {summary.model_dump()}')
        return summary
