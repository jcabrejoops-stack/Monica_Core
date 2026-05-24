
import speech_recognition as sr
import sys
import os

def listen_for_keyword(keyword="Mónica"):
    r = sr.Recognizer()
    m = sr.Microphone()
    print(f"Escuchando palabra clave: '{keyword}'...")

    with m as source:
        r.adjust_for_ambient_noise(source) # Ajuste inicial de ruido

    while True:
        try:
            with m as source:
                audio = r.listen(source, phrase_time_limit=5) # Escucha por hasta 5 segundos
            
            print("Procesando audio...")
            # Intenta reconocer el habla usando Google Web Speech API
            decoded_text = r.recognize_google(audio, language='es-ES')
            print(f"Has dicho: {decoded_text}")

            if keyword.lower() in decoded_text.lower():
                print("¡Palabra clave detectada! Activando modo llamada.")
                # Aquí podrías activar la grabación de audio más larga o iniciar la "llamada"
                # Por ahora, solo imprimimos un mensaje.
                # Para una implementación real, necesitarías integrar una lógica de conversación.
                # Por ejemplo, podrías iniciar otra función que escuche continuamente hasta un comando de fin.
                break # Sale del bucle de escucha de palabra clave para pasar a otro modo (simulado aquí)

        except sr.UnknownValueError:
            # El habla no fue entendida
            print("No se pudo entender el audio.")
        except sr.RequestError as e:
            # Error con la API de Google
            print(f"Error en la solicitud al servicio de reconocimiento de voz de Google; {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            # Si hay un error persistente con el micrófono, podríamos necesitar reiniciarlo
            # o informar al usuario.

    print("Modo llamada simulado. Escuchando para la próxima palabra clave.")
    # Si necesitas que siga escuchando después de la "llamada simulada", podrías volver a llamar a listen_for_keyword() o usar un bucle diferente.


if __name__ == '__main__':
    listen_for_keyword()
