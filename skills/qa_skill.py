import wikipedia
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QASkill:
   

    def __init__(self):
        
        try:
            # Set Wikipedia language to English
            wikipedia.set_lang("en")
            logger.info("Wikipedia API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Wikipedia API: {e}")

    def answer_question(self, query):
       
        if not query or not query.strip():
            return False, "Please provide a question or search query"

        try:
            logger.info(f"Searching Wikipedia for: '{query}'")

            # Search for the query
            search_results = wikipedia.search(query, results=3)

            if not search_results:
                return False, f"No Wikipedia articles found for '{query}'. Please try rephrasing your question."

            # Get the most relevant result (first one)
            page_title = search_results[0]

            try:
                # Get page summary
                summary = wikipedia.summary(page_title, sentences=3)

                # Clean up the summary
                clean_answer = self._clean_wikipedia_text(summary)

                logger.info(f"Found answer for '{query}': {clean_answer[:100]}...")
                return True, clean_answer

            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation (multiple possible pages)
                options = e.options[:3]  # Limit to first 3 options
                return False, f"Multiple results found for '{query}'. Did you mean: {', '.join(options)}?"

            except wikipedia.exceptions.PageError:
                # Try the next search result if the first one fails
                if len(search_results) > 1:
                    try:
                        page_title = search_results[1]
                        summary = wikipedia.summary(page_title, sentences=3)
                        clean_answer = self._clean_wikipedia_text(summary)
                        return True, clean_answer
                    except:
                        return False, f"Could not retrieve information for '{query}'. Please try a different query."

                return False, f"Could not find information for '{query}'."

        except wikipedia.exceptions.WikipediaException as e:
            logger.error(f"Wikipedia API error: {e}")
            return False, "Wikipedia service is currently unavailable. Please try again later."

        except Exception as e:
            logger.error(f"Unexpected error in Q&A: {e}")
            return False, f"An unexpected error occurred while searching: {str(e)}"

    def _clean_wikipedia_text(self, text):
        
        if not text:
            return ""

        # Remove extra whitespace
        cleaned = ' '.join(text.split())

        # Remove reference numbers like [1], [2], etc.
        import re
        cleaned = re.sub(r'\[\d+\]', '', cleaned)

        # Fix common formatting issues
        cleaned = cleaned.replace(' .', '.')
        cleaned = cleaned.replace(' ,', ',')

        # Ensure proper sentence spacing
        cleaned = re.sub(r'([.!?])([A-Z])', r'\1 \2', cleaned)

        return cleaned.strip()

    def get_suggestions(self, query):
        
        try:
            suggestions = wikipedia.search(query, results=5)
            return suggestions
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []

    def get_random_fact(self):
        
        try:
            # Get a random page title
            random_title = wikipedia.random(pages=1)[0]

            # Get summary
            summary = wikipedia.summary(random_title, sentences=2)
            clean_fact = self._clean_wikipedia_text(summary)

            return True, f"Did you know? {clean_fact}"

        except Exception as e:
            logger.error(f"Error getting random fact: {e}")
            return False, "Unable to fetch a random fact right now."

    def search_and_summarize(self, query, max_sentences=3):
       
        try:
            # Search for the most relevant page
            search_results = wikipedia.search(query, results=1)

            if not search_results:
                return False, f"No information found for '{query}'"

            page_title = search_results[0]

            # Get detailed summary
            summary = wikipedia.summary(page_title, sentences=max_sentences)
            clean_summary = self._clean_wikipedia_text(summary)

            return True, clean_summary

        except Exception as e:
            logger.error(f"Error in detailed search: {e}")
            return False, f"Unable to get detailed information for '{query}'"

    def _is_identity_question(self, query):
       
        if not query:
            return False

        query_lower = query.lower()

        # Common identity questions
        identity_keywords = [
            'what is your name',
            'who are you',
            'what are you',
            'your name',
            'who made you',
            'who created you',
            'who developed you',
            'who built you',
            'tell me about yourself'
        ]

        return any(keyword in query_lower for keyword in identity_keywords)

    def _is_time_question(self, query):
        
        if not query:
            return False

        query_lower = query.lower()

        # Common time/date questions
        time_keywords = [
            'what time is it',
            'what is the time',
            'current time',
            'time now',
            'what is today',
            'today date',
            'current date',
            'what day is it',
            'what is the date'
        ]

        return any(keyword in query_lower for keyword in time_keywords)

    def _handle_identity_question(self, query):
       
        return True, "I am Vishnu, your personal voice assistant. I was developed by Vishnu to help you with various tasks like sending emails, setting reminders, checking weather, playing music, and answering questions."

    def _handle_time_question(self, query):
     
        try:
            now = datetime.now()

            # Format date and time
            current_date = now.strftime("%A, %B %d, %Y")
            current_time = now.strftime("%I:%M %p")

            return True, f"Today is {current_date}. The current time is {current_time}."

        except Exception as e:
            logger.error(f"Error getting current time: {e}")
            return False, "Sorry, I couldn't get the current time right now."

    def answer_special_questions(self, query):
    
        if self._is_identity_question(query):
            success, answer = self._handle_identity_question(query)
            return success, answer, True

        elif self._is_time_question(query):
            success, answer = self._handle_time_question(query)
            return success, answer, True

        return False, "", False
