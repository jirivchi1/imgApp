# app/__init__.py

from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Flask Configuration
    app.config.update(
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"),
        MONGODB_URI=os.getenv("MONGODB_URI"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
    )

    # Initialize Celery
    from .tasks import make_celery

    celery = make_celery(app)

    # Register Blueprints
    from .routes import main_bp

    app.register_blueprint(main_bp)

    return app


# Initialize the app
app = create_app()
