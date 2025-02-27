import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, api_key=None):  # Made api_key optional since we're not using external service
        self.all_histories = {}  # Local cache

    def add_memory(self, key: str, data: Dict):
        """Add any type of memory (chat, image, etc)"""
        try:
            # Store in local cache
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
            return self.all_histories
        except Exception as e:
            logger.error(f"Failed to get all chat histories: {e}")
            return {}
