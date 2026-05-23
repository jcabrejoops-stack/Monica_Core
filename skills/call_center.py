# skills/call_center.py
import os
import uvicorn
from fastapi import FastAPI, Request, Response
try:
    from twilio.twiml.voice_response import VoiceResponse
except ImportError:
    pass

app = FastAPI(title="Monica AI Call Center")

@app.post("/twiml")
async def handle_call(request: Request):
    """
    Webhook de Twilio. Se ejecuta cuando un humano llama al número de teléfono.
    """
    try:
        from twilio.twiml.voice_response import VoiceResponse
    except ImportError:
        return {"error": "Falta instalar twilio (pip install twilio)"}
        
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult")
    
    response = VoiceResponse()
    
    if not speech_result:
        # Primera vez que llaman: Mónica se presenta y empieza a escuchar
        response.say("Hola, te comunicaste con la central telefónica de Inteligencia Artificial Mónica. ¿En qué puedo ayudarte hoy?", voice="Polly.Lucia-Neural", language="es-MX")
        response.gather(input="speech", action="/twiml", timeout=5, language="es-MX")
    else:
        # El humano dijo algo, el STT de Twilio lo transcribió
        print(f"[Call Center] Humano dice: {speech_result}")
        
        # Aquí Mónica usa su RAG / cerebro para responder.
        # Por simplicidad de la plantilla, devolvemos una respuesta genérica.
        # En producción, importaríamos `call_llm` de `core.llm`.
        respuesta_monica = f"Entiendo. Has dicho: {speech_result}. Déjame procesar esa información en mi base de datos."
        
        response.say(respuesta_monica, voice="Polly.Lucia-Neural", language="es-MX")
        # Volver a escuchar para continuar la conversación
        response.gather(input="speech", action="/twiml", timeout=5, language="es-MX")

    return Response(content=str(response), media_type="application/xml")

def iniciar_call_center(puerto: int = 5050):
    """
    Levanta el servidor local del Call Center.
    Nota: Para conectarlo con Twilio, debes exponer este puerto a internet usando ngrok:
    'ngrok http 5050' y poner la URL HTTPS resultante en el webhook de tu número de Twilio.
    """
    import threading
    def correr():
        uvicorn.run(app, host="0.0.0.0", port=puerto)
        
    hilo = threading.Thread(target=correr, daemon=True)
    hilo.start()
    return f"Servidor de Call Center IA iniciado en el puerto {puerto}. Usa Ngrok para exponerlo a Twilio."

# Puedes probarlo en Sandbox ejecutando:
# import sys; sys.path.append('skills'); from call_center import iniciar_call_center; iniciar_call_center()
