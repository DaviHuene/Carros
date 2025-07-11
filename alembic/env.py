from logging.config import fileConfig
from core.config import settings
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from db.base_class import Base
import db.base
from alembic import context

config = context.config
config.set_main_option('sqlalchemy.url', settings.ALEMBIC_URI)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 🔒 Função para filtrar apenas as tabelas do seu projeto
def include_object(object, name, type_, reflected, compare_to):
    # Só considera tabelas que começam com os prefixos do seu projeto
    if type_ == "table" and not name.startswith(("carros", "tb_", "TB_", "Car")):
        return False
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # ← aqui está o filtro
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
