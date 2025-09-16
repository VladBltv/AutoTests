# Гайд

## Настройка среды разработки

### Основное

1. На компьютере должны быть установлены
   1. git https://git-scm.com/downloads
   2. python https://www.python.org/downloads/
   3. poetry https://python-poetry.org/docs/
2. Клонировать репозиторий на компьютер любым удобным способом
3. Открыть проект в IDE
4. Настроить вирутальное окружение
   1. После открытия проекта poetry предложит создать вирутальное окружение. Необходимо отказаться.
   2. Выполнить в консоли в папке проекта 
      1. python3.13 -m venv venv - создание вирутального окружения (Для Windows py -3.13 -m venv venv)
      2. source venv/bin/activate - активация вирутального окружения (для mac)
      3. venv\Scripts\activate - - активация вирутального окружения (для windows)
5. Добавить интерпретатор
    1. В правом нижнем углу IDE кликнуть на линк No intrpreter
    2. Выбрать Add New Intrpreter / Add Local Intrpreter
    3. В открывшемся попапе будет предупреждение, что Intrpreter уже создан
    4. Нажать на кнопку Select Existing Intrpreter
    5. В поле Intrpreter Path указать путь до исполняемого файла Python в вирутальном окружении проекта, например, /Users/potegovaav/Documents/repositories/shop-tests/venv/bin/python3.13
6. Установить зависимости
   1. `poetry install`
7. Создать в корне проекта обычный (не python) файл .env
   1. Скопировать туда содержимое файла для определенной среды из папки deploy
   2. **Не добавлять этот файл под контроль версий**

### Переустановка Python

Со временем требуется обновить версию python, используемую в проекте.

1. Обновить версию Python на компьютере любым удобным способом
2. Удалить вирутальное оружение в проекте командой `rm -rf venv/`
3. Выполнить шаги по настройке нового вирутального окружения, описанные выше пункты 4 и 5

### Возможные проблемы

Если при запуске тестов на mac с чипом процессора M выводится ошибка типа `mach-o file, but is an incompatible architecture (have 'x86_64', need 'arm64e' or 'arm64')`, необходимо переустановить проблемные пакеты вручную.

1. pip uninstall <packge name>
2. pip install <packge name>

**Список ранее выявленных проблемных пакетов**
1. charset_normalizer 
2. numpy 
3. pandas 
4. psycopg2-binary

### Настройка линтера и форматтера

1. Используется линтер Ruff, который будет установлен со всеми зависимостями
2. Установить в IDE плагин File Watchers
3. В плагине необходимо создать два кастомных шаблона
4. Настройка шаблонов
   5. File type - Python
   6. Scope - Project Files
   7. Programm - `$PyInterpreterDirectory$/ruff`
   8. Arguments 
      9. Для шаблона Ruff format - `format --line-length=120 $FilePath$`
      10. Для шаблона  Ruff check - `check --fix --line-length=120 $FilePath$`
   9. Output paths to refresh - `$FilePath$`
   10. Working Directory - `$ProjectFileDir$`
   11. Проставить галки
       12. Auto-save edited files to trigger the watcher
       13. Trigger the watcher on external changes
       14. Trigger the watcher regardless of syntax errors

## Разметка тестов

### Каждый логический блок кода размечаем шагами.

Пример:

    with allure.step("Описание шага"):

### Над тестом проставляем мету

Пример:

    @allure.title("Заголовок теста на русском языке")
    @allure.description("Проверяем успешное обновление данных в стикере") # описание
    @allure.label("layer", "api") # кто написал
    @allure.severity(Severity.CRITICAL) # важность
    @allure.service("Catalog") # название микросервиса 1 уровень
    @allure.suite("Listing") # название сьюта 2 уровень, крупные функциональные блоки
    @allure.feature("Stickers") # название фичи 3 уровень, отдельное поведение внутри функционального блока
    @allure.label("owner", "Potegova") # кто написал
    @allure.tag("any") # тег

## Запуск тестов

### Перед запуском тестов общее

**Отключить капчу в монолите**

В таблице core_config проставить значение для поля captcha = 0

### Перед запуском тестов для каталога по листингам

1. Обновить дамп базы https://confluence.melonfashion.ru/pages/viewpage.action?pageId=1121650223
2. Собрать ветку
3. В енве на сервере установить очереди QUEUE_CONNECTION=rabbitmq
4. Перезаполнить эластик php artisan scout:fresh --fill

### Перед запуском тестов для каталога (сonfigs)

**В енве на требуемой среде отключить кеш и очистить кеш в редисе**

CACHE_PAYMENTS_ENABLED=false

### Перед запуском тестов для ордерса

**В енве на требуемой среде отключить кеш и очистить кеш в редисе**

CACHE_STARFISH_ENABLED=false
CACHE_CATALOG_ENABLED=false
CACHE_MONITORING_ENABLED=false
CACHE_MONOLITH_ENABLED=false
CACHE_DADATA_ENABLED=false

## Meta

### Service

- Catalog
- Monolith
- Admin
- Public
- Orders

### Suite

- Listing
- Filter
- Product
- Menu
- Header
- Footer
- Content
- Cart
- Checkout
- Account
- Order
- CMS
- Common
- Main
- Service

### Layers

- api
- ui
- unit
- integrations

### Severity

- MINOR
- NORMAL
- TRIVAIL
- CRITICAL
- BLOCKER

### Tags

- dev
- prod
- regress
- app
- mobile

## Архитектура

### Стурктура папок 
- api_model 
    - cocreate 
        - private
            - users
                - api.py
                - payloads.py
                - endpoints.py
                - schemas.py
            - collaborations
                - ...
            - base_test.py
        - public
            - ...
        - db_queries
            - ...
    - catalog
        - ...
- ui_model
    - ...
- config
    - api_session
    - db_connection
    - headers
