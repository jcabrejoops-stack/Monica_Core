
import keyboard
import pyperclip
import sys

def on_paste():
    try:
        content = pyperclip.paste()
        print(f"PASTE_CONTENT: {content}")
        sys.stdout.flush() # Asegura que la salida se envíe inmediatamente
    except Exception as e:
        print(f"ERROR: {e}")
        sys.stdout.flush()

# Asigna la función de callback a la combinación de teclas Ctrl+V
# 'ctrl+v' es la notación para esta combinación
keyboard.add_hotkey('ctrl+v', on_paste)

print("Listener de Ctrl+V iniciado. Presiona Ctrl+V para pegar.")
sys.stdout.flush()

# Mantiene el script en ejecución
keyboard.wait()
