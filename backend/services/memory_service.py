import logging
from typing import Dict, List, Optional
from mem0 import MemoryClient

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, api_key):
        self.client = MemoryClient(api_key=api_key)
        self.all_histories = {}  # Local cache

    def add_memory(self, key: str, data: Dict):
        """Add any type of memory (chat, image, etc)"""
        try:
            # For now, just store in local cache
            if key not in self.all_histories:
                self.all_histories[key] = []
            self.all_histories[key].append(data)
            logger.info(f"Added memory for key: {key}")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")

    def save_chat_history(self, session_id: str, chat_history: List[Dict]):
        """Save chat history"""
        try:
            self.all_histories[f"chat_{session_id}"] = chat_history
            logger.info(f"Saved chat history for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")

    def get_chat_history(self, session_id: str) -> Optional[List[Dict]]:
        """Get chat history"""
        try:
            return self.all_histories.get(f"chat_{session_id}")
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
