# src/generate_jokes.py
import os
import csv
import time
import json
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_joke(constraint_type, input1, input2=None, lang="en"):
    if constraint_type == "word_inclusion":
        prompt = f"Write a short, funny joke in {lang} that includes the words '{input1}' and '{input2}'."
    elif constraint_type == "headline":
        prompt = f"Write a short, funny joke in {lang} inspired by this news headline: '{input1}'."
    else:
        prompt = f"Write a short, creative, funny joke in {lang}."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers=headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        # parse response robustamente
        text = data.get("choices", [{}])[0].get("message", {}).get("content")
        if text is None:
            # fallback: buscar otros caminos en JSON
            text = str(data)
        return text.strip()
    except Exception as e:
        print("⚠️ Error:", e)
        return "[Error generating joke]"

def main(args):
    input_path = args.input
    output_path = args.output
    limit = args.limit

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        results = []
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            joke = generate_joke(constraint_type=row.get("constraint_type",""),
                                 input1=row.get("input_1",""),
                                 input2=row.get("input_2",""))
            results.append({"id": row.get("id", str(i+1)), "generated_text": joke})
            print(f"✅ Generated {row.get('id', i+1)}")
            time.sleep(1)  # respeta rate-limits

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id","generated_text"])
        writer.writeheader()
        writer.writerows(results)

    print(f"🎉 Saved {len(results)} jokes to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/task-a-en.tsv")
    parser.add_argument("--output", default="outputs/jokes_dev.csv")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of rows (0 = all)")
    args = parser.parse_args()
    main(args)
