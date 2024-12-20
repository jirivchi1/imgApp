from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .tasks import generate_image_task
import random
import string
from pymongo import MongoClient
from datetime import datetime

# Definir el Blueprint
main_bp = Blueprint("main", __name__)


@main_bp.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if not prompt:
            return "Por favor, proporciona un prompt", 400

        # Generar un nombre de usuario aleatorio
        username = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        # Guardar en MongoDB con estado "pending"
        mongodb_uri = current_app.config["MONGODB_URI"]
        mongo_client = MongoClient(mongodb_uri)
        db = mongo_client["image_generation"]
        user_prompts = db["prompts"]
        document = {
            "username": username,
            "prompt": prompt,
            "timestamp": datetime.now(),
            "status": "pending",
        }
        user_prompts.insert_one(document)

        # Encolar la tarea de Celery
        generate_image_task.delay(prompt, username)

        return redirect(url_for("main.visualization"))
    return render_template("submit.html")


@main_bp.route("/visualization")
def visualization():
    # Conectar a MongoDB
    mongodb_uri = current_app.config["MONGODB_URI"]
    mongo_client = MongoClient(mongodb_uri)
    db = mongo_client["image_generation"]
    user_prompts = db["prompts"]

    # Obtener todos los documentos
    images = user_prompts.find()

    return render_template("visualization.html", images=images)
