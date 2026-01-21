# Quick Start - Run Yui Locally

## 1. Install Dependencies
```bash
cd c:\hanime\yui-core
pip install -r requirements.txt
pip install fastapi uvicorn websockets python-multipart
```

## 2. Run Terminal Version
```bash
python main.py
```

## 3. Run Web Version
```bash
cd web
python app.py
```

Then open: http://localhost:8000

## 4. Available Commands
- `/clear` - Clear conversation history
- `/switch <personality>` - Change personality (yui, friday, jarvis)
- `/info` - Show conversation stats
- `/help` - Show help
- `/quit` - Exit
