"""Тесты функции UserRepository._make_query."""
import pytest

from bot import models, schemas
from bot.crud import UserRepository


@pytest.mark.parametrize(
    'keywords, expected',
    [
        (
            [models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.optional)], 'python'
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='backend', mode=schemas.KeywordModes.optional),
            ],
            'backend & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='backend', mode=schemas.KeywordModes.optional),
            ],
            'backend | python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='backend', mode=schemas.KeywordModes.binding),
            ],
            'backend & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.negative),
                models.Keyword(user_id=1, name='backend', mode=schemas.KeywordModes.negative),
            ],
            '!backend & !python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
            ],
            'middle & python | junior & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.negative),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
            ],
            'middle & !junior & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
            ],
            'middle & junior & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
            ],
            'middle | junior | python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='cv', mode=schemas.KeywordModes.negative),
            ],
            'middle & !cv & python | junior & !cv & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='cv', mode=schemas.KeywordModes.optional),
            ],
            'cv & python | middle & python | junior & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='cv', mode=schemas.KeywordModes.optional),
            ],
            'cv & junior & python | middle & junior & python',
        ),
        (
            [
                models.Keyword(user_id=1, name='python', mode=schemas.KeywordModes.binding),
                models.Keyword(user_id=1, name='junior', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='middle', mode=schemas.KeywordModes.optional),
                models.Keyword(user_id=1, name='cv', mode=schemas.KeywordModes.negative),
                models.Keyword(user_id=1, name='data science', mode=schemas.KeywordModes.negative),
            ],
            "middle & !'data science' & !cv & python | junior & !'data science' & !cv & python",
        )
    ]
)
async def test_make_query(keywords, expected):
    assert (await UserRepository._make_query(keywords)) == expected
