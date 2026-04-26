import requests
import json
import os

def ask_solaria_master(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "solaria-master",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    return response.json().get('response', 'No response field')

# Leer el código base
with open("/home/esfingex/workspace/scrapnews/main.py", "r") as f:
    base_code = f.read()

prompt = "Hola, dime 'OK' si me escuchas."

print(ask_solaria_master(prompt))
