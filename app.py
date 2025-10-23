from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

URL = "https://www.uniquindio.edu.co/actividades-por-subcategoria/4/consulta/"

def extraer_fechas_importantes():
    """
    Hace scraping a la página de actividades académicas
    y devuelve una lista con fechas y eventos relevantes.
    """
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    eventos = []
    # Buscar bloques que contengan texto tipo "fecha" o "actividad"
    for item in soup.find_all('div', class_=re.compile("evento|actividad|card|item", re.IGNORECASE)):
        texto = item.get_text(separator=" ", strip=True)
        # Buscar fechas en formato común (por ejemplo: 10 de octubre, 23/11/2025, etc.)
        fechas = re.findall(r'\d{1,2}\s+de\s+\w+|\d{1,2}/\d{1,2}/\d{2,4}', texto, re.IGNORECASE)
        if fechas:
            eventos.append({
                "evento": texto[:120] + "..." if len(texto) > 120 else texto,
                "fechas": fechas
            })

    return eventos

@app.route("/", methods=["GET"])
def home():
    return "Webhook activo para Dialogflow ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")

    if intent.lower() in ["fechas importantes", "consultar fechas", "fechas universidad"]:
        eventos = extraer_fechas_importantes()
        if not eventos:
            respuesta = "No encontré fechas importantes en este momento en el sitio web de la universidad."
        else:
            respuesta = "📅 Fechas importantes de la Universidad del Quindío:\n\n"
            for e in eventos[:5]:  # limitar a 5 eventos
                fechas = ", ".join(e["fechas"])
                respuesta += f"- {e['evento']} ({fechas})\n\n"
    else:
        respuesta = "No tengo información sobre ese tema."

    return jsonify({
        "fulfillmentText": respuesta
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
