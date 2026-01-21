#!/usr/bin/env python3
"""
Quick test script to verify API integrations
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq():
    """Test Groq API connection"""
    try:
        from groq import Groq
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            print("❌ GROQ_API_KEY not found in .env")
            return False
            
        client = Groq(api_key=api_key)
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Groq is working!' in one sentence."}],
            max_tokens=50
        )
        
        print(f"✅ Groq API: {response.choices[0].message.content.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return False

def test_gemini():
    """Test Google Gemini API connection (using requests like core/llm.py)"""
    try:
        import requests
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env")
            return False
            
        # Use v1beta for Gemini models
        model = "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": "Say 'Gemini is working!' in one sentence."}]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"❌ Gemini API Error ({response.status_code}): {response.text[:100]}"
            print(error_msg)
            return error_msg
            
        data = response.json()
        print(f"✅ Gemini API: {data['candidates'][0]['content']['parts'][0]['text'].strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return f"Error: {str(e)}"

def test_huggingface():
    """Test HuggingFace API connection"""
    try:
        import requests
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        if not api_key:
            print("❌ HUGGINGFACE_API_KEY not found in .env")
            return False
            
        # Simple test - just verify the key format
        if api_key.startswith('hf_'):
            print(f"✅ HuggingFace API: Key format valid (hf_...)")
            return True
        else:
            print(f"⚠️ HuggingFace API: Key format unusual, may not work")
            return False
        
    except Exception as e:
        print(f"❌ HuggingFace API Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 Testing API Integrations...\n")
    print("=" * 50)
    
    results = {
        "Groq": test_groq(),
        "Gemini": test_gemini(),
        "HuggingFace": test_huggingface()
    }
    
    working_count = sum(1 for r in results.values() if r is True)
    
    with open("test.log", "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f"Groq: {'✅ Working' if results['Groq'] is True else f'❌ Failed: {results['Groq']}'}\n")
        f.write(f"Gemini: {'✅ Working' if results['Gemini'] is True else f'❌ Failed: {results['Gemini']}'}\n")
        f.write(f"HuggingFace: {'✅ Key Valid' if results['HuggingFace'] else '❌ Failed'}\n")
        f.write("=" * 50 + "\n")

    print(f"\n✅ {working_count}/3 APIs working")
    
    if working_count > 0:
        print("\n🎉 At least one API is working! Yui can talk!\n")
        sys.exit(0)
    else:
        print("\n⚠️ No APIs are working. Please check your API keys.\n")
        sys.exit(1)
