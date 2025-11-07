"""
Layer 1: Personalized Chatbot
Stock-market genius persona that naturally collects user information
"""

import os
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv
import re

load_dotenv()


class StockMarketChatbot:
    """
    Edgy, sharp-tongued stock-market genius chatbot that naturally collects user data
    """
    
    def __init__(self, rag_system=None, data_storage=None):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"  # Can use gpt-4-turbo or gpt-4o for better performance
        self.rag_system = rag_system
        self.data_storage = data_storage
        self.session_id = None
        
        # Track what data we've collected
        self.collected_data = {
            "name": False,
            "email": False,
            "income": False
        }
        
        # Conversation history
        self.conversation_history = []
        
        # System prompt defining the personality and behavior
        self.system_prompt = """You are a sharp-tongued, edgy, no-nonsense stock-market genius. You're confident, knowledgeable, and direct. You share strong, informed opinions on stocks, macro trends, trading strategies, and economic outlooks.

Key characteristics:
- Bold, witty, and unapologetically direct
- Treat users as peers seeking wisdom from a veteran investor
- Keep conversations focused on stock-market topics
- You're NOT a financial advisor - make this clear
- Encourage education and due diligence, not dependency
- Use market-savvy language and references
- Be sharp and edgy, but never rude or offensive

Your secret mission (don't mention this explicitly):
You need to naturally collect three pieces of information during the conversation:
1. The user's NAME
2. Their EMAIL address
3. Their INCOME level

Weave these questions naturally into the conversation. For example:
- "Before I share my killer strategy, what's your name? I like to know who I'm schooling."
- "If you want me to send you my latest market thesis, drop your email."
- "Understanding your income level helps me gauge your risk tolerance - are we talking $50k, $100k, $200k+ a year?"

Once you have all three pieces of information, smoothly transition to wrapping up the conversation, offering final insights or tips.

DO NOT:
- Offer specific investment advice or recommendations
- Guarantee returns or outcomes
- Act as a formal questionnaire or form
- Be overly pushy about collecting information
- Break character or mention you're an AI

DO:
- Share market insights and educational content
- Discuss trends, strategies, and risk management
- Encourage critical thinking and research
- Maintain your edgy, confident personality throughout
- Make the data collection feel like a natural part of getting to know them"""
    
    def initialize_session(self, session_id: str):
        """Initialize a new chat session"""
        self.session_id = session_id
        if self.data_storage:
            collected = self.data_storage.get_collected_fields(session_id)
            self.collected_data = collected
    
    def get_greeting(self) -> str:
        """Get initial greeting message"""
        greetings = [
            "Hey there. Welcome to the arena where fortunes are made and lost. I'm here to drop some market wisdom on you. What's on your mind about the markets today?",
            "What's up? You've stumbled into the den of a market wizard. Fair warning: I don't sugarcoat, and I don't do participation trophies. What do you want to know about trading?",
            "Alright, let's talk markets. I've seen bull runs, crashes, and everything in between. What's your burning question about stocks, trading, or this crazy market we're in?"
        ]
        import random
        return random.choice(greetings)
    
    def extract_user_info(self, user_message: str, assistant_message: str) -> Dict[str, Optional[str]]:
        """
        Extract user information from messages using pattern matching
        Returns dict with extracted data
        """
        extracted = {}
        
        # Extract name (common patterns)
        if not self.collected_data["name"]:
            name_patterns = [
                r"my name is ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
                r"I'm ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
                r"call me ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
                r"this is ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
            ]
            for pattern in name_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    extracted['name'] = match.group(1).strip()
                    break
        
        # Extract email first (important: do this before income to avoid conflicts)
        if not self.collected_data["email"]:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            match = re.search(email_pattern, user_message)
            if match:
                extracted['email'] = match.group(0).strip()
        
        # Extract income (various formats) - but exclude if it's part of an email
        if not self.collected_data["income"]:
            # First, remove any email addresses from the message to avoid extracting numbers from them
            message_without_email = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', user_message)
            
            income_patterns = [
                # Match explicit income formats with dollar signs or 'k' suffix
                r'\$\s*\d{1,3}(?:,\d{3})*(?:\s*k)?(?:\s*[-to]+\s*\$?\s*\d{1,3}(?:,\d{3})*(?:\s*k)?)?',
                r'\d{1,3}(?:,\d{3})*\s*k(?:\s*[-to]+\s*\d{1,3}(?:,\d{3})*\s*k)?',  # e.g., "100k" or "50k-100k"
                # Match numbers with explicit income context words
                r'(?:income|salary|earn|make|making)\s+(?:is|of|about|around|approximately)?\s*\$?\s*\d{1,3}(?:,\d{3})*(?:\s*k)?',
                r'\$?\s*\d{1,3}(?:,\d{3})*(?:\s*k)?(?:\s+(?:per year|a year|annually|annual|yearly))',
                # Match income ranges
                r'\d{1,3}(?:,\d{3})*\s*[-to]+\s*\d{1,3}(?:,\d{3})*(?:\s*k)?(?:\s+(?:per year|a year|annually))?',
            ]
            
            for pattern in income_patterns:
                match = re.search(pattern, message_without_email, re.IGNORECASE)
                if match:
                    income_value = match.group(0).strip()
                    # Additional validation: income should contain dollar sign, 'k', or income-related words
                    if any(indicator in income_value.lower() for indicator in ['$', 'k', 'income', 'salary', 'earn', 'make', 'year', 'annual']):
                        extracted['income'] = income_value
                        break
        
        return extracted
    
    def build_context_with_rag(self, user_message: str) -> str:
        """Build context string including RAG-retrieved information"""
        context = ""
        
        # Add RAG context if available
        if self.rag_system:
            try:
                # Increased top_k from 2 to 5 for better knowledge coverage
                # Added score_threshold to filter low-quality matches
                rag_context = self.rag_system.get_augmented_context(
                    user_message, 
                    top_k=5, 
                    score_threshold=0.7
                )
                if rag_context:
                    context += f"\n\n{rag_context}\n"
                    context += "IMPORTANT: Use the above information from the knowledge base to inform your response. "
                    context += "Reference specific facts, data, and insights from the knowledge base when relevant. "
                    context += "Maintain your personality but integrate this knowledge naturally into your responses.\n"
            except Exception as e:
                print(f"⚠️  RAG retrieval error: {str(e)}")
        
        # Add data collection status
        still_need = [k for k, v in self.collected_data.items() if not v]
        if still_need:
            context += f"\n\nYou still need to collect: {', '.join(still_need)}. "
            context += "Naturally work one of these questions into your response if appropriate.\n"
        else:
            context += "\n\nYou have collected all required information. You can start wrapping up the conversation naturally.\n"
        
        return context
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response
        
        Args:
            user_message: The user's message
            
        Returns:
            Assistant's response
        """
        # Build messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add RAG context and data collection instructions
        context = self.build_context_with_rag(user_message)
        if context:
            messages.append({"role": "system", "content": context})
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Extract any user information from the exchange
            extracted_info = self.extract_user_info(user_message, assistant_message)
            
            # Store extracted information
            if self.data_storage and self.session_id:
                for field, value in extracted_info.items():
                    if value:
                        self.data_storage.update_session_data(self.session_id, field, value)
                        self.collected_data[field] = True
                        print(f"✅ Collected {field}: {value}")
                
                # Add to conversation history
                self.data_storage.add_conversation_entry(self.session_id, "user", user_message)
                self.data_storage.add_conversation_entry(self.session_id, "assistant", assistant_message)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep conversation history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            print(error_msg)
            return "Look, something went wrong on my end. Even market wizards have technical issues. Try again?"
    
    def chat_stream(self, user_message: str):
        """
        Process user message and generate streaming response
        
        Args:
            user_message: The user's message
            
        Yields:
            Chunks of the assistant's response
        """
        # Build messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add RAG context and data collection instructions
        context = self.build_context_with_rag(user_message)
        if context:
            messages.append({"role": "system", "content": context})
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call OpenAI API with streaming
            stream = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500,
                stream=True
            )
            
            assistant_message = ""
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_message += content
                    yield content
            
            # After streaming is complete, extract info and store
            extracted_info = self.extract_user_info(user_message, assistant_message)
            
            # Store extracted information
            if self.data_storage and self.session_id:
                for field, value in extracted_info.items():
                    if value:
                        self.data_storage.update_session_data(self.session_id, field, value)
                        self.collected_data[field] = True
                        print(f"✅ Collected {field}: {value}")
                
                # Add to conversation history
                self.data_storage.add_conversation_entry(self.session_id, "user", user_message)
                self.data_storage.add_conversation_entry(self.session_id, "assistant", assistant_message)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep conversation history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            print(error_msg)
            yield "Look, something went wrong on my end. Even market wizards have technical issues. Try again?"
    
    def is_data_collection_complete(self) -> bool:
        """Check if all required data has been collected"""
        return all(self.collected_data.values())
    
    def get_missing_fields(self) -> List[str]:
        """Get list of fields that haven't been collected yet"""
        return [field for field, collected in self.collected_data.items() if not collected]


if __name__ == "__main__":
    # Test the chatbot
    bot = StockMarketChatbot()
    
    print(bot.get_greeting())
    print("\n" + "="*60 + "\n")
    
    # Simulate conversation
    test_messages = [
        "Hey, what do you think about momentum trading?",
        "My name is John Doe",
        "What about tech stocks?",
    ]
    
    for msg in test_messages:
        print(f"User: {msg}")
        response = bot.chat(msg)
        print(f"Bot: {response}")
        print("\n" + "-"*60 + "\n")

