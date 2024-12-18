
import pyttsx3

engine = pyttsx3.init()

# List available voices
voices = engine.getProperty('voices')

# Display available voices and choose one
for voice in voices:
    print(f"ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")

# Set the voice to a more natural-sounding one (you can adjust this)
engine.setProperty('voice', voices[23].id)  # Adjust index based on your preference
engine.setProperty('rate', 150)  # Adjust speaking rate (normal is 200)
engine.setProperty('volume', 1)  # Volume range from 0.0 to 1.0

# Test the new voice
engine.say("Hello, I hope this voice sounds better.")
engine.runAndWait()