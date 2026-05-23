# core/video_ai.py
"""Módulo de generación de videos con IA para Mónica.

Flujo de generación Premium:
1. Calcula escenas y tiempos basados en la duración (5s, 15s, 30s).
2. Usa el LLM (Ollama) para generar un guion de escenas (títulos + descripciones).
3. En Image-to-Video, utiliza la imagen física subida como la primera escena.
4. Genera las imágenes restantes usando Pollinations.ai con sufijos estéticos de estilo.
5. Si es Modo Narrativo, genera la narración de voz usando edge-tts.
6. Aplica efectos cinematográficos Ken Burns (zoom-in, zoom-out, pan-left, pan-right) frame a frame usando PIL.
7. Combina los fotogramas en memoria y añade el audio/música usando moviepy.
"""
import asyncio
import logging
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image

from config import config
from core.media import generate_image, generate_audio, IMAGES_DIR, VIDEO_DIR

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)


def _apply_camera_motion(
    image_path: str,
    num_frames: int,
    width: int,
    height: int,
    motion_type: str
) -> list[np.ndarray]:
    """Lee la imagen con PIL, calcula un recorte progresivo para simular movimiento suave
    y devuelve una lista de frames como matrices de NumPy (uint8 RGB).
    """
    try:
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
    except Exception as e:
        logger.error(f"Error al cargar imagen en motion '{motion_type}': {e}")
        # Fallback a frame plano oscuro para no romper el flujo
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        return [frame] * num_frames

    frames = []
    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0.0

        if motion_type == "zoom_in":
            # Zoom suave desde 1.0x hasta 1.1x
            scale = 1.0 + 0.10 * t
            w_crop = int(width / scale)
            h_crop = int(height / scale)
            x0 = (width - w_crop) // 2
            y0 = (height - h_crop) // 2
            crop_box = (x0, y0, x0 + w_crop, y0 + h_crop)
            frame_img = img.crop(crop_box).resize((width, height), Image.Resampling.LANCZOS)

        elif motion_type == "zoom_out":
            # Zoom suave desde 1.1x hasta 1.0x
            scale = 1.10 - 0.10 * t
            w_crop = int(width / scale)
            h_crop = int(height / scale)
            x0 = (width - w_crop) // 2
            y0 = (height - h_crop) // 2
            crop_box = (x0, y0, x0 + w_crop, y0 + h_crop)
            frame_img = img.crop(crop_box).resize((width, height), Image.Resampling.LANCZOS)

        elif motion_type == "pan_right":
            # Zoom del 1.1x estático y paneo horizontal de izquierda a derecha
            scale = 1.10
            w_crop = int(width / scale)
            h_crop = int(height / scale)
            max_x = width - w_crop
            x0 = int(max_x * t)
            y0 = (height - h_crop) // 2
            crop_box = (x0, y0, x0 + w_crop, y0 + h_crop)
            frame_img = img.crop(crop_box).resize((width, height), Image.Resampling.LANCZOS)

        elif motion_type == "pan_left":
            # Zoom del 1.1x estático y paneo horizontal de derecha a izquierda
            scale = 1.10
            w_crop = int(width / scale)
            h_crop = int(height / scale)
            max_x = width - w_crop
            x0 = int(max_x * (1.0 - t))
            y0 = (height - h_crop) // 2
            crop_box = (x0, y0, x0 + w_crop, y0 + h_crop)
            frame_img = img.crop(crop_box).resize((width, height), Image.Resampling.LANCZOS)

        else:
            # Sin movimiento
            frame_img = img

        frames.append(np.array(frame_img))

    return frames


async def generate_video_from_prompt(
    prompt: str,
    duration: int = 15,
    mode: str = "animation",
    style: str = "photorealistic",
    voice: str = "es-MX-DaliaNeural",
    width: int = 1280,
    height: int = 720,
    image_path: str | None = None,
) -> dict:
    """Genera un video completo a partir de un prompt de texto o imagen guía.

    Parameters
    ----------
    prompt : str
        Descripción del video.
    duration : int
        Duración del video (5, 15 o 30 segundos).
    mode : str
        Modo de generación: 'animation' (sin voz, alta fluidez visual) o 'narrative' (con voz y guion).
    style : str
        Estilo visual: 'photorealistic', '3d-render', 'anime', 'pixel-art'.
    voice : str
        Voz para la narración (solo en modo narrative).
    width, height : int
        Resolución de salida.
    image_path : str | None
        Ruta física de la imagen inicial si es Image-to-Video.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = VIDEO_DIR / f"proyecto_{timestamp}"
    project_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"=== GENERACIÓN DE VIDEO PREMIUM ===")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Duración: {duration}s, Modo: {mode}, Estilo: {style}")
    if image_path:
        logger.info(f"Imagen de inicio (I2V): {image_path}")

    # 1. Mapeo de estilos estéticos
    style_prompts = {
        "photorealistic": "professional 8k photograph, cinematic lighting, photorealistic, highly detailed, raw photo, masterpiece, depth of field, 30 fps",
        "3d-render": "stunning 3d render, octane render, raytraced, detailed 3d art, vibrant colors, masterpiece, Unreal Engine 5 render, highly detailed",
        "anime": "premium anime style, beautiful anime illustration, high quality, vibrant colors, detailed line art, studio ghibli aesthetic, anime scenery",
        "pixel-art": "exquisite 16-bit pixel art style, detailed pixel scene, vibrant colors, nostalgic retro aesthetic, high quality pixel"
    }
    style_suffix = style_prompts.get(style, style_prompts["photorealistic"])

    # 2. Calcular escenas y tiempos basados en la duración
    if duration == 5:
        num_scenes = 2
        duration_per_scene = 2.5
    elif duration == 30:
        num_scenes = 6
        duration_per_scene = 5.0
    else:  # Por defecto 15 segundos
        duration = 15
        num_scenes = 4
        duration_per_scene = 3.75

    # 3. Generar guion de escenas
    scenes = await _generate_script(prompt, num_scenes, style)
    logger.info(f"Guion generado: {len(scenes)} escenas")

    # Guardar guion JSON para referencia
    script_path = project_dir / "guion.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    # 4. Generar o cargar imágenes (en paralelo)
    logger.info("Cargando y generando imágenes de las escenas...")
    image_paths = []
    
    # Si es Image-to-Video, la primera escena es la imagen física
    start_idx = 0
    if image_path and Path(image_path).exists():
        first_scene_path = project_dir / "escena_01.png"
        try:
            import shutil
            shutil.copy2(image_path, str(first_scene_path))
            image_paths.append(first_scene_path)
            logger.info("Imagen física cargada correctamente como primera escena.")
            start_idx = 1
        except Exception as e:
            logger.error(f"Error al copiar la imagen física de inicio: {e}")

    image_tasks = []
    for i in range(start_idx, num_scenes):
        scene = scenes[i]
        image_prompt = scene.get("image_prompt", scene.get("description", prompt))
        image_tasks.append(_generate_scene_image(image_prompt, project_dir, i, width, height, style_suffix))

    generated_paths = await asyncio.gather(*image_tasks)
    image_paths.extend(generated_paths)
    logger.info(f"Fotogramas base listos: {len(image_paths)}")

    # 5. Generar narración de audio (solo en Modo Narrativo)
    narration_path = None
    if mode == "narrative":
        narration_text = " ... ".join(scene.get("narration", scene.get("description", "")) for scene in scenes)
        logger.info("Generando narración de audio con edge-tts...")
        narration_path = project_dir / "narracion.mp3"
        try:
            import edge_tts
            communicate = edge_tts.Communicate(narration_text, voice)
            await communicate.save(str(narration_path))
            logger.info(f"Narración guardada en: {narration_path}")
        except Exception as exc:
            logger.warning(f"No se pudo generar narración: {exc}. Continuando sin audio.")
            narration_path = None

    # 6. Combinar fotogramas con efectos Ken Burns en video MP4
    logger.info("Aplicando efectos de cámara y compilando video final...")
    output_video_path = project_dir / f"video_{timestamp}.mp4"
    
    video_path = await _compose_video(
        image_paths=[str(p) for p in image_paths],
        audio_path=str(narration_path) if narration_path else None,
        output_path=str(output_video_path),
        duration_per_image=duration_per_scene,
        width=width,
        height=height,
        fps=24
    )

    logger.info(f"=== VIDEO PREMIUM COMPLETADO: {video_path} ===")

    return {
        "video_path": video_path,
        "video_filename": Path(video_path).name,
        "scenes": scenes,
        "narration_path": str(narration_path) if narration_path else None,
        "project_dir": str(project_dir),
    }


async def _generate_script(prompt: str, num_scenes: int, style: str) -> list[dict]:
    """Genera un guion de escenas en base al estilo solicitado usando el LLM."""
    try:
        from core.llm import call_llm

        llm_prompt = (
            f"Genera un guion de video altamente descriptivo, coherente y artístico con exactamente {num_scenes} escenas para el siguiente tema: '{prompt}'.\n"
            f"El estilo visual deseado del video es: '{style}'.\n"
            f"Responde ÚNICAMENTE con un JSON array de objetos. Cada objeto debe tener exactamente las siguientes claves:\n"
            f"- 'scene_number': número de escena (entero)\n"
            f"- 'description': descripción breve en español del contenido de la escena\n"
            f"- 'image_prompt': prompt hiperdetallado en INGLÉS especializado en el estilo '{style}' (describe luces, planos de cámara, texturas) que represente esta escena en una imagen\n"
            f"- 'narration': texto de narración en español corto y fluido para esta escena (1 o 2 oraciones)\n"
            f"Ejemplo: [{{'scene_number': 1, 'description': '...', 'image_prompt': '...', 'narration': '...'}}]\n"
            f"Responde ÚNICAMENTE el JSON, sin bloques de código, y sin texto explicativo."
        )
        response = await call_llm(llm_prompt)

        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            scenes = json.loads(json_match.group())
            if isinstance(scenes, list) and len(scenes) > 0:
                return scenes[:num_scenes]
    except Exception as exc:
        logger.warning(f"LLM no disponible para guion de video, usando generación automática: {exc}")

    # Fallback automático
    return [
        {
            "scene_number": i + 1,
            "description": f"Escena {i + 1} de: {prompt}",
            "image_prompt": f"{prompt}, scene {i + 1}, cinematic lighting, highly detailed, masterwork",
            "narration": f"Presentando la escena {i + 1} sobre {prompt}.",
        }
        for i in range(num_scenes)
    ]


async def _generate_scene_image(
    image_prompt: str,
    project_dir: Path,
    index: int,
    width: int,
    height: int,
    style_suffix: str = ""
) -> Path:
    """Genera una imagen para una escena agregándole el sufijo de estilo correspondiente."""
    import httpx
    import urllib.parse
    import re

    filename = project_dir / f"escena_{index + 1:02d}.png"
    
    # Adjuntar sufijo de estilo
    full_prompt = f"{image_prompt}, {style_suffix}" if style_suffix else image_prompt

    # Varios intentos de robustez
    attempts = [
        full_prompt,
        image_prompt, # fallback 1: prompt sin sufijo de estilo por si es muy largo
        re.sub(r'[^a-zA-Z0-9\s]', '', image_prompt.split(",")[0])[:60].strip() # fallback 2: solo palabras clave básicas
    ]
    attempts = [a for a in attempts if a.strip()]
    if not attempts:
        attempts = ["visual scenery, high resolution"]

    for attempt_idx, prompt_to_try in enumerate(attempts):
        encoded = urllib.parse.quote(prompt_to_try)
        model_param = "&model=turbo" if attempt_idx > 0 else ""
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true{model_param}"
        
        logger.info(f"Intento {attempt_idx + 1} para fotograma {index + 1}: '{prompt_to_try[:50]}...'")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(url, follow_redirects=True)
                resp.raise_for_status()
                if "image" not in resp.headers.get("content-type", "") and len(resp.content) < 1000:
                    raise ValueError("Respuesta no es una imagen válida")
                with open(filename, "wb") as f:
                    f.write(resp.content)
            logger.info(f"Fotograma {index + 1} guardado correctamente en el intento {attempt_idx + 1}")
            return filename
        except Exception as exc:
            logger.warning(f"Intento {attempt_idx + 1} falló para fotograma {index + 1}: {exc}")

    # Fallback: Generar una imagen Pillow premium elegante
    try:
        from PIL import ImageDraw
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, width - 20, height - 20], outline=(6, 182, 212), width=2)
        draw.text((width // 2 - 120, height // 2 - 10), f"Escena {index + 1} - Mónica Studio", fill=(243, 244, 246))
        img.save(str(filename))
        logger.info(f"Creado fotograma de respaldo premium para escena {index + 1}")
    except Exception as placeholder_exc:
        logger.error(f"Error generando fotograma de respaldo: {placeholder_exc}")
        img = Image.new("RGB", (width, height), color=(10, 10, 20))
        img.save(str(filename))

    return filename


async def _compose_video(
    image_paths: list[str],
    audio_path: str | None,
    output_path: str,
    duration_per_image: float,
    width: int = 1280,
    height: int = 720,
    fps: int = 24,
) -> str:
    """Aplica animación de cámara Ken Burns frame a frame y compila el video final con audio."""
    from moviepy import ImageSequenceClip, AudioFileClip
    
    logger.info(f"Compilando video animado: {len(image_paths)} escenas, {duration_per_image}s cada una a {fps} FPS")

    all_frames = []
    motions = ["zoom_in", "pan_right", "zoom_out", "pan_left"]

    # Generar secuencia de fotogramas suavizados
    for idx, img_path in enumerate(image_paths):
        motion = motions[idx % len(motions)]
        num_frames = int(duration_per_image * fps)
        if num_frames < 1:
            num_frames = 1
            
        logger.info(f"Procesando animación '{motion}' para escena {idx + 1} ({num_frames} frames)")
        frames = _apply_camera_motion(
            image_path=img_path,
            num_frames=num_frames,
            width=width,
            height=height,
            motion_type=motion
        )
        all_frames.extend(frames)

    # Crear el clip a partir de los arrays de fotogramas en memoria
    clip = ImageSequenceClip(all_frames, fps=fps)

    # Incorporar narración o banda sonora si existe
    if audio_path and Path(audio_path).exists():
        try:
            audio = AudioFileClip(audio_path)
            # Rellenar video repitiendo el último cuadro si el audio es más largo
            if audio.duration > clip.duration:
                last_frame = all_frames[-1]
                extra_frames = int((audio.duration - clip.duration) * fps)
                if extra_frames > 0:
                    logger.info(f"Alineando video con audio: agregando {extra_frames} frames al final")
                    extended_frames = all_frames + [last_frame] * extra_frames
                    clip = ImageSequenceClip(extended_frames, fps=fps)
            clip = clip.with_audio(audio)
        except Exception as exc:
            logger.warning(f"Error al integrar pista de audio al video: {exc}")

    # Guardar video final de forma asíncrona
    await asyncio.to_thread(
        clip.write_videofile,
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )

    return output_path
