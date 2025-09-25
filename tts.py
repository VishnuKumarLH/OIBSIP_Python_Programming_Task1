import pyttsx3
import logging

logger = logging.getLogger(__name__)

class TextToSpeech:
 

    def __init__(self):
       
        try:
            self.engine = pyttsx3.init()
            # Configure voice properties
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def speak(self, text):
      
        if not self.engine:
            logger.error("TTS engine not initialized")
            return False

        if not text or not text.strip():
            logger.warning("Empty text provided to speak")
            return False

        try:
            logger.info(f"Speaking: '{text}'")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            return False

    def set_voice_rate(self, rate):
        
        if self.engine:
            self.engine.setProperty('rate', rate)
            logger.info(f"Speech rate set to {rate}")

    def set_volume(self, volume):
     
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            logger.info(f"Speech volume set to {volume}")

    def get_available_voices(self):
       
        if self.engine:
            try:
                voices = self.engine.getProperty('voices')
                return voices
            except Exception as e:
                logger.error(f"Error getting available voices: {e}")
                return []
        return []

    def set_voice(self, voice_id):
      
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
                logger.info(f"Voice set to {voice_id}")
            except Exception as e:
                logger.error(f"Error setting voice: {e}")

    def stop_speaking(self):
      
        if self.engine:
            try:
                self.engine.stop()
                logger.info("Speech stopped")
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")
