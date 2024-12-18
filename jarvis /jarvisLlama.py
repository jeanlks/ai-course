import os
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import openai
import pyttsx3
import time
from openai import OpenAI
from playsound import playsound

# Load OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_KEY environment variable is not set")

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech and play it."""
    engine.say(text)
    engine.runAndWait()

def transcribe_speech():
    """Capture audio and transcribe it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your question...")
        audio = recognizer.listen(source, timeout=5)
    try:
        print("Transcribing speech...")
        question = recognizer.recognize_google(audio)
        print(f"You said: {question}")
        return question
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError as e:
        print(f"Speech Recognition error: {e}")
        return None

def get_openai_response(question):
    """Send the transcribed question to OpenAI and get a response."""
    try:
        print("Sending your question to OpenAI...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # You can change to another model like gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            max_tokens=150
        )
        answer = response.choices[0].message.content.strip()
        print(f"OpenAI Response: {answer}")
        return answer
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return "Sorry, I couldn't fetch the answer right now."

def speak_with_openai(text=None, audio_location="response.mp3"):
    if text:
        """Convert text to speech using OpenAI's TTS API and stream to file."""
        client = OpenAI(api_key=os.environ["OPENAI_KEY"])

        # Request TTS audio from OpenAI
        response = client.audio.speech.create(
            model="tts-1",  # You can choose another model like "tts-2" or a specific voice
            voice="alloy",  # Choose the voice you'd like, e.g., "alloy", "newscaster", etc.
            input=text
        )

        # Stream the response audio to a file (e.g., output.mp3)
        response.stream_to_file("response.mp3")

        # Optionally, play the audio using pydub
        playsound('response.mp3')
    else:
        playsound(audio_location)



def main():
    """Main function to handle wake word detection and the Q&A pipeline."""
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        raise ValueError("PICOVOICE_ACCESS_KEY environment variable is not set")

    porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=["jarvis"]  # Change wake word to "jarvis"
    )

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for wake word...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word 'jarvis' detected! Ready for your question.")
                speak_with_openai(audio_location="whatisquestion.mp3")
                time.sleep(0.5)

                # Capture and transcribe the question
                question = transcribe_speech()
                if question:
                    # Get the OpenAI response
                    answer = get_openai_response(question)

                    # Speak the response
                    speak_with_openai(answer)
                else:
                    speak_with_openai("I didn't catch that, please try again.")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        porcupine.delete()
        print("Goodbye!")

if __name__ == "__main__":
    main()

