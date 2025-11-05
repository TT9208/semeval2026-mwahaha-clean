import pandas as pd
import requests
import os
from dotenv import load_dotenv

# 1️⃣ Cargar las variables de entorno (API Key)
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# 2️⃣ Configurar el modelo
MODEL = "meta-llama/llama-4-maverick:free"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 3️⃣ Leer dataset (solo 5 filas para prueba)
df = pd.read_csv("data/raw/task-a-en.tsv", sep="\t", nrows=5)

# 4️⃣ Función para generar un chiste Zero-Shot
def generate_joke(prompt):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a creative comedian AI participating in SemEval 2026 Task 1: Humor Generation."},
            {"role": "user", "content": f"Generate a short, funny joke based on this headline or constraint: {prompt}"}
        ],
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers=HEADERS, json=data)
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return "⚠️ No joke generated (parsing error)"
    else:
        return f"⚠️ API error: {response.status_code}"

# 5️⃣ Generar chistes
jokes = []
for _, row in df.iterrows():
    prompt = row["headline"] if "headline" in row else "Random humor"
    joke = generate_joke(prompt)
    jokes.append({"id": row["id"], "generated_text": joke})
    print(f"✅ Generated for {row['id']}: {joke}\n")

# 6️⃣ Guardar resultados
out_df = pd.DataFrame(jokes)
out_df.to_csv("outputs/jokes_dev.csv", index=False)
print("\n🎉 Chistes generados guardados en outputs/jokes_dev.csv")
