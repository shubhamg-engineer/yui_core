"""
Memory Manager for Yui AI Companion
Combines SQLite persistence with ChromaDB vector search for semantic memory
"""
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from memory.database import DatabaseManager


class MemoryManager:
    """
    Central memory system combining:
    - Short-term memory (recent conversation context)
    - Long-term memory (vector database for semantic search)
    - User profiles and preferences
    """
    
    def __init__(self, user_name: str, session_id: Optional[str] = None):
        """Initialize memory system"""
        self.user_name = user_name
        self.session_id = session_id or str(uuid.uuid4())
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize vector database for semantic search
        try:
            self.chroma_client = chromadb.Client(Settings(
                persist_directory="data/chroma_db",
                anonymized_telemetry=False
            ))
            
            # Create or get collection for this user
            self.collection = self.chroma_client.get_or_create_collection(
                name=f"memories_{self.user_name.lower().replace(' ', '_')}",
                metadata={"user": self.user_name}
            )
            
            # Load sentence transformer for embeddings (lightweight model)
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.vector_enabled = True
            
        except Exception as e:
            print(f"⚠️ Vector memory disabled: {e}")
            self.vector_enabled = False
            self.collection = None
            self.encoder = None
        
        # Load user profile
        self.user_profile = self.db.get_or_create_user_profile(user_name)
    
    def start_session(self, personality: str):
        """Start a new conversation session"""
        self.db.create_session(self.session_id, self.user_name, personality)
    
    def save_message(self, role: str, content: str, personality: str, 
                    emotion: Optional[str] = None):
        """
        Save message to both database and vector store
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            personality: Current personality name
            emotion: Detected emotion (optional)
        """
        # Save to SQL database
        self.db.save_message(
            session_id=self.session_id,
            user_name=self.user_name,
            personality=personality,
            role=role,
            content=content,
            emotion=emotion
        )
        
        # Save to vector database for semantic search
        if self.vector_enabled and role == "user":  # Only index user messages
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[{
                        "session_id": self.session_id,
                        "personality": personality,
                        "timestamp": datetime.now().isoformat(),
                        "emotion": emotion or "neutral"
                    }],
                    ids=[f"{self.session_id}_{datetime.now().timestamp()}"]
                )
            except Exception as e:
                print(f"⚠️ Failed to save to vector memory: {e}")
    
    def get_recent_memory(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history for context"""
        return self.db.get_session_history(self.session_id, limit)
    
    def search_semantic_memory(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search past conversations semantically
        
        Args:
            query: What to search for
            n_results: Number of results to return
            
        Returns:
            List of relevant past conversations
        """
        if not self.vector_enabled:
            # Fallback to keyword search
            return self.db.search_conversations(self.user_name, query, n_results)
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    memories.append({
                        'content': doc,
                        'session_id': metadata.get('session_id'),
                        'personality': metadata.get('personality'),
                        'timestamp': metadata.get('timestamp'),
                        'emotion': metadata.get('emotion')
                    })
            
            return memories
            
        except Exception as e:
            print(f"⚠️ Semantic search failed: {e}")
            return self.db.search_conversations(self.user_name, query, n_results)
    
    def get_relevant_context(self, current_message: str, max_items: int = 3) -> List[str]:
        """
        Get relevant past conversations for current message
        
        Args:
            current_message: User's current message
            max_items: Maximum number of relevant memories to return
            
        Returns:
            List of relevant past conversation snippets
        """
        memories = self.search_semantic_memory(current_message, max_items)
        
        context = []
        for memory in memories:
            timestamp = memory.get('timestamp', 'unknown time')
            content = memory.get('content')
            context.append(f"[Past conversation from {timestamp}]: {content}")
        
        return context
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        return self.db.get_stats(self.user_name)
    
    def update_preferences(self, preferences: Dict):
        """Update user preferences"""
        self.db.update_user_preferences(self.user_name, preferences)
    
    def end_session(self):
        """End current session"""
        self.db.end_session(self.session_id)
    
    def get_full_history(self, limit: int = 100) -> List[Dict]:
        """Get full conversation history across all sessions"""
        return self.db.get_user_history(self.user_name, limit)
    
    def clear_session_memory(self):
        """Clear current session from memory (for /clear command)"""
        # Note: We don't delete from DB, just start a new session
        self.session_id = str(uuid.uuid4())
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.end_session()
        except:
            pass
