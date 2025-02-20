from typing import Dict, List, Optional
import logging
from mem0 import MemoryClient
import os
logger = logging.getLogger(__name__)

# Initialize mem0 client
mem0_client = MemoryClient(api_key=os.environ['MEM0_API_KEY'])
def get_login(credentials: Optional[Dict] = None) -> Dict:
    """Simple login for now"""
    return {
        "status": "success",
        "user_id": "temp_user",
    }

def get_memories(user_id: str, query: Optional[str] = None) -> List[Dict]:
    """Get memories using mem0"""
    try:
        if query:
            return mem0_client.search(query, user_id=user_id)
        else:
            return mem0_client.get(user_id=user_id)
    except Exception as e:
        logger.error(f"Error getting memories: {str(e)}")
        return []

def add_memory(user_id: str, conversation: List[Dict]):
    """Add memory using mem0"""
    try:
        mem0_client.add(conversation, user_id=user_id)
    except Exception as e:
        logger.error(f"Error adding memory: {str(e)}")
