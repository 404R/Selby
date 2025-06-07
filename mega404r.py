"""Mega404r - Simple Personal Assistant
This simplified version provides a basic chat interface with optional
voice input and text to speech. It uses OpenAI's API if an API key is
provided in the OPENAI_API_KEY environment variable.
"""

import os
import asyncio
import logging

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    VOICE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class VoiceInterface:
    """Handle text to speech and optional speech to text."""
    def __init__(self):
        self.enabled = VOICE_AVAILABLE
        if self.enabled:
            self.tts = pyttsx3.init()
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

    def speak(self, text: str) -> None:
        print(text)
        if self.enabled:
            self.tts.say(text)
            self.tts.runAndWait()

    def listen(self) -> str:
        if not self.enabled:
            return ""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5)
        try:
            return self.recognizer.recognize_google(audio)
        except Exception:
            return ""

async def chat_openai(prompt: str) -> str:
    if not openai or not OPENAI_API_KEY:
        return "OpenAI is not configured."
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

async def main() -> None:
    voice = VoiceInterface()
    voice.speak("Mega404r ready. Say something or type your request.")

    while True:
        text = input("You: ").strip()
        if not text and voice.enabled:
            text = voice.listen()
            if not text:
                continue
            print(f"You (voice): {text}")
        if text.lower() in {"exit", "quit"}:
            voice.speak("Goodbye!")
            break
        reply = await chat_openai(text)
        voice.speak(reply)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
