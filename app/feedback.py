import os
import json

FEEDBACK_FILE = "data/processed/feedback.json"
os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)

def cargar_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_feedback(feedback):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2)

def registrar_interaccion(nombre_vector, tipo):
    feedback = cargar_feedback()
    if nombre_vector not in feedback:
        feedback[nombre_vector] = {"likes": 0, "dislikes": 0, "clics": 0, "estrellas": []}

    if tipo == "like":
        feedback[nombre_vector]["likes"] += 1
    elif tipo == "dislike":
        feedback[nombre_vector]["dislikes"] += 1
    elif tipo == "clic":
        feedback[nombre_vector]["clics"] += 1

    guardar_feedback(feedback)

def eliminar_interaccion(nombre_vector, tipo):
    feedback = cargar_feedback()
    if nombre_vector not in feedback:
        return
    if tipo == "like" and feedback[nombre_vector]["likes"] > 0:
        feedback[nombre_vector]["likes"] -= 1
    elif tipo == "dislike" and feedback[nombre_vector]["dislikes"] > 0:
        feedback[nombre_vector]["dislikes"] -= 1
    guardar_feedback(feedback)

def registrar_estrellas(nombre_vector, estrellas):
    feedback = cargar_feedback()
    if nombre_vector not in feedback:
        feedback[nombre_vector] = {"likes": 0, "dislikes": 0, "clics": 0, "estrellas": []}

    feedback[nombre_vector]["estrellas"].append(estrellas)
    guardar_feedback(feedback)

def obtener_feedback(nombre_vector):
    feedback = cargar_feedback().get(nombre_vector, {})
    estrellas = feedback.get("estrellas", [])
    promedio = round(sum(estrellas) / len(estrellas), 1) if estrellas else None
    return {
        "likes": feedback.get("likes", 0),
        "dislikes": feedback.get("dislikes", 0),
        "clics": feedback.get("clics", 0),
        "promedio_estrellas": promedio,
        "num_estrellas": len(estrellas)
    }