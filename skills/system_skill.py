import os
import subprocess
import webbrowser
import logging
import re

logger = logging.getLogger(__name__)

class SystemSkill:
  

    def __init__(self):
   
        self.exit_commands = ['exit', 'quit', 'stop', 'shutdown', 'bye', 'goodbye']
        # Use Windows commands that work regardless of installation paths
        self.application_commands = {
            'chrome': 'start chrome',
            'edge': 'start msedge',
            'calculator': 'calc',
            'notepad': 'notepad',
            'paint': 'mspaint.exe',
            'word': 'start winword',
            'excel': 'start excel',
            'powerpoint': 'start powerpnt',
            'firefox': 'start firefox',
            'opera': 'start opera',
            'vscode': 'code',
            'visual studio': 'start devenv',
            'command prompt': 'cmd',
            'powershell': 'powershell',
            'file explorer': 'explorer',
            'settings': 'start ms-settings:',
            'control panel': 'control',
            'task manager': 'taskmgr',
            'device manager': 'devmgmt.msc',
            'disk management': 'diskmgmt.msc',
            'event viewer': 'eventvwr',
            'services': 'services.msc',
            'registry editor': 'regedit',
            'youtube': 'start https://www.youtube.com',
            'browser': 'start chrome'
        }

    def open_application(self, app_name):
        
        app_name = app_name.lower().strip()

        # Try exact match first
        if app_name in self.application_commands:
            try:
                command = self.application_commands[app_name]
                subprocess.Popen(command, shell=True)
                logger.info(f"Opened application: {app_name} with command: {command}")
                return True, f"Opening {app_name}"
            except Exception as e:
                logger.error(f"Failed to open {app_name}: {e}")
                return False, f"Failed to open {app_name}"

        # Try partial matching
        for key, command in self.application_commands.items():
            if app_name in key or key in app_name:
                try:
                    subprocess.Popen(command, shell=True)
                    logger.info(f"Opened application: {key} with command: {command}")
                    return True, f"Opening {key}"
                except Exception as e:
                    logger.error(f"Failed to open {key}: {e}")
                    continue

        # Try to open directly with shell as fallback
        try:
            subprocess.Popen(app_name, shell=True)
            logger.info(f"Opened application via shell: {app_name}")
            return True, f"Opening {app_name}"
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")

        return False, f"Application '{app_name}' not found or not supported"

    def play_youtube_video(self, query):
       
        if not query or not query.strip():
            return False, "Please specify what you want to play on YouTube"

        try:
            # Clean the query
            query = query.strip()

            # Create YouTube search URL that directly plays the first result
            search_query = query.replace(' ', '+')
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

            # Try to get the first video ID from search (this is a simplified approach)
            # In a real implementation, you might want to use YouTube Data API
            import urllib.request
            import json

            try:
                # Use YouTube search to get video ID
                search_url = f"https://www.youtube.com/results?search_query={search_query}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

                req = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')

                # Extract video ID from the search results page
                import re
                video_id_match = re.search(r'videoId":"([^"]+)"', html)

                if video_id_match:
                    video_id = video_id_match.group(1)
                    # Open the direct video URL
                    direct_url = f"https://www.youtube.com/watch?v={video_id}"
                    webbrowser.open(direct_url)
                    logger.info(f"Playing YouTube video: {query} (ID: {video_id})")
                    return True, f"Playing '{query}' on YouTube"
                else:
                    # Fallback to search results if we can't extract video ID
                    webbrowser.open(youtube_url)
                    logger.info(f"Searching YouTube for: {query}")
                    return True, f"Searching for '{query}' on YouTube"

            except Exception as api_error:
                logger.warning(f"YouTube API search failed: {api_error}")
                # Fallback to direct search
                webbrowser.open(youtube_url)
                logger.info(f"Searching YouTube for: {query}")
                return True, f"Searching for '{query}' on YouTube"

        except Exception as e:
            logger.error(f"Failed to play YouTube video: {e}")
            return False, "Failed to play YouTube video"

    def play_song(self, song_name):
      
        if not song_name or not song_name.strip():
            return False, "Please specify the song name"

        try:
            # Create YouTube music search URL
            search_query = f"{song_name} official audio".replace(' ', '+')
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

            # Open YouTube in default browser
            webbrowser.open(youtube_url)

            logger.info(f"Searching YouTube for song: {song_name}")
            return True, f"Playing '{song_name}' on YouTube"

        except Exception as e:
            logger.error(f"Failed to play song: {e}")
            return False, "Failed to play song on YouTube"

    def open_website(self, website):
        
        if not website or not website.strip():
            return False, "Please specify a website"

        try:
            # Clean the website input
            website = website.strip()

            # Add http:// if not present
            if not website.startswith(('http://', 'https://')):
                # Check if it's a common website
                if '.' in website and not website.startswith('www.'):
                    website = f"https://www.{website}"
                else:
                    website = f"https://{website}"

            webbrowser.open(website)
            logger.info(f"Opened website: {website}")
            return True, f"Opening {website}"

        except Exception as e:
            logger.error(f"Failed to open website: {e}")
            return False, "Failed to open website"

    def search_web(self, query):
        
        if not query or not query.strip():
            return False, "Please specify what to search"

        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            logger.info(f"Searching web for: {query}")
            return True, f"Searching for '{query}'"

        except Exception as e:
            logger.error(f"Failed to search web: {e}")
            return False, "Failed to search web"

    def search_youtube(self, query):
        
        return self.play_youtube_video(query)

    def play_video_on_youtube(self, video_name):
    
        if not video_name or not video_name.strip():
            return False, "Please specify what video you want to play"

        try:
            # Clean the video name
            video_name = video_name.strip()

            # Create YouTube search URL
            search_query = video_name.replace(' ', '+')
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

            # Try to extract video ID and play directly
            import urllib.request

            try:
                search_url = f"https://www.youtube.com/results?search_query={search_query}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

                req = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')

                # Extract video ID from the search results page
                video_id_match = re.search(r'videoId":"([^"]+)"', html)

                if video_id_match:
                    video_id = video_id_match.group(1)
                    # Open the direct video URL
                    direct_url = f"https://www.youtube.com/watch?v={video_id}"
                    webbrowser.open(direct_url)
                    logger.info(f"Playing YouTube video: {video_name} (ID: {video_id})")
                    return True, f"Playing '{video_name}' on YouTube"
                else:
                    # Fallback to search results
                    webbrowser.open(youtube_url)
                    logger.info(f"Searching YouTube for video: {video_name}")
                    return True, f"Searching for '{video_name}' on YouTube"

            except Exception as api_error:
                logger.warning(f"YouTube video search failed: {api_error}")
                # Fallback to direct search
                webbrowser.open(youtube_url)
                logger.info(f"Searching YouTube for video: {video_name}")
                return True, f"Searching for '{video_name}' on YouTube"

        except Exception as e:
            logger.error(f"Failed to play video on YouTube: {e}")
            return False, "Failed to play video on YouTube"

    def is_exit_command(self, command):
       
        if not command:
            return False

        command_lower = command.lower().strip()
        return any(exit_cmd in command_lower for exit_cmd in self.exit_commands)
