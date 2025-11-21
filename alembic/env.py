"""
env.py — конфігурація Alembic для управління міграціями бази даних.

Цей файл налаштовує підключення до БД, логування та метадані моделей SQLAlchemy.
Підтримуються два режими міграцій:
1. offline — генерує SQL скрипти без підключення до БД
2. online — виконує міграції безпосередньо в БД

Автор: PhotoShare Project Team
"""

from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
from app.database.models import Base
from app.conf.config import settings

# ----------------------------------------------------------------------
# Alembic Config object: доступ до параметрів у alembic.ini
# ----------------------------------------------------------------------
config = context.config

# Використовуємо URL бази даних з Pydantic Settings
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_url)

# ----------------------------------------------------------------------
# Логування Alembic
# ----------------------------------------------------------------------
if config.config_file_name is not None:
    # Налаштування логування з alembic.ini
    fileConfig(config.config_file_name)

# ----------------------------------------------------------------------
# Метадані моделей SQLAlchemy
# ----------------------------------------------------------------------
# Використовуються для автогенерації міграцій
target_metadata = Base.metadata

# ----------------------------------------------------------------------
# Режим offline
# ----------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Виконує міграції в offline-режимі:
    - Генерує SQL скрипти без підключення до БД.
    - Підтримує 'literal_binds' для вставки значень у SQL.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ----------------------------------------------------------------------
# Режим online
# ----------------------------------------------------------------------
def run_migrations_online() -> None:
    """
    Виконує міграції в online-режимі:
    - Підключається безпосередньо до бази даних.
    - Виконує команди CREATE, ALTER, DROP таблиць та колонок.
    """
    connectable = create_engine(
        settings.sqlalchemy_database_url,
        poolclass=pool.NullPool,  # Без пулінгу для короткочасного підключення
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ----------------------------------------------------------------------
# Вибір режиму виконання
# ----------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
