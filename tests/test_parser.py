from typing import Callable

import pytest

from bot import client, schemas


@pytest.fixture
def text1(request) -> str:
    return """
    Python разработчик**

    **Чем предстоит заниматься:**
    - Проектированием архитектуры сервисов, API;
    """


@pytest.fixture
def text2(request) -> str:
    return r"""
    Разработчик Python (RuPost)**

    **Ожидания от кандидата:**
    - Опыт работы с GNU\Linux дистрибутивами
    """


@pytest.fixture
def text3(request) -> str:
    return """
    Программист Python (Middle)

    **[__Neovox Technology](http://neovoxtech.ru/)____ ИТ-компания, \
    специализирующаяся на разработке индивидуального программного обеспечения, роботизации бизнес-процессов
    """


@pytest.fixture
def text4(request) -> str:
    return """
    Программист Python**

    __EasyByte
    Специализируется на разработке скриптов автоматизации, программировании и настройке CRM-систем.
    """


@pytest.fixture
def text5(request) -> str:
    return """
    Python-разработчик**

    **Обязанности:**

·      Разработка сервиса на Python (доработка существующего функционала и разработка нового).
    """


@pytest.fixture
def text6(request) -> str:
    return """
    **Python Backend Developer**
    в **Phygital+** — No-code AI инструмент для создания визуального контента для креаторов.
    """


@pytest.fixture
def text7(request) -> str:
    return """
    Backend Python developer**

    __modesco
    Компания молодых, активных и позитивных людей, объединённых целью сделать интернет лучше.
    """


@pytest.fixture
def text8(request) -> str:
    return """
    **❓ Как разместить вакансию в канале @ru_pythonjobs?
    Пришлите мне @ultranoise текст вакансии Python разработчика, укажите в тексте адрес обратной связи.
    """


@pytest.fixture
def text9(request) -> str:
    return """
    **Middle Python Developer**
    в **Kaspi.kz** — казахстанская финтех компания-разработчик мобильного приложения для платежей и переводов
    """


@pytest.fixture
def text10(request) -> str:
    return """
    Lead Data Engineer
    **#гибрид #lead #200k
    **Локация**: Екатеринбург, Омск, Челябинск
    """


@pytest.fixture
def text11(request) -> str:
    return """
    Python Tech Lead**

    **Чем предстоит заниматься:**
    В качестве разработчика:
    - Дорабатывать и улучшать наш продукт
    """


@pytest.mark.parametrize(
    'text_name',
    [
        'text1', 'text2', 'text3', 'text4', 'text5', 'text6', 'text7', pytest.param('text8', marks=pytest.mark.xfail),
        'text9',  pytest.param('text10', marks=pytest.mark.xfail), pytest.param('text11', marks=pytest.mark.xfail),
    ])
async def test_middle_no_grade_ok_true(
    tgclient: client.Client,
    make_user: Callable,
    text_name: str,
    request: pytest.FixtureRequest,
) -> None:
    text = request.getfixturevalue(text_name)
    user = await make_user(grade=schemas.Grades.MIDDLE.name, no_grade_ok=True)
    recipients = await tgclient.process(text)
    assert list(recipients)[0].id == user.id


@pytest.mark.parametrize(
    'text_name',
    [
        'text1', 'text2', pytest.param('text3', marks=pytest.mark.xfail), 'text4', 'text5', 'text6', 'text7', 'text8',
        pytest.param('text9', marks=pytest.mark.xfail), 'text10', 'text11'
    ]
)
async def test_middle_no_grade_ok_false_without_grade(
    tgclient: client.Client,
    make_user: Callable,
    text_name: str,
    request: pytest.FixtureRequest,
) -> None:
    text = request.getfixturevalue(text_name)
    await make_user(grade=schemas.Grades.MIDDLE.name, no_grade_ok=False)
    recipients = await tgclient.process(text)
    assert recipients == set()


@pytest.mark.parametrize(
    'text_name',
    [
        'text1', 'text2', pytest.param('text3', marks=pytest.mark.xfail), 'text4', 'text5', 'text6', 'text7',
        pytest.param('text8', marks=pytest.mark.xfail), pytest.param('text9', marks=pytest.mark.xfail),
        pytest.param('text10', marks=pytest.mark.xfail), pytest.param('text11', marks=pytest.mark.xfail),
    ]
)
async def test_junior_no_grade_ok_true(
    tgclient: client.Client,
    make_user: Callable,
    text_name: str,
    request: pytest.FixtureRequest,
) -> None:
    text = request.getfixturevalue(text_name)
    user = await make_user(grade=schemas.Grades.JUNIOR.name, no_grade_ok=True)
    recipients = await tgclient.process(text)
    assert list(recipients)[0].id == user.id


@pytest.mark.parametrize(
    'text_name',
    ['text1', 'text2', 'text3', 'text4', 'text5', 'text6', 'text7', 'text8', 'text9', 'text10', 'text11']
)
async def test_junior_no_grade_ok_false(
    tgclient: client.Client,
    make_user: Callable,
    text_name: str,
    request: pytest.FixtureRequest,
) -> None:
    text = request.getfixturevalue(text_name)
    await make_user(grade=schemas.Grades.JUNIOR.name, no_grade_ok=False)
    recipients = await tgclient.process(text)
    assert recipients == set()
