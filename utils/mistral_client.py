import json
import os
from hashlib import md5
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

CACHE_DIR = Path("data/mistral_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    return _client

def cache_key(prompt):
    return md5(prompt.encode()).hexdigest()

def ask(prompt, fallback="No response"):
    key = cache_key(prompt)
    file = CACHE_DIR / f"{key}.json"

    if file.exists():
        return json.loads(file.read_text())["response"]

    try:
        res = get_client().chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        text = res.choices[0].message.content

        file.write_text(json.dumps({"response": text}))
        return text

    except Exception:
        return fallback