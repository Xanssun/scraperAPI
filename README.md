# scraperAPI

API и асинхронный скрапер для [books.toscrape.com](https://books.toscrape.com).

Проект собирает книги из каталога, сохраняет их в Postgres и отдает данные через FastAPI. Скрапинг запускается через HTTP endpoint, а сама работа выполняется в фоне через Taskiq + NATS JetStream.

## Стек

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0 async
- Alembic
- PostgreSQL 18
- aiohttp
- BeautifulSoup4
- Taskiq + taskiq-nats
- Dishka
- uv

## Архитектура

Проект разложен в стиле hexagonal architecture. Внутри находится application-слой с use cases, портами и сервисами, а внешние детали подключаются вокруг него через адаптеры: HTTP API, Postgres, внешний сайт `books.toscrape.com` и Taskiq/NATS.

Главная идея: бизнес-сценарии не зависят напрямую от FastAPI, aiohttp, SQLAlchemy engine или Taskiq. Use case работает с портами и gateway, а конкретная инфраструктура подставляется через DI.

```text
src/
├── application/          # use cases, application services, results, ports
├── database/psql/        # SQLAlchemy models, repositories, DBGateway, migrations support
├── infrastructure/       # outbound adapters: HTTP provider and external clients
├── presentation/http/    # inbound HTTP adapter: routers, contracts, middlewares
├── tasks/                # background tasks, Taskiq broker and producer
├── entrypoints/          # composition roots for HTTP app and task worker
├── settings/             # typed application settings
└── common/               # shared small utilities and DI markers
```

Что лежит в основных папках:

- `application/common/interfaces` — порты, через которые use cases говорят с внешним миром. Например `BooksToScrapeClient` и `ScrapeTaskProducer`.
- `application/v1/usecases` — бизнес-сценарии: получить книги, получить категории, запустить скрапинг, посмотреть scrape runs.
- `application/v1/services` — application services. `BooksToScrapeService` берет raw HTML от клиента и превращает его в application result.
- `application/v1/results` — внутренние DTO, которые use cases возвращают наружу.
- `database/psql/models` — ORM-модели таблиц.
- `database/psql/repositories` — тонкий слой работы с БД. Репозитории не решают бизнес-логику, а только выполняют `create/select/update/delete/select_many`.
- `infrastructure/http/provider` — общий async HTTP provider на aiohttp, middleware для ошибок, retry и логирования.
- `infrastructure/http/clients` — клиенты внешних HTTP API. Сейчас это `BooksToScrapeAPI`.
- `presentation/http/v1` — FastAPI endpoints и Pydantic contracts для входящих/исходящих HTTP-данных.
- `tasks` — Taskiq-задачи и producer, который ставит задачи в NATS.
- `entrypoints` — точки сборки приложения: HTTP-процесс и worker-процесс используют общий DI container.

## Быстрый Старт

Создайте `.env` из примера:

```bash
cp .env.example .env
```

Поднимите весь стек:

```bash
make docker-up
```

Команда поднимает:

- `postgres`
- `nats`
- `migrate`
- `http`
- `worker`

Миграции применяются автоматически сервисом `migrate`:

HTTP API будет доступно по адресу:

```text
http://localhost:8080
```

Swagger:

```text
http://localhost:8080/docs
```

## Локальный Запуск

Установить зависимости:

```bash
make install
```

Поднять инфраструктуру для разработки:

```bash
make docker-dev-up
```

Применить миграции:

```bash
make upgrade
```

Запустить HTTP API:

```bash
make run-http
```

В отдельном терминале запустить worker:

```bash
make run-worker
```

## API

Основные ручки:

```text
GET  /v1/books
GET  /v1/books/{book_uuid}
GET  /v1/categories
POST /v1/scrape
GET  /v1/scrape/runs
GET  /v1/scrape/runs/{scrape_run_uuid}
```

Пример запуска скрапинга одной страницы:

```bash
curl -X POST http://localhost:8080/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"start_page": 1, "end_page": 1, "concurrency": 10}'
```

Пример поиска книг:

```bash
curl "http://localhost:8080/v1/books?rating=5&limit=10"
```

## Тесты И Проверки

Запустить все тесты:

```bash
make test
```

Запустить по уровням:

```bash
make test-unit
make test-integration
make test-e2e
```

Статические проверки:

```bash
make check
```

В проекте есть три обязательных теста:

- unit: парсер книги на сохраненной HTML-фикстуре;
- integration: повторное сохранение книги с тем же UPC не создает дубль и обновляет данные;
- e2e: `GET /v1/books` с фильтром через FastAPI + реальную тестовую Postgres.

CI настроен в `.github/workflows/ci.yml`: на push и pull request запускаются `make check` и `make test`.

## Решения

Hexagonal architecture выбрана, чтобы отделить бизнес-сценарии от способов запуска и внешней инфраструктуры. Один и тот же application-слой используется HTTP endpoint-ами, task worker-ом и тестами.

Скрапер ходит по страницам каталога `1..50`. Для каждой страницы он берет ссылки на карточки книг и затем параллельно загружает карточки. Параллелизм ограничен параметром `concurrency`, максимум 10. Сетевые ошибки и ответы `5xx` ретраятся middleware-слоем HTTP provider-а с backoff, `4xx` не ретраятся.

HTML парсится через BeautifulSoup4. Для этого сайта это проще и прозрачнее, чем тащить headless browser: контент статический, данные лежат в обычной HTML-разметке, JavaScript не нужен.

Внешний HTTP API разделен на Client и Service. `BooksToScrapeAPI` находится в infrastructure-слое и возвращает raw response DTO с HTML. `BooksToScrapeService` находится в application-слое и превращает HTML в application results.

Роутеры FastAPI находятся в presentation-слое и не работают с БД напрямую. Они собирают request DTO, отправляют их в `RequestBus` и мапят application results в HTTP contracts.

Книги и категории лежат в отдельных таблицах. Запуски скрапинга хранятся в `scrape_run`: время старта, время завершения, статус, количество обработанных, созданных, обновленных записей и ошибок.

Пагинация в API offset-based. Для каталога на тысячу книг это достаточное и понятное решение.

Фоновый запуск сделан через Taskiq + NATS. Endpoint `POST /v1/scrape` быстро создает запись запуска и кладет задачу в очередь, поэтому HTTP-запрос не висит до окончания сбора.

Если приложение упадет во время сбора, уже закоммиченные книги останутся в БД, а текущий `scrape_run` может остаться в статусе `running`. Автоматическое помечание протухших запусков как `failed` пока не реализовано.

## Что Сделано Из Дополнительного

- CI с `ruff`, `mypy` и тестами.

## Что Не Сделано

- Инкрементальный сбор: сейчас карточка книги перезапрашивается при каждом запуске.
- Протухший запуск: `running` старше N минут пока автоматически не переводится в `failed`.
- Rate limit на `POST /v1/scrape`.
- JSON-логи: request_id есть в access logs, но renderer сейчас console-style, не JSON.

## Время

Фактически ушло около 12 часов. Больше всего времени заняли архитектурная раскладка слоев, фоновый запуск через Taskiq/NATS, DI-сборка и доведение тестового окружения с Postgres/testcontainers.
