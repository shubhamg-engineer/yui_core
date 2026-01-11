
import os

from dotenv import load_dotenv

load_dotenv()

def test_api():

    groq = os.getenv('GROQ_API_KEY')

    gemini = os.getenv('GEMINI_API_KEY')

    print("Groq:", "✅ Set" if groq else "❌ Not set")

    print("Gemini:", "✅ Set" if gemini else "❌ Not set")

if __name__ == "__main__":

    test_api()

