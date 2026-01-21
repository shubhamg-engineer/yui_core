"""
Yui AI Companion - Web Interface Backend
FastAPI server with WebSocket support for real-time chat
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import core modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from typing import Dict
from datetime import datetime

# Import Yui core
from core.conversation import ConversationManager
from config.config import Config
from tools.tool_executor import ToolExecutor

app = FastAPI(title="Yui AI Companion", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Store active conversations
conversations: Dict[str, ConversationManager] = {}
tool_executor = ToolExecutor()


@app.get("/")
async def root():
    """Serve the main chat interface"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Yui AI Companion API - WebSocket endpoint at /ws/{user_name}"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "provider": Config.get_active_provider(),
        "timestamp": datetime.now().isoformat()
    }


@app.websocket("/ws/{user_name}")
async def websocket_endpoint(websocket: WebSocket, user_name: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Create or get conversation manager
    session_id = str(uuid.uuid4())
    conversation_key = f"{user_name}_{session_id}"
    
    try:
        # Initialize conversation
        conversation = ConversationManager(
            personality_name="yui",
            user_name=user_name
        )
        conversations[conversation_key] = conversation
        
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "content": f"✨ Welcome {user_name}! I'm Yui. How can I help you today?",
            "timestamp": datetime.now().isoformat()
        })
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("content", "")
            message_type = message_data.get("type", "user")
            
            if not user_message.strip():
                continue
            
            # Handle commands
            if user_message.startswith("/"):
                command_result = await handle_command(
                    conversation,
                    user_message,
                    websocket
                )
                if command_result:
                    continue
            
            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "content": "Yui is thinking...",
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if message needs a tool
            tool_result = tool_executor.process_message(user_message)
            
            if tool_result:
                # Send tool result
                await websocket.send_json({
                    "type": "tool",
                    "content": tool_result,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Get AI response
            bot_response = conversation.send_message(user_message)
            
            # Send response
            await websocket.send_json({
                "type": "assistant",
                "content": bot_response,
                "personality": conversation.personality.name,
                "timestamp": datetime.now().isoformat()
            })
    
    except WebSocketDisconnect:
        # Cleanup on disconnect
        if conversation_key in conversations:
            del conversations[conversation_key]
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


async def handle_command(conversation: ConversationManager, command: str, websocket: WebSocket) -> bool:
    """Handle chat commands"""
    command_lower = command.lower().strip()
    
    if command_lower in ["/quit", "/exit"]:
        await websocket.send_json({
            "type": "system",
            "content": "Goodbye! 👋",
            "timestamp": datetime.now().isoformat()
        })
        await websocket.close()
        return True
    
    elif command_lower == "/clear":
        conversation.clear_history()
        await websocket.send_json({
            "type": "system",
            "content": "🗑️ Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    elif command_lower.startswith("/switch"):
        parts = command_lower.split()
        if len(parts) > 1:
            personality_name = parts[1]
            try:
                conversation.switch_personality(personality_name)
                await websocket.send_json({
                    "type": "system",
                    "content": f"✨ Switched to {personality_name.title()} personality",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error switching personality: {e}",
                    "timestamp": datetime.now().isoformat()
                })
        else:
            await websocket.send_json({
                "type": "system",
                "content": "Usage: /switch <personality>\nAvailable: yui, friday, jarvis",
                "timestamp": datetime.now().isoformat()
            })
        return True
    
    elif command_lower == "/info":
        summary = conversation.get_conversation_summary()
        await websocket.send_json({
            "type": "system",
            "content": summary,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    elif command_lower == "/help":
        help_text = """
**Available Commands:**
- /clear - Clear conversation history
- /switch <personality> - Switch between yui, friday, jarvis
- /info - Show conversation statistics
- /help - Show this help message
- /quit - Close the chat
"""
        await websocket.send_json({
            "type": "system",
            "content": help_text,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    return False


# Mount static files (must be last)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🌙 Starting Yui AI Companion Web Server...")
    print(f"🔗 Open: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
