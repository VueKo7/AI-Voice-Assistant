import io
import json

file = io.open("settings.json", "r")
file = file.read()
fjson = json.loads(file)

API_KEY = fjson["API_KEY"]
PROJECT_ID = fjson["PROJECT_ID"]
ASSISTANT_ID = fjson["ASSISTANT_ID"]
THREAD_ID = fjson["THREAD_ID"]
KEY_TO_HOLD = fjson["KEY_TO_HOLD"]
MODEL = fjson["MODEL"]


from openai import OpenAI
client = OpenAI(
    api_key=API_KEY,
    project=PROJECT_ID
)



def callAssistant(transcription):
    
    client.beta.threads.messages.create(
        thread_id=THREAD_ID,
        role="user",
        content=transcription
    )
    
    run = client.beta.threads.runs.create_and_poll(
        thread_id=THREAD_ID,
        assistant_id=ASSISTANT_ID,
        model="gpt-3.5-turbo"
    )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=THREAD_ID,
        )
        msg = messages.to_dict()
        return msg.get('data')[0].get('content')[0].get('text').get('value')
    else:
        return run.status





import pyaudio
import wave
import keyboard
import requests
import time

# Configurazione dei parametri di registrazione
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "recording.wav"

# Funzione per registrare audio
def record_audio():
    audio = pyaudio.PyAudio()

    # Configurazione dello stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []

    while keyboard.is_pressed(KEY_TO_HOLD):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Terminazione dello stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Salvataggio del file audio
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Funzione per inviare audio all'API di OpenAI Whisper
def transcribe_audio(file_path):
    api_key = API_KEY
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    files = {
        'file': open(file_path, 'rb'),
        'model': (None, MODEL),
        'language': (None, 'en')  # Impostazione della lingua su inglese
    }
    response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files)

    if response.status_code == 200:
        text = response.json().get('text', '').strip()
        if text:
            return text
        else:
            return ""
    else:
        return ""
    
import requests
import pygame
import time

file_path = "output.mp3"

def text_to_speech(text):
    # Codice per ottenere il file audio dal client e salvarlo
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=text,
        response_format="mp3"
    )

    # Salvataggio del file audio
    with open(file_path, "wb") as file:
        file.write(response.content)  # Usare .content se response è un oggetto della libreria requests
    
    # Aggiungi un piccolo ritardo per garantire che il file sia completamente salvato e chiuso
    time.sleep(1)



def play_audio():
    # Inizializzazione di pygame mixer
    pygame.mixer.init()

    # Caricamento del file audio
    pygame.mixer.music.load(file_path)

    # Riproduzione del file audio
    pygame.mixer.music.play()

    # Aspetta fino alla fine della riproduzione dell'audio
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    # Scarica il mixer per rilasciare il file
    pygame.mixer.music.unload()
    pygame.mixer.quit()


    

# Programma principale
print("Press and hold " + KEY_TO_HOLD + " to start recording...")

while True:
    if keyboard.is_pressed(KEY_TO_HOLD):
        record_audio()
        
        # get the speech to text
        transcription = transcribe_audio(WAVE_OUTPUT_FILENAME)
        if len(transcription) > 0:
            print("User: " + transcription)
        
            # send the text to the assistant and get the response
            response = callAssistant(transcription)
            print("Assistant: " + response)
            
            text_to_speech(response)
            play_audio()
            
                
        print("Press and hold " + KEY_TO_HOLD + " to start recording again...")
    
    time.sleep(0.1)  # Piccola pausa per evitare un utilizzo eccessivo della CPU


