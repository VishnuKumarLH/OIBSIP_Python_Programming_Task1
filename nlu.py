import re
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
   
    def __init__(self):
       
        self.wake_words = ["vishnu", "hey vishnu", "assistant"]
        self.intent_patterns = {
            'reminder': [
                r'\bremind\b',
                r'\breminder\b',
                r'\balarm\b',
                r'\bnotify\b',
                r'\balert\b',
                r'\bremind\s+me\b',
                r'\bset\s+reminder\b',
                r'\bcreate\s+reminder\b',
                r'\bmake\s+reminder\b',
                r'\bset\s+alarm\b',
                r'\bcreate\s+alarm\b'
            ],
            'email': [
                r'\bemail\s+(?:to|about|regarding)',
                r'\bsend\s+email\b',
                r'\bcompose\s+email\b',
                r'\bwrite\s+email\b',
                r'\bmail\s+(?:to|about|regarding)',
                r'\bmessage\s+(?:to|about|regarding)'
            ],
            'weather': [
                r'\bweather\b',
                r'\btemperature\b',
                r'\bforecast\b',
                r'\bclimate\b',
                r'\bdegrees?\b'
            ],
            'system': [
                r'\bopen\b',
                r'\blaunch\b',
                r'\bstart\b',
                r'\brun\b',
                r'\bplay\b',
                r'\bwatch\b',
                r'\bsearch\b',
                r'\bgoogle\b',
                r'\bexit\b',
                r'\bquit\b',
                r'\bstop\b',
                r'\bshutdown\b',
                r'\bclose\b',
                r'\bturn\s+off\b'
            ],
            'greeting': [
                r'\bgood\s+morning\b',
                r'\bgood\s+afternoon\b',
                r'\bgood\s+evening\b',
                r'\bgood\s+night\b',
                r'\bhello\b',
                r'\bhi\b',
                r'\bhey\b',
                r'\bhowdy\b',
                r'\bgreetings\b',
                r'\bnamaste\b',
                r'\bsup\b',
                r'\bwhat\'s\s+up\b'
            ],
            'qa': []  # Default fallback for any other queries
        }

        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for intent, patterns in self.intent_patterns.items():
            self.compiled_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def has_wake_word(self, text):
      
        if not text:
            return False

        text_lower = text.lower().strip()
        return any(wake_word in text_lower for wake_word in self.wake_words)

    def remove_wake_word(self, text):
       
        if not text:
            return text

        text_lower = text.lower()

        # Remove all wake words from the text
        for wake_word in self.wake_words:
            wake_word_lower = wake_word.lower()
            # Remove wake word from beginning
            if text_lower.startswith(wake_word_lower):
                text = text[len(wake_word):].strip()
                text_lower = text.lower()
            # Remove wake word from middle
            text = text_lower.replace(wake_word_lower, '').strip()

        return text

    def is_wake_word_only(self, text):
      
        if not text:
            return False

        # Remove all wake words from the text
        clean_text = self.remove_wake_word(text)

        # If there's no text left after removing wake words, it's wake word only
        return not clean_text or not clean_text.strip()

    def classify_intent(self, text):
        
        if not text or not text.strip():
            return 'qa', 0.0, {}

        text_lower = text.lower()

        # Check each intent pattern
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(text_lower)
                if match:
                    # Extract relevant information based on intent
                    extracted_info = self._extract_info(intent, text_lower, match)
                    logger.info(f"Classified as '{intent}' with confidence 1.0")
                    return intent, 1.0, extracted_info

        # Default to Q&A if no specific intent matches
        logger.info("No specific intent matched, defaulting to 'qa'")
        return 'qa', 0.5, {}

    def _extract_info(self, intent, text, match):
        
        info = {}

        if intent == 'email':
            # Extract email components
            info = self._extract_email_info(text)

        elif intent == 'reminder':
            # Extract reminder components
            info = self._extract_reminder_info(text)

        elif intent == 'weather':
            # Extract location for weather
            info = self._extract_weather_info(text)

        elif intent == 'system':
            # Extract system command information
            info = self._extract_system_info(text)

        return info

    def _extract_system_info(self, text):
       
        info = {}

        # Check for exit commands first
        exit_commands = ['exit', 'quit', 'stop', 'shutdown', 'bye', 'goodbye', 'close', 'turn off', 'shut down']
        text_lower = text.lower()
        for exit_cmd in exit_commands:
            if exit_cmd in text_lower:
                info['exit'] = True
                break

        # Extract application name
        app_patterns = [
            r'\bopen\s+([a-zA-Z\s]+)',
            r'\blaunch\s+([a-zA-Z\s]+)',
            r'\bstart\s+([a-zA-Z\s]+)',
            r'\brun\s+([a-zA-Z\s]+)'
        ]

        for pattern in app_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
                if app_name:
                    info['application'] = app_name
                break

        # Extract YouTube query
        youtube_patterns = [
            r'\bplay\s+(?:youtube\s+)?(.+)',
            r'\bwatch\s+(?:youtube\s+)?(.+)',
            r'\bplay\s+videos?\s+(?:in\s+)?(?:youtube\s+)?(.+)',
            r'\bplay\s+(?:in\s+)?youtube\s+(.+)'
        ]

        for pattern in youtube_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                if query:
                    info['youtube_query'] = query
                break

        # Extract video query (for "play videos in youtube" commands)
        video_patterns = [
            r'\bplay\s+videos?\s+(?:in\s+)?(?:youtube\s+)?(.+)',
            r'\bplay\s+(?:in\s+)?youtube\s+(.+)',
            r'\bwatch\s+videos?\s+(?:in\s+)?(?:youtube\s+)?(.+)'
        ]

        for pattern in video_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                video_query = match.group(1).strip()
                if video_query:
                    info['video_query'] = video_query
                break

        # Extract song name
        song_patterns = [
            r'\bplay\s+song\s+(.+)',
            r'\bplay\s+(.+?)\s+song',
            r'\blisten\s+to\s+(.+)'
        ]

        for pattern in song_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                song_name = match.group(1).strip()
                if song_name:
                    info['song_name'] = song_name
                break

        # Extract search query
        search_patterns = [
            r'\bsearch\s+(?:for\s+)?(.+)',
            r'\bgoogle\s+(.+)',
            r'\blook\s+up\s+(.+)'
        ]

        for pattern in search_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                search_query = match.group(1).strip()
                if search_query:
                    info['search_query'] = search_query
                break

        return info

    def _extract_email_info(self, text):
        
        info = {}

        # First try to find complete email addresses with @ symbol
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        emails = re.findall(email_pattern, text)

        if emails:
            info['recipient'] = emails[0]  # Take first email found
            logger.info(f"Found complete email address: {emails[0]}")

        # Handle speech recognition errors where @ might be missing or replaced
        if 'recipient' not in info:
            reconstructed_email = self._reconstruct_email_from_speech(text)
            if reconstructed_email:
                info['recipient'] = reconstructed_email
                logger.info(f"Reconstructed email from speech: {reconstructed_email}")

        # Look for subject (after "about", "regarding", etc.)
        subject_patterns = [
            r'(?:about|regarding|subject)\s*[:\-]?\s*([^\.,;!?]+)',
            r'subject\s*[:\-]?\s*([^\.,;!?]+)',
            r'with\s+subject\s*[:\-]?\s*([^\.,;!?]+)'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                if subject and len(subject) > 2:
                    info['subject'] = subject
                    logger.info(f"Found email subject: {subject}")
                break

        # Extract body (everything after common separators)
        body_separators = ['about', 'regarding', 'subject', 'message', 'body', 'content']
        body_text = text

        for separator in body_separators:
            if separator in text.lower():
                parts = text.lower().split(separator, 1)
                if len(parts) > 1:
                    body_text = parts[1].strip(' :-.')
                    break

        # Clean up the body text
        if body_text and len(body_text) > 5:
            # Remove email addresses from body if present
            body_text = re.sub(email_pattern, '', body_text)
            body_text = body_text.strip(' :-.!?')
            if body_text:
                info['body'] = body_text
                logger.info(f"Found email body: {body_text}")

        # If no body found, use the entire text as body
        if 'body' not in info and text.strip():
            clean_text = re.sub(email_pattern, '', text).strip(' :-.!?')
            if clean_text and len(clean_text) > 5:
                info['body'] = clean_text
                logger.info(f"Using full text as email body: {clean_text}")

        return info

    def _reconstruct_email_from_speech(self, text):
       
        text_lower = text.lower()
        logger.info(f"Attempting to reconstruct email from: '{text}'")

        # Common speech recognition errors for @ symbol
        at_replacements = [' at ', ' add ', ' and ', ' et ', ' @ ', ' at', ' add', ' and', ' et', ' @']

        # Common email domains that might be mentioned separately
        common_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'protonmail.com', 'mail.com', 'yandex.com', 'zoho.com',
            'inbox.com', 'live.com', 'msn.com', 'me.com', 'mac.com'
        ]

        # Method 1: Handle "username at domain" patterns
        for replacement in at_replacements:
            if replacement in text_lower:
                parts = text_lower.split(replacement, 1)
                if len(parts) == 2:
                    username_part = parts[0].strip()
                    domain_part = parts[1].strip()

                    # Extract username from the end of the first part (most likely the actual username)
                    username_words = username_part.split()
                    if username_words:
                        # Skip command words and take the last meaningful word as username
                        command_words = ['email', 'send', 'compose', 'write', 'mail', 'message', 'to']
                        meaningful_words = [word for word in username_words if word not in command_words]

                        if meaningful_words:
                            # Take the last meaningful word as the username
                            potential_username = meaningful_words[-1]
                            # Clean up the username
                            username = re.sub(r'[^\w.]', '', potential_username).strip('.')

                            # Try to extract domain from domain part
                            domain = self._extract_domain_from_text(domain_part, common_domains)

                            if username and domain:
                                reconstructed = f"{username}@{domain}"
                                logger.info(f"Reconstructed email: {username}@{domain} from '{username_part}' + '{replacement}' + '{domain_part}'")
                                return reconstructed

                        # If no meaningful words found, try to reconstruct from the entire username part
                        # This handles cases like "john doe" where we need to combine words
                        if len(username_words) >= 2:
                            # Look for patterns like "firstname lastname" and combine them
                            # Skip command words and combine the remaining words
                            non_command_words = [word for word in username_words if word not in command_words]
                            if len(non_command_words) >= 2:
                                # Combine the last two non-command words (e.g., "john doe" -> "johndoe")
                                combined_username = ''.join(non_command_words[-2:])
                                username = re.sub(r'[^\w.]', '', combined_username).strip('.')

                                domain = self._extract_domain_from_text(domain_part, common_domains)

                                if username and domain:
                                    reconstructed = f"{username}@{domain}"
                                    logger.info(f"Reconstructed email from combined words: {username}@{domain}")
                                    return reconstructed

        # Method 2: Handle "username domain" patterns (missing @)
        words = text_lower.split()
        for i, word in enumerate(words):
            # Look for potential username followed by domain parts
            if i < len(words) - 1:
                # Skip common email command words
                skip_words = ['email', 'send', 'compose', 'write', 'mail', 'message', 'to']
                if word in skip_words:
                    continue

                potential_username = re.sub(r'[^\w.]', '', word).strip('.')
                remaining_text = ' '.join(words[i+1:])

                # Check if remaining text contains domain-like words
                for domain in common_domains:
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        # Check if domain parts appear in remaining text
                        domain_found = True
                        for part in domain_parts:
                            if part not in remaining_text:
                                domain_found = False
                                break

                        if domain_found and potential_username:
                            reconstructed = f"{potential_username}@{domain}"
                            logger.info(f"Reconstructed email from word pattern: {reconstructed}")
                            return reconstructed

        # Method 3: Handle cases where domain appears before username
        # Look for domain patterns first, then find username before it
        for domain in common_domains:
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # Check if domain parts appear in the text
                domain_found = True
                for part in domain_parts:
                    if part not in text_lower:
                        domain_found = False
                        break

                if domain_found:
                    # Find the word before the domain
                    domain_pos = text_lower.find(domain_parts[0])
                    if domain_pos > 0:
                        # Get text before domain
                        before_domain = text_lower[:domain_pos].strip()
                        before_words = before_domain.split()

                        if before_words:
                            # Take the last word before domain as username
                            potential_username = before_words[-1]
                            username = re.sub(r'[^\w.]', '', potential_username).strip('.')

                            if username:
                                reconstructed = f"{username}@{domain}"
                                logger.info(f"Reconstructed email from domain-first pattern: {reconstructed}")
                                return reconstructed

        # Method 4: Enhanced pattern matching for complex cases
        # Look for patterns like "to X at Y" where X is the username
        patterns = [
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+at\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+add\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+and\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                username_part = match.group(1).strip()
                domain_part = match.group(2).strip()

                # Clean username (remove spaces and special chars)
                username = re.sub(r'[^\w.]', '', username_part.replace(' ', '')).strip('.')

                # Check if domain is in our common domains list
                domain = None
                for common_domain in common_domains:
                    if common_domain in domain_part:
                        domain = common_domain
                        break

                if not domain:
                    domain = domain_part  # Use as-is if not in common list

                if username and domain:
                    reconstructed = f"{username}@{domain}"
                    logger.info(f"Reconstructed email from enhanced pattern: {reconstructed}")
                    return reconstructed

        # Method 5: More flexible pattern matching for edge cases
        # Handle cases where the command words are interfering
        flexible_patterns = [
            r'\b([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+at\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\b([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+add\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\b([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+and\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]

        for pattern in flexible_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                username_part = match.group(1).strip()
                domain_part = match.group(2).strip()

                # Skip if this looks like a command word
                command_indicators = ['email', 'send', 'compose', 'write', 'mail', 'message']
                if username_part in command_indicators:
                    continue

                # Clean username (remove spaces and special chars)
                username = re.sub(r'[^\w.]', '', username_part.replace(' ', '')).strip('.')

                # Check if domain is in our common domains list
                domain = None
                for common_domain in common_domains:
                    if common_domain in domain_part:
                        domain = common_domain
                        break

                if not domain:
                    domain = domain_part  # Use as-is if not in common list

                if username and domain and len(username) > 1:
                    reconstructed = f"{username}@{domain}"
                    logger.info(f"Reconstructed email from flexible pattern: {reconstructed}")
                    return reconstructed

        # Method 6: Last resort - try to find any word + domain pattern
        # This is a fallback for cases where other methods fail
        logger.info("Trying last resort method...")
        words = text_lower.split()
        for i, word in enumerate(words):
            # Skip command words
            if word in ['email', 'send', 'compose', 'write', 'mail', 'message', 'to']:
                continue

            # Check if this word could be a username (not a domain part)
            if not any(domain_part in word for domain_part in ['.com', '.org', '.net', '.edu', '.gov']):
                # Look ahead for domain-like words
                for j in range(i + 1, min(i + 3, len(words))):  # Look at next 2 words
                    potential_domain = words[j]
                    # Check if it looks like a domain
                    if '.' in potential_domain and len(potential_domain) > 3:
                        # Check if domain is in our common domains list
                        domain = None
                        for common_domain in common_domains:
                            if common_domain in potential_domain:
                                domain = common_domain
                                break

                        if not domain:
                            domain = potential_domain  # Use as-is if not in common list

                        if domain:
                            username = re.sub(r'[^\w.]', '', word).strip('.')
                            if username and len(username) > 1:
                                reconstructed = f"{username}@{domain}"
                                logger.info(f"Reconstructed email from last resort pattern: {reconstructed}")
                                return reconstructed

        # Method 7: Ultimate fallback - look for any pattern that might work
        logger.info("Trying ultimate fallback method...")
        # Try to find patterns like "X at Y" or "X add Y" anywhere in the text
        ultimate_patterns = [
            r'(\w+)\s+at\s+(\w+\.\w+)',
            r'(\w+)\s+add\s+(\w+\.\w+)',
            r'(\w+)\s+and\s+(\w+\.\w+)'
        ]

        for pattern in ultimate_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                username = match.group(1).strip()
                domain = match.group(2).strip()

                # Skip if username looks like a command word
                if username not in ['email', 'send', 'compose', 'write', 'mail', 'message', 'to']:
                    # Check if domain is in our common domains list
                    actual_domain = None
                    for common_domain in common_domains:
                        if common_domain in domain:
                            actual_domain = common_domain
                            break

                    if not actual_domain:
                        actual_domain = domain  # Use as-is if not in common list

                    if username and actual_domain and len(username) > 1:
                        reconstructed = f"{username}@{actual_domain}"
                        logger.info(f"Reconstructed email from ultimate fallback: {reconstructed}")
                        return reconstructed

        # Method 8: Debug the specific failing cases
        logger.info("Trying debug method for specific failing cases...")
        # For "send email to john doe at company.com" - the issue is "john doe" should become "johndoe"
        # Let's try a more specific approach for multi-word usernames
        debug_patterns = [
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+at\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+add\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'\bto\s+([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)\s+and\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]

        for pattern in debug_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                username_part = match.group(1).strip()
                domain_part = match.group(2).strip()

                logger.info(f"Debug pattern matched: username_part='{username_part}', domain_part='{domain_part}'")

                # Clean username (remove spaces and special chars)
                username = re.sub(r'[^\w.]', '', username_part.replace(' ', '')).strip('.')

                # Check if domain is in our common domains list
                domain = None
                for common_domain in common_domains:
                    if common_domain in domain_part:
                        domain = common_domain
                        break

                if not domain:
                    domain = domain_part  # Use as-is if not in common list

                if username and domain and len(username) > 1:
                    reconstructed = f"{username}@{domain}"
                    logger.info(f"Reconstructed email from debug pattern: {reconstructed}")
                    return reconstructed

        return None

    def _extract_domain_from_text(self, text, common_domains):
    
        text_lower = text.lower()

        # First try exact matches
        for domain in common_domains:
            if domain in text_lower:
                return domain

        # Try partial matches (e.g., "gmail" -> "gmail.com")
        domain_starters = {}
        for domain in common_domains:
            main_part = domain.split('.')[0]
            if main_part in domain_starters:
                domain_starters[main_part].append(domain)
            else:
                domain_starters[main_part] = [domain]

        for starter, domains in domain_starters.items():
            if starter in text_lower:
                # Return the most common domain for this starter
                return domains[0]  # Usually gmail.com, yahoo.com, etc.

        return None

    def _extract_reminder_info(self, text):
       
        info = {}

        # Extract time information
        time_patterns = [
            r'in\s+(\d+)\s*(minutes?|mins?|hours?|hrs?)',
            r'(\d+)\s*(minutes?|mins?|hours?|hrs?)\s+from\s+now',
            r'at\s+(\d+):?(\d+)?\s*(am|pm)?'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'minute' in pattern or 'hour' in pattern:
                    amount = int(match.group(1))
                    unit = match.group(2).lower()
                    if 'hour' in unit:
                        info['hours'] = amount
                    else:
                        info['minutes'] = amount
                break

        # Extract reminder text (everything else)
        # Remove time-related parts
        clean_text = re.sub(r'\b(?:in|at|from)\s+[^,]*', '', text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\d+\s*(?:minutes?|mins?|hours?|hrs?)', '', clean_text, flags=re.IGNORECASE)
        clean_text = clean_text.strip(' ,.to')

        if clean_text:
            info['text'] = clean_text

        return info

    def _extract_weather_info(self, text):
        """Extract location for weather query."""
        info = {}

        # Common location patterns
        location_patterns = [
            r'in\s+([A-Za-z\s,]+)',
            r'at\s+([A-Za-z\s,]+)',
            r'for\s+([A-Za-z\s,]+)'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip(' ,.')
                if location and len(location) > 1:
                    info['city'] = location
                break

        # If no location found, try to extract any place names
        if 'city' not in info:
            words = text.split()
            # Look for capitalized words that might be place names
            potential_cities = [word.strip('.,') for word in words if word.istitle() and len(word) > 2]
            if potential_cities:
                info['city'] = potential_cities[0]

        return info
