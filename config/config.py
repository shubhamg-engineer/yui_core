import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for Yui"""
    
    # ============ API KEYS (Choose ONE) ============
    # FREE APIS - No payment required!
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # RECOMMENDED - Fast & Free
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Free
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Free tier
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Free trial
    
    # PAID APIS (Optional - better quality)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Claude
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # GPT
    
    # ============ MODEL SETTINGS ============
    # Choose your provider: "groq", "huggingface", "gemini", "ollama", "cohere"
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")
    
    # Model names (optional - defaults are set in LLMEngine)
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "")
    
    # Generation settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # ============ BOT SETTINGS ============
    BOT_NAME = os.getenv("BOT_NAME", "Yui")
    DEFAULT_PERSONALITY = os.getenv("DEFAULT_PERSONALITY", "yui")
    
    # ============ PATHS ============
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"
    DATABASE_PATH = DATA_DIR / "yui_memory.db"
    
    # ============ LOGGING ============
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOG_DIR / "yui.log"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        # Check if at least one API key is available (or using Ollama)
        has_api_key = any([
            cls.GROQ_API_KEY,
            cls.HUGGINGFACE_API_KEY,
            cls.GEMINI_API_KEY,
            cls.COHERE_API_KEY,
            cls.ANTHROPIC_API_KEY,
            cls.OPENAI_API_KEY,
            cls.DEFAULT_PROVIDER == "ollama"  # Ollama doesn't need API key
        ])
        
        if not has_api_key:
            raise ValueError("""
╔════════════════════════════════════════════════════════════╗
║  NO API KEY FOUND!                                         ║
║                                                            ║
║  You need to set up ONE of these FREE APIs:               ║
║                                                            ║
║  1. GROQ (RECOMMENDED - Fastest & Free)                   ║
║     → Get key at: https://console.groq.com/                ║
║     → Set in .env: GROQ_API_KEY=your_key_here             ║
║                                                            ║
║  2. GOOGLE GEMINI (Free tier)                             ║
║     → Get key at: https://makersuite.google.com/          ║
║     → Set in .env: GEMINI_API_KEY=your_key_here           ║
║                                                            ║
║  3. HUGGING FACE (Free)                                   ║
║     → Get key at: https://huggingface.co/settings/tokens  ║
║     → Set in .env: HUGGINGFACE_API_KEY=your_key_here      ║
║                                                            ║
║  4. OLLAMA (100% Free, Local)                             ║
║     → Install: https://ollama.ai/                         ║
║     → Set in .env: DEFAULT_PROVIDER=ollama                ║
║     → No API key needed!                                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
        
        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def get_active_provider(cls):
        """Get which provider is being used"""
        # Respect DEFAULT_PROVIDER setting first
        if cls.DEFAULT_PROVIDER:
            provider = cls.DEFAULT_PROVIDER.lower()
            
            # Validate provider has required key
            if provider == "ollama":
                return "ollama"
            elif provider == "groq" and cls.GROQ_API_KEY:
                return "groq"
            elif provider == "gemini" and cls.GEMINI_API_KEY:
                return "gemini"
            elif provider == "huggingface" and cls.HUGGINGFACE_API_KEY:
                return "huggingface"
            elif provider == "cohere" and cls.COHERE_API_KEY:
                return "cohere"
        
        # Fallback: auto-detect first available API
        if cls.GROQ_API_KEY:
            return "groq"
        elif cls.GEMINI_API_KEY:
            return "gemini"
        elif cls.HUGGINGFACE_API_KEY:
            return "huggingface"
        elif cls.COHERE_API_KEY:
            return "cohere"
        elif cls.ANTHROPIC_API_KEY:
            return "anthropic"
        elif cls.OPENAI_API_KEY:
            return "openai"
        
        return None

# Validate on import
Config.validate()