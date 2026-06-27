import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context
from app import create_app  # <-- ДОБАВЛЯЕМ ИМПОРТ

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# ИСПРАВЛЯЕМ: получаем URL через контекст приложения
def get_engine_url():
    app = create_app()
    with app.app_context():
        return current_app.config['SQLALCHEMY_DATABASE_URI']

# ИСПРАВЛЯЕМ: получаем metadata через контекст приложения
def get_metadata():
    app = create_app()
    with app.app_context():
        return current_app.extensions['migrate'].db.metadata

# Устанавливаем URL для Alembic
config.set_main_option('sqlalchemy.url', get_engine_url())
target_metadata = get_metadata()

def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    app = create_app()
    with app.app_context():
        connectable = current_app.extensions['migrate'].db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                process_revision_directives=process_revision_directives
            )
            with context.begin_transaction():
                context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()