## Telegram Listener

Приложение для работы Телеграмом на основе библиотеки [Telethon](https://github.com/LonamiWebs/Telethon)

Запускает 2 Телеграм-клиента: бота и клиента с номером телефона.
Через меню бота можно:
- задать чаты для поиска по ключевым словам (доступно только пользователям с правами админа) 
- сохранять и редактировать поисковые запросы в чатах (для всех пользователей).

Клиент слушает заданные чаты и пересылает сообщения тем пользоватям, чей поисковый запрос найден во входящем сообщении.

Для поиска по словам используется полнотекстовый поиск Postgres.

Проект развернут, бота [@word_catcher_bot](https://t.me/word_catcher_bot) можно потестить в Телеграме. 

### Как использовать

Предположим, нужно отслеживать ИТ-вакансии для начинающих разработчиков, публикуемые в Телеграмм-каналах. Пользователь бота может задать 2 ключевых слова: `PYTHON` и `JUNIOR`. Регистр значения не имеет.

Меню бота позволяет указать слова, которые не должны встречаться в сообщении.

Также возможно указать поисковый запрос с оператором `OR`. Например, если интересуют сообщения, содержащие `JUNIOR` или `MIDDLE`.

### Запуск

Необходимо заполнить переменные среды из файла `env.example`.
Создание строковой сессии для реального клиента см. [здесь](https://docs.telethon.dev/en/stable/concepts/sessions.html#string-sessions)

Далее стандартно:

    docker-compose up
