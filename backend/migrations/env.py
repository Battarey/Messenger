import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from shared.config import settings
from shared.models import Base

# Это объект конфигурации Alembic, который предоставляет
# доступ к значениям в файле alembic.ini.
config = context.config

# Интерпретируем конфигурационный файл для логирования.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для autogenerate поддержки
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме.

    Этот режим настраивает контекст только с URL, без создания Engine.
    """
    url = settings.POSTGRES_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Запускает миграции в синхронном контексте соединения.

    Args:
        connection (Connection): Объект соединения SQLAlchemy.
    """
    # Автоматически создаем схемы, если они еще не существуют в PostgreSQL
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS users;"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS chats;"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS contacts;"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS read_models;"))
    connection.commit()

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме с асинхронным движком."""
    connectable = create_async_engine(
        settings.POSTGRES_URL,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
