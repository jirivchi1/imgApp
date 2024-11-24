from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Configuración de Flask
    app.config.update(
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"),
        MONGODB_URI=os.getenv("MONGODB_URI"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
    )

    # Inicializar extensiones, rutas, etc.
    with app.app_context():
        from . import routes

    return app


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_app()
celery = make_celery(app)
