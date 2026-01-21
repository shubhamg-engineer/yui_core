
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing .env loading...")
print(f"DEFAULT_PROVIDER: {os.getenv('DEFAULT_PROVIDER')}")
print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"GROQ_API_KEY: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")

# Test Gemini directly
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    import requests
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_key}"
    payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}
    
    print("\nTesting Gemini API...")
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Gemini works!")
            print(f"Response: {r.json()['candidates'][0]['content']['parts'][0]['text']}")
        else:
            print(f"❌ Error: {r.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
else:
    print("❌ No Gemini key found")