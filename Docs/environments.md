# Переменные окружения

Все микросервисы используют подход **Config via Environment** для управления конфигурацией. Для сбора и валидации настроек используется библиотека `pydantic-settings`.

## Группы конфигурационных параметров

### 1. Системные переменные (System / Gateway)
Используются для конфигурации хоста, портов и общих настроек запуска.
* `ENV` — режим окружения (`development`, `testing`, `production`).
* `LOG_LEVEL` — уровень логирования (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

### 2. База данных PostgreSQL (Database Settings)
Настройки для подключения сервисов к PostgreSQL.
* `POSTGRES_HOST` — адрес сервера
* `POSTGRES_PORT` — порт сервера
* `POSTGRES_USER` — имя пользователя
* `POSTGRES_PASSWORD` — пароль
* `POSTGRES_DB` — имя базы данных
* `POSTGRES_URL` — URL для подключения

### 3. База данных Redis (Cache & Broker Settings)
Параметры подключения к Redis (Pub/Sub, присутствие, кэш сессий, очереди arq).
* `REDIS_HOST` — адрес хоста Redis
* `REDIS_PORT` — порт
* `REDIS_PASSWORD` — пароль
* `REDIS_URL` — URL для подключения

### 4. Аутентификация и безопасность (Auth Settings)
Секреты для работы с JWT-токенами.
* `JWT_SECRET_KEY` — секретный ключ для подписи токенов.
* `JWT_ALGORITHM` — алгоритм подписи токенов (например, `HS256`).
* `ACCESS_TOKEN_EXPIRE_MINUTES` — время жизни Access-токена в минутах.
* `REFRESH_TOKEN_EXPIRE_DAYS` — время жизни Refresh-токена в днях.
