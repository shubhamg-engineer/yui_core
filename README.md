# 🌙 Yui AI Companion

> **A human-like AI companion with memory, emotions, and personality**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Cost](https://img.shields.io/badge/cost-%240-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

**Yui** is a fully-featured AI companion that remembers your conversations, understands your emotions, and helps you with various tasks—all for **$0** using free APIs.

---

## ✨ Features

### 🧠 **Intelligent Conversation**
- Multi-LLM support (Groq, Gemini, HuggingFace, Cohere, Ollama)
- 3 distinct personalities: **Yui** 🌙 (warm companion), **Friday** 💼 (professional assistant), **Jarvis** 🎩 (sophisticated butler)
- Context-aware responses with conversation history

### 💾 **Persistent Memory**
- **SQLite Database**: Stores all conversations, user profiles, and sessions
- **ChromaDB Vector Store**: Semantic search of past conversations
- Remembers you across sessions—close and reopen, she still knows you!

### ❤️ **Emotion Detection**
- VADER sentiment analysis detects 8+ emotions (joy, sadness, anger, fear, etc.)
- Empathetic responses based on your emotional state
- Dynamic mood adaptation

### 🛠️ **Smart Tools**
- **Web Search**: DuckDuckGo integration (no API key needed)
- **Weather**: Real-time weather for any location
- **Jokes, Quotes, Facts**: Entertainment on demand
- **Crypto Prices**: Live cryptocurrency data
- **Dictionary**: Word definitions and meanings
- Natural language tool invocation—just ask!

### 🎨 **Beautiful Interfaces**
- **Terminal**: Rich, colorful CLI with commands
- **Web UI**: Premium dark theme with glassmorphism, gradients, and smooth animations
- Mobile-responsive design

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Free API keys (see [Setup](#setup))

### Installation

```bash
# Clone the repository
git clone https://github.com/shubhamg-engineer/yui_core.git
cd yui_core

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys
```

### Setup

Get your **free** API keys:

1. **Groq** (Recommended - Fastest & Free)
   - Get key at: https://console.groq.com/
   - Add to `.env`: `GROQ_API_KEY=your_key_here`

2. **Google Gemini** (Optional - Free tier)
   - Get key at: https://makersuite.google.com/
   - Add to `.env`: `GEMINI_API_KEY=your_key_here`

3. **HuggingFace** (Optional - Free)
   - Get key at: https://huggingface.co/settings/tokens
   - Add to `.env`: `HUGGINGFACE_API_KEY=your_key_here`

### Run

**Terminal Interface:**
```bash
python main.py
```

**Web Interface:**
```bash
python web/app.py
# Open http://localhost:8000 in your browser
```

---

## 📖 Usage

### Commands
- `/clear` - Clear conversation history
- `/switch <personality>` - Switch between yui, friday, or jarvis
- `/info` - Show conversation statistics
- `/help` - Display help message
- `/quit` - Exit the application

### Examples

**Basic Conversation:**
```
You: Hello!
Yui: Hi there! 🌙 How are you doing today?

You: I'm feeling a bit stressed
Yui: I'm sorry to hear you're stressed. Want to talk about it? I'm here to listen.
```

**Using Tools:**
```
You: What's the weather in Tokyo?
Yui: *Fetches weather data* It's currently 22°C and partly cloudy in Tokyo!

You: Tell me a joke
Yui: Why don't scientists trust atoms? Because they make up everything! 😄
```

**Personality Switching:**
```
You: /switch friday
Friday: Switching to professional mode. How may I assist you today?

You: /switch jarvis
Jarvis: Good day, sir. Jarvis at your service.
```

---

## 🏗️ Architecture

```
yui-core/
├── config/              # Configuration & API keys
├── core/                # LLM engine & conversation logic
├── personalities/       # 3 personality definitions
├── memory/              # SQLite + ChromaDB memory system
├── emotions/            # Sentiment analysis & emotion detection
├── tools/               # External APIs & tool executor
├── web/                 # FastAPI backend + HTML/CSS/JS frontend
├── main.py              # Terminal interface
└── requirements.txt     # Dependencies
```

---

## 🌍 Deployment

Deploy to the cloud in minutes!

### Render.com (Recommended)
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. New → Web Service
3. Connect your `yui_core` repository
4. Add environment variables (`GROQ_API_KEY`, etc.)
5. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions for Render, Railway, and Fly.io.

---

## 🧪 Testing

Run the API test suite:
```bash
python test_apis_quick.py
```

Expected output:
```
✅ Groq API: Working
✅ Gemini API: Working
✅ HuggingFace API: Key Valid
✅ 3/3 APIs working
```

---

## 📊 Tech Stack

**Core:**
- Python 3.10+
- FastAPI (web backend)
- WebSockets (real-time chat)

**AI/ML:**
- Groq, Gemini, HuggingFace (LLM providers)
- VADER (sentiment analysis)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)

**Storage:**
- SQLite (conversation history)
- ChromaDB (semantic search)

**UI:**
- Rich (terminal UI)
- HTML/CSS/JavaScript (web UI)

**APIs:**
- DuckDuckGo Search
- wttr.in (weather)
- JokeAPI, Advice Slip, BoredAPI, CoinGecko, etc.

---

## 🎯 Roadmap

**Completed (MVP):**
- ✅ Conversation engine with 3 personalities
- ✅ Persistent memory system
- ✅ Emotion detection & empathy
- ✅ Smart tools integration
- ✅ Web interface
- ✅ Deployment ready

**Future Enhancements:**
- 🎤 Voice interface (TTS/STT)
- 👁️ Vision capabilities (webcam, face emotion detection)
- 🤖 Multi-bot spawning system
- 🔐 User authentication
- ☁️ Cloud database integration
- 📱 Mobile app

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for blazing-fast free LLM API
- **Google** for Gemini API
- **HuggingFace** for model hosting
- **DuckDuckGo** for free search API
- All the amazing open-source libraries used in this project

---

## 📧 Contact

**Project Link:** https://github.com/shubhamg-engineer/yui_core

---

<div align="center">

**Built with ❤️ using free APIs and open source tools**

⭐ Star this repo if you find it useful!

</div>
