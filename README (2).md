# Voice Assistant 🎙️🤖

A simple Python-based **Voice Assistant** that can recognize speech, process natural language, and respond with text-to-speech.  

## 📌 Features
- 🎤 **Speech Recognition** (convert voice → text)  
- 🧠 **NLU (Natural Language Understanding)** for processing commands  
- 🔊 **Text-to-Speech** responses  
- ⚡ Lightweight and runs locally  

## 🛠️ Tech Stack
- **Python 3.x**
- `speechrecognition`
- `pyttsx3`
- `pyaudio` (for microphone input)

## 📂 Project Structure
```
voice_assistant/
│── config.py        # Configuration settings
│── recognizer.py    # Speech recognition logic
│── nlu.py           # Natural language understanding
│── tts.py           # Text-to-speech engine
│── requirements.txt # Dependencies
│── README.md        # Project documentation
```

## 🚀 Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/VishnuKumarLH/OIBSIP_Python_Programming_Task1.git
   cd OIBSIP_Python_Programming_Task1
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On Mac/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the assistant:
   ```bash
   python recognizer.py
   ```

## 🎯 Usage
- Speak into your microphone after starting the program.  
- The assistant will **recognize your speech**, **process commands**, and **reply with voice output**.  

## 📸 Example
```
You: "Hello assistant"
Assistant: "Hello! How can I help you today?"
```

## 📜 License
This project is licensed under the MIT License.  
