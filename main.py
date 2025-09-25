
import logging
import time
import signal
import sys
from datetime import datetime

# Import core components
from recognizer import VoiceRecognizer
from tts import TextToSpeech
from nlu import IntentClassifier
from config import validate_config

# Import skills
from skills.email_skill import EmailSkill
from skills.reminder_skill import ReminderSkill
from skills.weather_skill import WeatherSkill
from skills.qa_skill import QASkill
from skills.system_skill import SystemSkill
from skills.greeting_skill import GreetingSkill

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VoiceAssistant:
   

    def __init__(self):
   
        logger.info("Initializing Mini Voice Assistant...")

        # Validate configuration
        try:
            validate_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            print(f"Configuration error: {e}")
            print("Please check your .env file and ensure all required variables are set.")
            sys.exit(1)

        # Initialize core components
        self.recognizer = VoiceRecognizer()
        self.tts = TextToSpeech()
        self.intent_classifier = IntentClassifier()

        # Initialize skills
        self.email_skill = EmailSkill()
        self.reminder_skill = ReminderSkill()
        self.weather_skill = WeatherSkill()
        self.qa_skill = QASkill()
        self.system_skill = SystemSkill()
        self.greeting_skill = GreetingSkill()

        # Track running state
        self.is_running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Voice Assistant initialized successfully")

    def _signal_handler(self, signum, frame):
       
        logger.info(f"Received signal {signum}. Shutting down...")
        self.stop()

    def start(self):
     
        logger.info("Starting Voice Assistant...")
        self.is_running = True

        # Welcome message
        welcome_msg = "Hello! I'm Vishnu, your voice assistant. Say 'Hey Vishnu' followed by your command. How can I help you today?"
        self.tts.speak(welcome_msg)
        print(f"🤖 {welcome_msg}")

        try:
            while self.is_running:
                self._process_voice_command()
                time.sleep(0.5)  # Small delay between listening attempts

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()

    def stop(self):
       
        logger.info("Stopping Voice Assistant...")
        self.is_running = False

        # Cleanup skills
        if hasattr(self, 'reminder_skill'):
            self.reminder_skill.shutdown()

        logger.info("Voice Assistant stopped")

    def _process_voice_command(self):
       
        try:
            # Listen for voice input
            print("\n🎤 Listening... (say something)")
            text = self.recognizer.listen_and_recognize(timeout=5, phrase_time_limit=10)

            if not text:
                return

            print(f"👤 You said: '{text}'")

            # Check if text contains only wake words
            if self.intent_classifier.is_wake_word_only(text):
                response = "Yes, I'm hearing. What can I do for you?"
                self.tts.speak(response)
                print(f"🤖 Assistant: {response}")
                return

            # Classify intent
            intent, confidence, extracted_info = self.intent_classifier.classify_intent(text)

            logger.info(f"Intent classified as: {intent} (confidence: {confidence})")
            logger.info(f"Extracted info: {extracted_info}")

            # Process the intent
            response = self._handle_intent(intent, extracted_info, text)

            # Speak the response
            if response:
                self.tts.speak(response)
                print(f"🤖 Assistant: {response}")

        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            error_msg = "Sorry, I encountered an error. Please try again."
            self.tts.speak(error_msg)
            print(f"🤖 Assistant: {error_msg}")

    def _handle_intent(self, intent, extracted_info, original_text):
        
        try:
            if intent == 'greeting':
                return self._handle_greeting_intent(original_text)

            elif intent == 'email':
                return self._handle_email_intent(extracted_info)

            elif intent == 'reminder':
                return self._handle_reminder_intent(extracted_info)

            elif intent == 'weather':
                return self._handle_weather_intent(extracted_info)

            elif intent == 'qa':
                return self._handle_qa_intent(original_text)

            elif intent == 'system':
                return self._handle_system_intent(extracted_info)

            else:
                return "I'm not sure how to help with that. You can ask me to send emails, set reminders, check weather, open applications, search, or ask questions."

        except Exception as e:
            logger.error(f"Error handling intent '{intent}': {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

    def _handle_email_intent(self, extracted_info):
       
        try:
            recipient = extracted_info.get('recipient')
            subject = extracted_info.get('subject', 'Voice Assistant Message')
            body = extracted_info.get('body', 'This message was sent via voice assistant.')

            if not recipient:
                return "I couldn't find an email address in your message. Please include the recipient's email address."

            success, message = self.email_skill.send_email(recipient, subject, body)

            if success:
                return f"Email sent successfully to {recipient}."
            else:
                return f"Failed to send email: {message}"

        except Exception as e:
            logger.error(f"Error in email handling: {e}")
            return "Sorry, I encountered an error while sending the email."

    def _handle_reminder_intent(self, extracted_info):
       
        try:
            reminder_text = extracted_info.get('text')
            minutes = extracted_info.get('minutes')
            hours = extracted_info.get('hours')

            if not reminder_text:
                return "Please tell me what you want to be reminded about."

            if not minutes and not hours:
                return "Please specify when you want to be reminded (e.g., 'in 10 minutes' or 'in 2 hours')."

            success, message, reminder_id = self.reminder_skill.set_reminder(
                reminder_text, minutes=minutes, hours=hours
            )

            if success:
                return message
            else:
                return f"Failed to set reminder: {message}"

        except Exception as e:
            logger.error(f"Error in reminder handling: {e}")
            return "Sorry, I encountered an error while setting the reminder."

    def _handle_weather_intent(self, extracted_info):
       
        try:
            city = extracted_info.get('city')

            if not city:
                return "Please specify a city name for the weather information."

            success, message = self.weather_skill.get_weather(city)

            if success:
                return message
            else:
                return f"Unable to get weather information: {message}"

        except Exception as e:
            logger.error(f"Error in weather handling: {e}")
            return "Sorry, I encountered an error while fetching weather information."

    def _handle_qa_intent(self, query):
      
        try:
            # First check for special questions (identity, time/date)
            success, answer, is_special = self.qa_skill.answer_special_questions(query)

            if is_special:
                if success:
                    return answer
                else:
                    return f"Sorry, I encountered an error: {answer}"

            # Fall back to Wikipedia search for other questions
            success, answer = self.qa_skill.answer_question(query)

            if success:
                return answer
            else:
                return f"I couldn't find information about that. {answer}"

        except Exception as e:
            logger.error(f"Error in Q&A handling: {e}")
            return "Sorry, I encountered an error while searching for information."

    def _handle_system_intent(self, extracted_info):
     
        try:
            # Check for exit command
            if extracted_info.get('exit'):
                self.stop()
                return "Goodbye! Vishnu is shutting down."

            # Handle application opening
            application = extracted_info.get('application')
            if application:
                success, message = self.system_skill.open_application(application)
                if success:
                    return f"Opening {application}."
                else:
                    return f"Failed to open {application}: {message}"

            # Handle YouTube search
            youtube_query = extracted_info.get('youtube_query')
            if youtube_query:
                success, message = self.system_skill.play_youtube_video(youtube_query)
                if success:
                    return f"Playing '{youtube_query}' on YouTube."
                else:
                    return f"Failed to play YouTube video: {message}"

            # Handle video requests (for "play videos in youtube" commands)
            video_query = extracted_info.get('video_query')
            if video_query:
                success, message = self.system_skill.play_video_on_youtube(video_query)
                if success:
                    return f"Playing '{video_query}' on YouTube."
                else:
                    return f"Failed to play video: {message}"

            # Handle song playing
            song_name = extracted_info.get('song_name')
            if song_name:
                success, message = self.system_skill.play_song(song_name)
                if success:
                    return f"Playing {song_name}."
                else:
                    return f"Failed to play song: {message}"

            # Handle web search
            search_query = extracted_info.get('search_query')
            if search_query:
                success, message = self.system_skill.search_web(search_query)
                if success:
                    return f"Searching for '{search_query}'."
                else:
                    return f"Failed to search: {message}"

            return "I can help you open applications, play YouTube videos, play songs, or search the web. What would you like me to do?"

        except Exception as e:
            logger.error(f"Error in system handling: {e}")
            return "Sorry, I encountered an error while processing the system command."

    def _handle_greeting_intent(self, original_text):
      
        try:
            # Determine the greeting type from the original text
            text_lower = original_text.lower()

            if 'good morning' in text_lower:
                greeting_type = 'good_morning'
            elif 'good afternoon' in text_lower:
                greeting_type = 'good_afternoon'
            elif 'good evening' in text_lower:
                greeting_type = 'good_evening'
            elif 'good night' in text_lower:
                greeting_type = 'good_night'
            elif 'hello' in text_lower:
                greeting_type = 'hello'
            elif 'hi' in text_lower:
                greeting_type = 'hi'
            elif 'hey' in text_lower:
                greeting_type = 'hey'
            elif 'howdy' in text_lower:
                greeting_type = 'howdy'
            elif 'greetings' in text_lower:
                greeting_type = 'greetings'
            elif 'namaste' in text_lower:
                greeting_type = 'namaste'
            elif 'sup' in text_lower or 'what\'s up' in text_lower:
                greeting_type = 'sup'
            else:
                greeting_type = 'hello'  # Default fallback

            success, response = self.greeting_skill.get_greeting_response(greeting_type, original_text)

            if success:
                return response
            else:
                return "Hello! How can I help you today?"

        except Exception as e:
            logger.error(f"Error in greeting handling: {e}")
            return "Hello! How can I help you today?"

def main():
   
    try:
        assistant = VoiceAssistant()
        assistant.start()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
