#!/usr/bin/env python3
"""
Validate Yui setup before running
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def validate_setup():
    """Check if Yui is properly configured"""
    print("🔍 Validating Yui Setup...\n")
    
    issues = []
    warnings = []
    
    # Check 1: .env file exists
    if not Path(".env").exists():
        issues.append("❌ .env file not found! Create it in the root directory.")
    else:
        print("✅ .env file found")
        load_dotenv()
        
        # Check 2: Provider is set
        provider = os.getenv('DEFAULT_PROVIDER')
        if not provider:
            issues.append("❌ DEFAULT_PROVIDER not set in .env")
        else:
            print(f"✅ Provider: {provider}")
            
            # Check 3: Required API key for provider
            if provider == 'groq':
                if not os.getenv('GROQ_API_KEY'):
                    issues.append("❌ GROQ_API_KEY not set but provider is 'groq'")
                else:
                    key = os.getenv('GROQ_API_KEY')
                    print(f"✅ Groq key: {key[:15]}...")
            
            elif provider == 'gemini':
                if not os.getenv('GEMINI_API_KEY'):
                    issues.append("❌ GEMINI_API_KEY not set but provider is 'gemini'")
                else:
                    key = os.getenv('GEMINI_API_KEY')
                    print(f"✅ Gemini key: {key[:15]}...")
            
            elif provider == 'huggingface':
                if not os.getenv('HUGGINGFACE_API_KEY'):
                    issues.append("❌ HUGGINGFACE_API_KEY not set but provider is 'huggingface'")
                else:
                    key = os.getenv('HUGGINGFACE_API_KEY')
                    print(f"✅ HuggingFace key: {key[:15]}...")
            
            elif provider == 'ollama':
                print("ℹ️  Ollama doesn't need API key")
                warnings.append("⚠️  Make sure Ollama is running: ollama serve")
    
    # Check 4: Required Python packages
    try:
        import requests
        print("✅ requests installed")
    except ImportError:
        issues.append("❌ 'requests' not installed. Run: pip install requests")
    
    try:
        import rich
        print("✅ rich installed")
    except ImportError:
        issues.append("❌ 'rich' not installed. Run: pip install rich")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        issues.append("❌ 'python-dotenv' not installed. Run: pip install python-dotenv")
    
    # Check 5: File structure
    required_files = [
        'config/config.py',
        'core/llm.py',
        'core/conversation.py',
        'personalities/base_personality.py',
        'main.py'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            issues.append(f"❌ Missing file: {file}")
    
    # Print summary
    print("\n" + "="*60)
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou can now run: python main.py")
    else:
        print(f"\n❌ Found {len(issues)} issue(s). Fix them before running Yui.")
    
    print("="*60)
    
    return len(issues) == 0

if __name__ == "__main__":
    validate_setup()