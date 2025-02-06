# Please install OpenAI SDK first: `pip3 install openai`
import json
import time
import wave
import logging
import requests
import pyaudio
import keyboard
from openai import OpenAI  # Importa l'SDK OpenAI

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_settings(settings_file="settings.json"):
    """
    Carica la configurazione dal file JSON.
    Il file deve contenere le chiavi:
      - OPEN_KEY: per il servizio di trascrizione OpenAI Whisper
      - DEEP_KEY: per l'accesso all'API DeepSeek tramite OpenAI SDK
      - eventuali altre impostazioni
    """
    try:
        with open(settings_file, "r") as f:
            config = json.load(f)
        return config
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Errore nel caricamento del file di configurazione: {e}")
        raise

def transcribe_audio(file_path, open_key):
    """
    Invia il file audio all'API di OpenAI Whisper per ottenere la trascrizione.
    
    :param file_path: Percorso del file audio
    :param open_key: Chiave API per OpenAI Whisper (OPEN_KEY)
    :return: Testo trascritto oppure un messaggio d'errore
    """
    headers = {
        'Authorization': f'Bearer {open_key}',
    }
    try:
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': audio_file,
                'model': (None, 'whisper-1'),
                'language': (None, 'it')  # Impostazione della lingua su italiano
            }
            response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files)
        response.raise_for_status()
        text = response.json().get('text', '').strip()
        return text if text else "Non sono riuscito a capire"
    except (requests.RequestException, IOError) as e:
        logging.error(f"Errore nella trascrizione audio: {e}")
        return "Non sono riuscito a capire"

def call_assistant(transcription, deep_key):
    """
    Invia il testo trascritto al modello DeepSeek tramite OpenAI SDK e restituisce la risposta.
    
    Utilizza il seguente formato per la comunicazione:
    
        from openai import OpenAI
    
        client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
    
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False
        )
    
        print(response.choices[0].message.content)
    
    :param transcription: Testo da inviare al modello
    :param deep_key: Chiave API per DeepSeek (DEEP_KEY)
    :return: Risposta del modello oppure un messaggio d'errore
    """
    try:
        client = OpenAI(api_key=deep_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": transcription},
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Errore nella richiesta a DeepSeek: {e}")
        return "Non sono riuscito a ottenere una risposta"

def record_audio(filename="recording.wav", format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
    """
    Registra audio finché il tasto 'T' è premuto e salva il risultato in un file WAV.
    
    :param filename: Nome del file audio
    :param format: Formato audio
    :param channels: Numero di canali
    :param rate: Frequenza di campionamento
    :param chunk: Dimensione del buffer
    :return: Nome del file audio registrato
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    logging.info("Inizio registrazione...")
    frames = []

    while keyboard.is_pressed('t'):
        data = stream.read(CHUNK)
        frames.append(data)

    logging.info("Registrazione terminata.")
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
        'model': (None, 'whisper-1'),
        'language': (None, 'it')  # Impostazione della lingua su italiano
    }
    response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files)

    if response.status_code == 200:
        text = response.json().get('text', '').strip()
        if text:
            return text
        else:
            return "Non sono riuscito a capire"
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return "Non sono riuscito a capire"

# Programma principale
print("Press and hold 'T' to start recording...")

while True:
    if keyboard.is_pressed('t'):
        record_audio()
        
        # get the speech to text
        transcription = transcribe_audio(WAVE_OUTPUT_FILENAME)
        print("User: " + transcription)
        
        

        # send the text to the assistant and get the response
        response = callAssistant(transcription)
        print("Assistant: " + response)
                
        print("Press and hold 'T' to start recording again...")
    
    time.sleep(0.1)  # Piccola pausa per evitare un utilizzo eccessivo della CPU