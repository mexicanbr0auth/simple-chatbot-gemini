from dotenv import load_dotenv
import os
import requests
from gtts import gTTS
import pygame
import tempfile
import threading

load_dotenv()

if os.getenv("API_URL"):
    api_url = os.getenv("API_URL")
else:
    raise ValueError("API_URL Nao Encontrado No .env")
if os.getenv("API_KEY"):
    api_key = os.getenv("API_KEY")
else:
    raise ValueError("API_KEY Nao Encontrado No .env")

pygame.mixer.init()

def falar_gtts(texto):
    def _falar():
        try:
            tts = gTTS(text=texto, lang='pt', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            os.unlink(temp_file)
        except Exception as e:
            print(f"Erro na voz: {e}")

    threading.Thread(target=_falar, daemon=True).start()

def main():
    print("""
          GEMINI CHAT BOT
          /clear
          /exit
          /voice on
          /voice off
          """)
    
    voz_ativa = True
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    while True:
        user_input = input("Chat: ").strip()
        
        if user_input == "/clear":
            os.system("clear")
            continue
        elif user_input == "/exit":
            break
        elif user_input == "/voice on":
            voz_ativa = True
            print("Voz ativada")
            continue
        elif user_input == "/voice off":
            voz_ativa = False
            print("Voz desativada")
            continue

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": user_input
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                url=api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    message = data['candidates'][0]['content']['parts'][0]['text']
                    print(f"Message: {message}")
                    
                    if voz_ativa and message:
                        falar_gtts(message)
                else:
                    print(f"Erro: Resposta inválida da API")
                    print(f"Resposta completa: {data}")
            else:
                print(f"Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    main()
