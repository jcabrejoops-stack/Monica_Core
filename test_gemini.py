import asyncio
from core.agent import run_vibe_agent

async def main():
    print("Iniciando prueba con Gemini (Chiste)...")
    respuesta = await run_vibe_agent("cuéntame un chiste por favor, algo corto.")
    print("Respuesta de Mónica:")
    print(respuesta)

if __name__ == "__main__":
    asyncio.run(main())
