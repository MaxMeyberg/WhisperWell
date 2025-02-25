import logging
from typing import Dict, List, Optional
from mem0 import MemoryClient

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, api_key):
        self.client = MemoryClient(api_key=api_key)
        self.all_histories = {}  # Local cache of all histories
    
    def save_chat_history(self, session_id: str, chat_history: List[Dict]):
        """Save individual chat history to Mem0"""
        try:
            # Save to Mem0
            self.client.add_memory(session_id, chat_history)
            # Update local cache
            self.all_histories[session_id] = chat_history
            logger.info(f"Saved chat history for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
    
    def get_chat_history(self, session_id: str) -> Optional[List[Dict]]:
        """Get chat history from Mem0"""
        try:
            # Try local cache first
            if session_id in self.all_histories:
                return self.all_histories[session_id]
            
            # If not in cache, get from Mem0
            history = self.client.get_memories(session_id)
            if history:
                self.all_histories[session_id] = history  # Update cache
            return history
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None
            
    def get_all_chat_histories(self) -> Dict[str, List[Dict]]:
        """Get all chat histories"""
        try:
            # Get all sessions from Mem0
            all_sessions = self.client.get_all_sessions()  # You'll need to implement this in Mem0
            
            # Update local cache
            for session_id in all_sessions:
                if session_id not in self.all_histories:
                    history = self.client.get_memories(session_id)
                    if history:
                        self.all_histories[session_id] = history
                        
            return self.all_histories
        except Exception as e:
            logger.error(f"Failed to get all chat histories: {e}")
            return {}
