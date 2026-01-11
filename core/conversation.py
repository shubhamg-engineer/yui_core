from typing import List, Dict
from datetime import datetime
from core.llm import LLMEngine
from personalities.base_personality import get_personality
from config.config import Config

class ConversationManager:
    """Manages conversation flow and context"""
    
    def __init__(self, personality_name: str = "yui", user_name: str = "User"):
        # Initialize LLM with configured provider
        provider = Config.get_active_provider()
        self.llm = LLMEngine(provider=provider)
        self.personality = get_personality(personality_name)
        self.user_name = user_name
        self.conversation_history: List[Dict] = []
        self.max_history = 20  # Keep last 20 messages for context
        
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if too long (keep most recent messages)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_messages_for_llm(self) -> List[Dict]:
        """Format conversation history for LLM (without timestamps)"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    def send_message(self, user_message: str) -> str:
        """
        Send user message and get bot response
        
        Args:
            user_message: The user's message
            
        Returns:
            Bot's response
        """
        # Add user message to history
        self.add_message("user", user_message)
        
        # Get system prompt
        system_prompt = self.personality.get_system_prompt(self.user_name)
        
        # Get messages for LLM
        messages = self.get_messages_for_llm()
        
        # Generate response
        bot_response = self.llm.generate(messages, system_prompt)
        
        # Add bot response to history
        self.add_message("assistant", bot_response)
        
        return bot_response
    
    def stream_response(self, user_message: str):
        """
        Stream bot response (for future voice integration)
        
        Args:
            user_message: The user's message
            
        Yields:
            Response chunks
        """
        # Add user message to history
        self.add_message("user", user_message)
        
        # Get system prompt
        system_prompt = self.personality.get_system_prompt(self.user_name)
        
        # Get messages for LLM
        messages = self.get_messages_for_llm()
        
        # Stream response
        full_response = ""
        for chunk in self.llm.stream_generate(messages, system_prompt):
            full_response += chunk
            yield chunk
        
        # Add complete response to history
        self.add_message("assistant", full_response)
    
    def switch_personality(self, personality_name: str):
        """Switch to a different personality"""
        self.personality = get_personality(personality_name)
        print(f"\n✨ Switched to {self.personality.name} personality\n")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("\n🗑️  Conversation history cleared\n")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        return f"""
Conversation with {self.personality.name}
Total messages: {len(self.conversation_history)}
User: {self.user_name}
Started: {self.conversation_history[0]['timestamp'] if self.conversation_history else 'N/A'}
"""