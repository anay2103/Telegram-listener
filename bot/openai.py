import logging
from typing import Optional
from textwrap import dedent

import openai
from openai import AsyncOpenAI

from pydantic import BaseModel, Field
from bot import settings, schemas


class TextSummary(BaseModel):
    """Модель с параметрами входящего сообщения."""

    is_vacancy: bool
    position: Optional[str] = None
    language: list[schemas.Languages] = Field(default_factory=list)
    grade: list[schemas.Grades] = Field(default_factory=list)


PROMPT = '''
Проанализируй текст и перескажи его содержание, используя предоставленную схему.
Описание параметров схемы:
is_vacancy: является ли текст вакансией, да или нет
position: название должности, описанной в вакансии. Если текст не является вакансией, укажи в этом параметре None.
language: язык программирования, знание которого требуется, для должности, определенной выше в параметре position.
Выбери один из следующих языков: Python, Golang.
Если знание ни одного из указанных языков не требуется, оставь в этом параметре пустой список.
grade: уровень должности, описанной в вакансии.
Выбери из один или несколько следующих вариантов:
- junior
- middle
- senior
- techlead
При выборе уровня должности ориентируйся не только на ключевые слова junior, middle, head, lead и т.д. но и на уровень
предлагаемой в вакансии заработной платы.
Например, если в тексте указана заработная плата 700$, это вакансия уровня junior,
так как у специалистов уровня middle, senior, techlead заработная плата обычно выше.
Если текст является вакансией, но при этом нельзя сделать заключение об уровне должности, укажи все варианты.
Если текст не является вакансией, оставь в этом параметре пустой список.
'''


class OpenAIClient:
    """OpenAI http-клиент."""

    def __init__(self, **kwargs):
        self.openai_cli = AsyncOpenAI(api_key=settings.OPENAI_KEY)
        self.model = "gpt-4o-mini"
        super().__init__(**kwargs)

    async def ai_request(self, text: str) -> TextSummary:
        """Запрос к LLM-модели на парсинг входящего сообщения."""
        try:
            completion = await self.openai_cli.beta.chat.completions.parse(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": dedent(PROMPT)},
                    {"role": "user", "content": text}
                ],
                response_format=TextSummary,
            )
            summary = completion.choices[0].message.parsed
            logging.debug(f"Got text summary: {summary.model_dump()}")
            return summary
        except openai.RateLimitError as rate_err:
            logging.error(f"Got {rate_err} for {text}")
            # TODO: add email notification
        except openai.APIError as err:
            logging.error(f"Got {err} for {text}")
        summary = TextSummary(is_vacancy=False)
        logging.debug(f"Got text summary: {summary.model_dump()}")
        return summary
