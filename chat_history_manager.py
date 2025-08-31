from azure.cosmos import CosmosClient, PartitionKey
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

class ChatHistoryManager:
    def __init__(self, cosmos_endpoint: str, cosmos_key: str, database_name: str = "ChatDB", container_name: str = "ChatHistory"):
        self.client = CosmosClient(cosmos_endpoint, cosmos_key)
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)
    
    def save_message(self, user_id: str, user_message: str, assistant_message: str):
        """Save user and assistant messages to chat history"""
        try:
            # Try to get existing chat
            chat = self.get_user_chat(user_id)
            
            if not chat:
                # Create new chat document
                chat = {
                    "id": user_id,
                    "userId": user_id,
                    "messages": [],
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
            
            # Add user message
            chat["messages"].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add assistant message
            chat["messages"].append({
                "role": "assistant", 
                "content": assistant_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            chat["updatedAt"] = datetime.utcnow().isoformat()
            
            # Save to CosmosDB
            self.container.upsert_item(chat)
            return True
            
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def get_user_chat(self, user_id: str) -> Optional[Dict]:
        """Get entire chat history for a user"""
        try:
            return self.container.read_item(user_id, partition_key=user_id)
        except:
            return None
    
    def get_recent_messages(self, user_id: str, count: int = 5) -> List[Dict]:
        """Get last N messages for context checking"""
        chat = self.get_user_chat(user_id)
        if not chat or not chat.get("messages"):
            return []
        
        messages = chat["messages"]
        return messages[-count:] if len(messages) > count else messages
    
    def is_followup_question(self, user_id: str, new_question: str) -> bool:
        """Simple check if new question is a follow-up"""
        recent_messages = self.get_recent_messages(user_id, 3)
        
        if not recent_messages:
            return False
        
        # Get last user message
        last_user_message = None
        for msg in reversed(recent_messages):
            if msg["role"] == "user":
                last_user_message = msg
                break
        
        if not last_user_message:
            return False
        
        # Simple time-based check (within 30 minutes = follow-up)
        last_time = datetime.fromisoformat(last_user_message["timestamp"].replace('Z', '+00:00'))
        time_diff = datetime.utcnow().replace(tzinfo=last_time.tzinfo) - last_time
        
        if time_diff.total_seconds() > 1800:  # 30 minutes
            return False
        
        # Simple keyword-based detection
        followup_keywords = [
            "and", "also", "what about", "how about", "tell me more",
            "explain", "why", "how", "continue", "more details",
            "but", "however", "what if", "can you", "please"
        ]
        
        question_lower = new_question.lower()
        return any(keyword in question_lower for keyword in followup_keywords)

# Usage Example
def main():
    # Initialize
    chat_manager = ChatHistoryManager(
        cosmos_endpoint="your-cosmos-endpoint",
        cosmos_key="your-cosmos-key"
    )
    
    user_id = "user123"
    
    # Simulate conversation flow
    def handle_user_message(user_message: str):
        print(f"User: {user_message}")
        
        # Check if follow-up
        is_followup = chat_manager.is_followup_question(user_id, user_message)
        
        if is_followup:
            # Get recent context for AI
            context = chat_manager.get_recent_messages(user_id, 5)
            print(f"Follow-up detected. Using context of {len(context)} messages.")
        else:
            print("New topic detected. Starting fresh.")
            context = []
        
        # Generate AI response (placeholder)
        ai_response = f"AI response to: {user_message}"
        
        # Save to database
        success = chat_manager.save_message(user_id, user_message, ai_response)
        
        if success:
            print(f"Assistant: {ai_response}")
            print("✓ Saved to CosmosDB")
        else:
            print("✗ Failed to save")
        
        print("-" * 50)
    
    # Example conversation
    handle_user_message("How do I cook pasta?")
    handle_user_message("What about the cooking time?")  # Follow-up
    handle_user_message("What's the weather today?")     # New topic

if __name__ == "__main__":
    main()
