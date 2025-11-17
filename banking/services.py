# chatbot/services.py
import requests
import json
from django.conf import settings
from typing import List, Dict, Optional

class OpenRouterService:
    @staticmethod
    def send_message(messages: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Send messages to OpenRouter API and return the response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Dict containing the API response or None if error
        """
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": settings.YOUR_SITE_URL,
                    "X-Title": settings.YOUR_SITE_NAME,
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": messages,
                },
                timeout=30  # 30 second timeout
            )
            
            response.raise_for_status()  # Raise exception for bad status codes
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode failed: {e}")
            return None

    @staticmethod
    def get_chat_response(user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Get a response from the chatbot for a user message
        
        Args:
            user_message: The user's input message
            conversation_history: Optional previous messages for context
            
        Returns:
            The assistant's response text
        """
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the new user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Send to API
        api_response = OpenRouterService.send_message(messages)
        
        if api_response and 'choices' in api_response and len(api_response['choices']) > 0:
            return api_response['choices'][0]['message']['content']
        else:
            return "Sorry, I'm having trouble connecting to the chatbot service."