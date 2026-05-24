
import keyboard
import pyperclip
import sys
import os

def start_clipboard_listener():
    print("Iniciando listener de portapapeles...")
    def on_paste():
        try:
            clipboard_content = pyperclip.paste()
            print(f"Contenido del portapapeles detectado: {clipboard_content}")
            # Aquí podrías enviar 'clipboard_content' al sandbox o a donde sea necesario.
            # Por ahora, solo lo imprimimos para verificación.
        except Exception as e:
            print(f"Error al leer el portapapeles: {e}")

    # Configurar el atajo de teclado para Ctrl+V
    # Usamos un callback que se ejecuta cuando se detecta la combinación
    keyboard.add_hotkey('ctrl+v', on_paste)

    # Mantener el script en ejecución
    print("Listener de portapapeles activo. Presiona Ctrl+V para pegar.")
    keyboard.wait() # Bloquea hasta que se presione una tecla para salir (no aplica aquí si es un listener continuo)

if __name__ == '__main__':
    start_clipboard_listener()
