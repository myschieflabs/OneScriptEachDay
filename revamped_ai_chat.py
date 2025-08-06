import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import subprocess
import os
import tkinter as tk
import time
import threading
import pyperclip
from rapidfuzz import fuzz

GENAI_API_KEY = "your-api-key-here"
FONT = ("Segoe UI", 12)
MAX_SPEAK_LENGTH = 500
WAKE_PHRASES = [
    "hey luna", "yo luna", "wake up luna", "luna", "luna wake up",
    "are you there luna", "can you hear me luna", "hey assistant", "hello luna"
]
INTERRUPT_PHRASES = ["stop", "cancel", "luna stop", "quiet", "shut up"]
interrupted = False

genai.configure(api_key=GENAI_API_KEY)
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 150,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel("gemini-pro", generation_config=generation_config, safety_settings=safety_settings)

def interrupt_listener():
    global interrupted
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
            spoken = recognizer.recognize_google(audio).lower()
            if any(phrase in spoken for phrase in INTERRUPT_PHRASES):
                interrupted = True
                print("Interrupt detected.")
        except:
            pass

def speak(text):
    global interrupted
    interrupted = False
    tts = gTTS(text=text, lang="en", slow=False, tld="co.uk")
    tts.save("temp.mp3")

    def play_audio():
        try:
            subprocess.run(["mpv", "--quiet", "temp.mp3"])
        except:
            os.startfile("temp.mp3")
        finally:
            time.sleep(1)
            if os.path.exists("temp.mp3"):
                os.remove("temp.mp3")

    audio_thread = threading.Thread(target=play_audio)
    listener_thread = threading.Thread(target=interrupt_listener)
    audio_thread.start()
    listener_thread.start()

    while audio_thread.is_alive():
        if interrupted:
            print("Stopping audio...")
            try:
                subprocess.run(["taskkill", "/f", "/im", "mpv.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            break
        time.sleep(0.1)

def is_wake_word(text):
    return any(fuzz.partial_ratio(text.lower(), phrase) > 80 for phrase in WAKE_PHRASES)

def show(text, title="Luna"):
    root = tk.Tk()
    root.title(title)
    root.geometry("900x700")
    root.configure(bg="black")
    root.bind('<Escape>', lambda e: root.destroy())

    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True)

    box = tk.Text(frame, bg="black", fg="white", font=FONT, wrap="word")
    box.insert(tk.END, text)
    box.configure(state="disabled")
    box.pack(padx=20, pady=20, fill="both", expand=True)

    btn_frame = tk.Frame(root, bg="black")
    btn_frame.pack(fill="x")
    tk.Button(btn_frame, text="Close", command=root.destroy, bg="black", fg="white", font=FONT).pack(side="left", padx=10, pady=10)
    tk.Button(btn_frame, text="Copy", command=lambda: pyperclip.copy(text), bg="black", fg="white", font=FONT).pack(side="left", padx=10)
    
    root.mainloop()

def listen_and_return_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        with sr.Microphone() as source:
            print("Listening for wake phrase...")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("Heard:", text)

            if is_wake_word(text):
                speak("Yes?")
                with sr.Microphone() as cmd_source:
                    recognizer.adjust_for_ambient_noise(cmd_source)
                    command_audio = recognizer.listen(cmd_source)
                try:
                    command = recognizer.recognize_google(command_audio)
                    print("Command:", command)
                    return command
                except:
                    speak("Sorry, I didn't catch that.")
        except:
            pass
        time.sleep(1)

def main():
    while True:
        command = listen_and_return_command()
        if command:
            try:
                response = model.generate_content([command])
                if len(response.text) < MAX_SPEAK_LENGTH:
                    speak(response.text)
                else:
                    speak("That's a long one. Let me show it.")
                    show(response.text)
            except Exception as e:
                print("Luna met with an error:", e)
                show("Sorry, something went wrong.\n\n" + str(e))

if __name__ == "__main__":
    main()
