import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)

class VoiceRecognizer:
  

    def __init__(self):
      
        self.recognizer = sr.Recognizer()

    def listen_for_audio(self, timeout=5, phrase_time_limit=10):
        
        with sr.Microphone() as source:
            logger.info("Listening for audio...")
            try:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return audio
            except sr.WaitTimeoutError:
                logger.warning("No speech detected within timeout period")
                return None
            except Exception as e:
                logger.error(f"Error listening for audio: {e}")
                return None

    def recognize_speech(self, audio):
       
        if audio is None:
            return None

        try:
            logger.info("Recognizing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: '{text}'")
            return text.lower()  # Convert to lowercase for easier processing
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during speech recognition: {e}")
            return None

    def listen_and_recognize(self, timeout=5, phrase_time_limit=10):
       
        audio = self.listen_for_audio(timeout, phrase_time_limit)
        return self.recognize_speech(audio)
