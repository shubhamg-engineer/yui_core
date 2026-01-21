from typing import List, Dict, Optional
from datetime import datetime
from core.llm import LLMEngine
from personalities.base_personality import get_personality
from config.config import Config

# Import memory and emotion systems
try:
    from memory.memory_manager import MemoryManager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠️  Memory system not available")

try:
    from emotions.emotion_detector import EmotionDetector, EmotionState
    EMOTIONS_AVAILABLE = True
except ImportError:
    EMOTIONS_AVAILABLE = False
    print("⚠️  Emotion detection not available")


class ConversationManager:
    """Manages conversation flow with memory and emotion awareness"""
    
    def __init__(self, personality_name: str = "yui", user_name: str = "User"):
        # Initialize LLM with configured provider
        provider = Config.get_active_provider()
        self.llm = LLMEngine(provider=provider)
        self.personality = get_personality(personality_name)
        self.user_name = user_name
        self.conversation_history: List[Dict] = []
        self.max_history = 20  # Keep last 20 messages for context
        
        # Initialize memory system
        if MEMORY_AVAILABLE:
            try:
                self.memory = MemoryManager(user_name)
                self.memory.start_session(self.personality.name)
                print(f"✅ Memory system enabled for {user_name}")
            except Exception as e:
                print(f"⚠️  Memory system failed to initialize: {e}")
                self.memory = None
        else:
            self.memory = None
        
        # Initialize emotion detection
        if EMOTIONS_AVAILABLE:
            try:
                self.emotion_detector = EmotionDetector()
                self.emotion_state = EmotionState()
                print(f"✅ Emotion detection enabled")
            except Exception as e:
                print(f"⚠️  Emotion detection failed to initialize: {e}")
                self.emotion_detector = None
                self.emotion_state = None
        else:
            self.emotion_detector = None
            self.emotion_state = None
        
    def add_message(self, role: str, content: str, emotion: Optional[str] = None):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion
        })
        
        # Save to persistent memory
        if self.memory:
            try:
                self.memory.save_message(
                    role=role,
                    content=content,
                    personality=self.personality.name,
                    emotion=emotion
                )
            except Exception as e:
                print(f"⚠️  Failed to save to memory: {e}")
        
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
        # Detect emotion from user message
        emotion_data = None
        if self.emotion_detector:
            try:
                emotion_data = self.emotion_detector.analyze_emotion(user_message)
                detected_emotion = emotion_data['emotion']
                
                # Update bot's emotional state
                if self.emotion_state:
                    self.emotion_state.update_mood(detected_emotion)
            except Exception as e:
                print(f"⚠️  Emotion detection error: {e}")
                detected_emotion = None
        else:
            detected_emotion = None
        
        # Add user message to history
        self.add_message("user", user_message, detected_emotion)
        
        # Build system prompt with personality and context
        system_prompt = self.personality.get_system_prompt(self.user_name)
        
        # Add emotion context if available
        if emotion_data and self.emotion_detector:
            emotion_context = self.emotion_detector.get_emotion_context(emotion_data)
            system_prompt += f"\n\n{emotion_context}"
        
        # Add emotional tone instruction
        if self.emotion_state:
            tone_instruction = self.emotion_state.get_tone_instruction()
            system_prompt += f"\n{tone_instruction}"
        
        # Get relevant memories if available
        if self.memory:
            try:
                relevant_memories = self.memory.get_relevant_context(user_message, max_items=2)
                if relevant_memories:
                    memory_context = "\n\nRelevant past conversations:\n" + "\n".join(relevant_memories)
                    system_prompt += memory_context
            except Exception as e:
                print(f"⚠️  Memory retrieval error: {e}")
        
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
        # Detect emotion
        emotion_data = None
        if self.emotion_detector:
            try:
                emotion_data = self.emotion_detector.analyze_emotion(user_message)
                detected_emotion = emotion_data['emotion']
                if self.emotion_state:
                    self.emotion_state.update_mood(detected_emotion)
            except:
                detected_emotion = None
        else:
            detected_emotion = None
        
        # Add user message to history
        self.add_message("user", user_message, detected_emotion)
        
        # Build system prompt
        system_prompt = self.personality.get_system_prompt(self.user_name)
        
        if emotion_data and self.emotion_detector:
            emotion_context = self.emotion_detector.get_emotion_context(emotion_data)
            system_prompt += f"\n\n{emotion_context}"
        
        if self.emotion_state:
            tone_instruction = self.emotion_state.get_tone_instruction()
            system_prompt += f"\n{tone_instruction}"
        
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
        
        # Update memory session
        if self.memory:
            try:
                self.memory.end_session()
                self.memory.session_id = None
                self.memory.start_session(self.personality.name)
            except Exception as e:
                print(f"⚠️  Memory session update error: {e}")
        
        print(f"\n✨ Switched to {self.personality.name} personality\n")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
        # Clear memory session (start new one)
        if self.memory:
            try:
                self.memory.clear_session_memory()
                self.memory.start_session(self.personality.name)
            except Exception as e:
                print(f"⚠️  Memory clear error: {e}")
        
        print("\n🗑️  Conversation history cleared\n")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        base_summary = f"""
Conversation with {self.personality.name}
Total messages: {len(self.conversation_history)}
User: {self.user_name}
Started: {self.conversation_history[0]['timestamp'] if self.conversation_history else 'N/A'}
"""
        
        # Add memory stats if available
        if self.memory:
            try:
                stats = self.memory.get_user_stats()
                base_summary += f"""
Memory Stats:
- Total messages across all sessions: {stats['total_messages']}
- Total sessions: {stats['total_sessions']}
- Favorite personality: {stats['favorite_personality']}
"""
            except Exception as e:
                print(f"⚠️  Stats retrieval error: {e}")
        
        return base_summary
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'memory') and self.memory:
            try:
                self.memory.end_session()
            except:
                pass