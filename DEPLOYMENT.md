# Deployment Guide - Deploy Yui to Cloud

## Option 1: Render.com (Recommended - Free Tier)

### Steps:
1. Create account at [render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repository
4. Configuration:
   - **Build Command**: `pip install -r requirements.txt && pip install fastapi uvicorn websockets python-multipart`
   - **Start Command**: `cd web && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `GROQ_API_KEY`: your_groq_key
     - `GEMINI_API_KEY`: your_gemini_key
     - `HUGGINGFACE_API_KEY`: your_hf_key

5. Deploy!

## Option 2: Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project
railway init

# Add environment variables
railway variables set GROQ_API_KEY=your_key
railway variables set GEMINI_API_KEY=your_key

# Deploy
railway up
```

## Option 3: Fly.io

```bash
# Install flyctl
# Windows: iwr https://fly.io/install.ps1 -useb | iex

# Launch app
fly launch

# Set secrets
fly secrets set GROQ_API_KEY=your_key
fly secrets set GEMINI_API_KEY=your_key

# Deploy
fly deploy
```

## Environment Variables Required

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_hf_api_key_here
DEFAULT_PROVIDER=gemini  
DEFAULT_PERSONALITY=yui
MAX_TOKENS=2048
TEMPERATURE=0.7
```

## Testing Deployment

1. Visit your deployed URL
2. Enter your name
3. Send a test message
4. Try commands: `/switch friday`, `/info`
5. Test tools: "What's the weather in Tokyo?"

## Troubleshooting

- **WebSocket errors**: Check CORS settings
- **Memory errors**: Increase Render/Railway memory limit
- **API errors**: Verify environment variables are set
- **Import errors**: Ensure all dependencies in requirements.txt
