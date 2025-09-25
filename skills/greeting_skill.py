import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

class GreetingSkill:
  
    def __init__(self):
      
        self.greeting_responses = {
            'good_morning': [
                "Good morning! I hope you have a wonderful day ahead!",
                "Good morning! How can I help you start your day?",
                "Good morning! I'm ready to assist you today.",
                "Good morning! What would you like me to do for you?"
            ],
            'good_afternoon': [
                "Good afternoon! How is your day going so far?",
                "Good afternoon! What can I help you with this afternoon?",
                "Good afternoon! I'm here to assist you.",
                "Good afternoon! How may I be of service?"
            ],
            'good_evening': [
                "Good evening! How was your day?",
                "Good evening! What can I help you with this evening?",
                "Good evening! I'm here to assist you.",
                "Good evening! How may I help you?"
            ],
            'good_night': [
                "Good night! Sleep well and have sweet dreams!",
                "Good night! Rest well and I'll be here when you wake up.",
                "Good night! Sweet dreams!",
                "Good night! Have a peaceful sleep."
            ],
            'hello': [
                "Hello! How can I help you today?",
                "Hello! What would you like me to do for you?",
                "Hello! I'm here to assist you.",
                "Hello! How may I be of service?"
            ],
            'hi': [
                "Hi there! How can I help you?",
                "Hi! What would you like me to do?",
                "Hi! I'm ready to assist you.",
                "Hi! How may I help you today?"
            ],
            'hey': [
                "Hey! What's up? How can I help you?",
                "Hey! What can I do for you?",
                "Hey! I'm here to assist you.",
                "Hey! How may I be of service?"
            ],
            'howdy': [
                "Howdy! How can I help you today?",
                "Howdy partner! What would you like me to do?",
                "Howdy! I'm ready to assist you.",
                "Howdy! How may I be of service?"
            ],
            'greetings': [
                "Greetings! How can I assist you today?",
                "Greetings! What would you like me to do for you?",
                "Greetings! I'm here to help.",
                "Greetings! How may I be of service?"
            ],
            'namaste': [
                "Namaste! How can I help you today?",
                "Namaste! What would you like me to do for you?",
                "Namaste! I'm here to assist you.",
                "Namaste! How may I be of service?"
            ],
            'sup': [
                "Not much, just here to help! What can I do for you?",
                "Just hanging out and ready to assist! How can I help?",
                "Nothing much! What would you like me to do?",
                "Just waiting to help you! What's up?"
            ],
            'whats_up': [
                "Not much, just here to help! What about you?",
                "Just ready to assist you! What's going on?",
                "Nothing much! How can I help you today?",
                "Just waiting for your commands! What's up with you?"
            ]
        }

        # Time-based greeting detection
        self.time_greetings = {
            'morning': (6, 12),    # 6 AM to 12 PM
            'afternoon': (12, 17), # 12 PM to 5 PM
            'evening': (17, 21),   # 5 PM to 9 PM
            'night': (21, 6)       # 9 PM to 6 AM
        }

    def get_greeting_response(self, greeting_type, original_text=""):
      
        try:
            # Get responses for the specific greeting type
            responses = self.greeting_responses.get(greeting_type, self.greeting_responses['hello'])

            # Select a random response
            response = random.choice(responses)

            logger.info(f"Generated greeting response for '{greeting_type}': {response}")
            return True, response

        except Exception as e:
            logger.error(f"Error generating greeting response: {e}")
            return False, "Hello! How can I help you today?"

    def detect_time_based_greeting(self):
        
        try:
            current_hour = datetime.now().hour

            for greeting_type, (start_hour, end_hour) in self.time_greetings.items():
                if start_hour <= current_hour < end_hour:
                    return greeting_type
                elif greeting_type == 'night' and (current_hour >= 21 or current_hour < 6):
                    return greeting_type

            return 'hello'  # Default fallback

        except Exception as e:
            logger.error(f"Error detecting time-based greeting: {e}")
            return 'hello'

    def get_personalized_greeting(self, user_name=None):
     
        try:
            time_greeting = self.detect_time_based_greeting()

            if user_name:
                if time_greeting == 'good_morning':
                    response = f"Good morning, {user_name}! I hope you have a wonderful day ahead!"
                elif time_greeting == 'good_afternoon':
                    response = f"Good afternoon, {user_name}! How is your day going so far?"
                elif time_greeting == 'good_evening':
                    response = f"Good evening, {user_name}! How was your day?"
                elif time_greeting == 'good_night':
                    response = f"Good night, {user_name}! Sleep well and have sweet dreams!"
                else:
                    response = f"Hello, {user_name}! How can I help you today?"
            else:
                # Use time-based greeting without name
                success, response = self.get_greeting_response(f"good_{time_greeting}")
                return success, response

            logger.info(f"Generated personalized greeting: {response}")
            return True, response

        except Exception as e:
            logger.error(f"Error generating personalized greeting: {e}")
            return False, "Hello! How can I help you today?"

    def is_goodbye_greeting(self, text):
       
        if not text:
            return False

        text_lower = text.lower()

        goodbye_phrases = [
            'goodbye',
            'bye',
            'see you later',
            'farewell',
            'take care',
            'have a good day',
            'have a nice day',
            'good night'
        ]

        return any(phrase in text_lower for phrase in goodbye_phrases)

    def get_goodbye_response(self):
        
        try:
            goodbye_responses = [
                "Goodbye! Have a great day!",
                "Goodbye! Take care!",
                "Goodbye! See you later!",
                "Goodbye! Have a wonderful day!",
                "Goodbye! Stay safe!",
                "Goodbye! Until next time!"
            ]

            response = random.choice(goodbye_responses)
            logger.info(f"Generated goodbye response: {response}")
            return True, response

        except Exception as e:
            logger.error(f"Error generating goodbye response: {e}")
            return False, "Goodbye!"
