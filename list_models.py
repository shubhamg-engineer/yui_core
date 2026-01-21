import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("No key found")
    exit()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    with open("models.txt", "w") as f:
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                line = f"- {m['name']} ({m.get('version', '')})"
                print(line)
                f.write(line + "\n")
else:
    print(f"Error: {response.status_code} - {response.text}")
