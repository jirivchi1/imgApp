from .celery_app import celery
from flask import current_app
from datetime import datetime
import os
import requests
from pymongo import MongoClient
from openai import OpenAI


@celery.task()
def generate_image_task(prompt, username):
    # Obtener configuración desde current_app
    mongodb_uri = current_app.config["MONGODB_URI"]
    openai_api_key = current_app.config["OPENAI_API_KEY"]

    # Conectar a MongoDB
    mongo_client = MongoClient(mongodb_uri)
    db = mongo_client["image_generation"]
    user_prompts = db["prompts"]

    # Configurar el cliente de OpenAI
    client = OpenAI(api_key=openai_api_key)

    # Llamada a la API para generar la imagen
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    # Extraer la URL de la imagen
    image_url = response.data[0].url

    # Descargar la imagen
    image_data = requests.get(image_url).content

    # Guardar la imagen en static/images/
    image_filename = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    image_path = os.path.join(current_app.static_folder, "images", image_filename)
    with open(image_path, "wb") as file:
        file.write(image_data)

    # Actualizar el documento en MongoDB
    user_prompts.update_one(
        {"username": username, "prompt": prompt},
        {"$set": {"image_filename": image_filename, "status": "completed"}},
    )

    return image_filename
