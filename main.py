
import os
import sys
import random
import argparse
from pydub import AudioSegment

# === CONFIGURACIÓN GENERAL ===
FADE_DURATION_MS = 1000
DURACION_CLIP_MIN_MS = 5000
DURACION_CLIP_MAX_MS = 10000

# === BASE_DIR para .py y .exe ===
if getattr(sys, 'frozen', False):
    # Cuando está empaquetado en .exe, base_dir es la carpeta donde está el ejecutable
    base_dir = os.path.dirname(sys.executable)
else:
    # Cuando se ejecuta como script .py, base_dir es la carpeta del script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Rutas a carpetas efectos e intros (al lado del .exe o script)
carpeta_efectos = os.path.join(base_dir, "efectos")
carpeta_intros = os.path.join(base_dir, "intros")

# === FUNCIONES ===

def obtener_archivos_mp3(carpeta):
    """Devuelve una lista de todos los archivos mp3 en una carpeta (recursivo)."""
    if not os.path.exists(carpeta):
        raise FileNotFoundError(f"No se encontró la carpeta: {carpeta}")
    
    archivos_mp3 = []
    for root, _, files in os.walk(carpeta):
        for f in files:
            if f.lower().endswith(".mp3"):
                archivos_mp3.append(os.path.join(root, f))
    
    return archivos_mp3


def cargar_audio_random_segmento(ruta):
    """Carga un segmento aleatorio del archivo MP3 con fade in/out."""
    audio = AudioSegment.from_mp3(ruta)
    if len(audio) <= DURACION_CLIP_MIN_MS:
        return None
    duracion_segmento = random.randint(DURACION_CLIP_MIN_MS, min(DURACION_CLIP_MAX_MS, len(audio)))
    inicio = random.randint(0, len(audio) - duracion_segmento)
    clip = audio[inicio:inicio + duracion_segmento]
    return clip.fade_in(FADE_DURATION_MS).fade_out(FADE_DURATION_MS)


def cargar_audio_transicion(efectos):
    """Devuelve un efecto de transición aleatorio completo y sin fade."""
    if not efectos:
        return AudioSegment.silent(duration=0)
    
    efecto_path = random.choice(efectos)
    efecto = AudioSegment.from_mp3(efecto_path)
    efecto._path = efecto_path  # Guardamos la ruta para log
    return efecto


def cargar_intro(carpeta_intros):
    """Devuelve un audio de intro aleatorio completo y sin fade."""
    intros = obtener_archivos_mp3(carpeta_intros) if os.path.exists(carpeta_intros) else []
    if not intros:
        return None
    intro_path = random.choice(intros)
    print(f"🎵 Intro seleccionada: {os.path.basename(intro_path)}")
    return AudioSegment.from_mp3(intro_path)


def crear_intromix(carpeta_entrada, carpeta_efectos, carpeta_intros, duracion_total_ms):
    """Genera el intromix con una intro y crossfades entre clips."""
    archivos = obtener_archivos_mp3(carpeta_entrada)
    efectos = obtener_archivos_mp3(carpeta_efectos) if carpeta_efectos and os.path.exists(carpeta_efectos) else []

    if not archivos:
        print("No se encontraron archivos MP3 en la carpeta de entrada.")
        return None

    if carpeta_efectos and not efectos:
        print("⚠️ No se encontraron efectos en la carpeta de efectos.")

    if carpeta_intros and not os.path.exists(carpeta_intros):
        print("⚠️ Carpeta de intros no encontrada.")

    mix_final = AudioSegment.silent(duration=0)
    duracion_actual = 0
    primer_clip = True

    # === Añadir intro al inicio ===
    intro = cargar_intro(carpeta_intros)
    if intro:
        mix_final += intro
        duracion_actual += len(intro)
        print(f"Añadido intro inicial ({len(intro)/1000:.1f}s)")

    while duracion_actual < duracion_total_ms:
        ruta = random.choice(archivos)
        nuevo_clip = cargar_audio_random_segmento(ruta)

        if not nuevo_clip:
            continue

        if primer_clip:
            mix_final = mix_final.append(nuevo_clip, crossfade=0)
            duracion_actual += len(nuevo_clip)
            primer_clip = False
            print(f"Añadido primer clip: {os.path.basename(ruta)} ({len(nuevo_clip)/1000:.1f}s)")
            continue

        efecto = cargar_audio_transicion(efectos)

        mix_final = mix_final.append(nuevo_clip, crossfade=FADE_DURATION_MS)

        if len(efecto) > 0:
            inicio_crossfade = len(mix_final) - len(nuevo_clip)
            mix_final = mix_final.overlay(efecto, position=inicio_crossfade)
            print(f"   ↳ Efecto agregado: {os.path.basename(efecto._path)} ({len(efecto)/1000:.1f}s)")

        duracion_actual += len(nuevo_clip) - FADE_DURATION_MS
        print(f"Añadido clip: {os.path.basename(ruta)} ({len(nuevo_clip)/1000:.1f}s + crossfade)")

    return mix_final


# === ARGUMENTOS DE LÍNEA DE COMANDOS ===

def parse_args():
    parser = argparse.ArgumentParser(description="Crear un intromix de clips MP3 con transiciones.")
    parser.add_argument("-r", "--root", default="carpeta_mp3", help="Carpeta raíz con los MP3. Usa '.' para carpeta actual.")
    parser.add_argument("-d", "--dest", default="intromix.mp3", help="Ruta del archivo MP3 de salida.")
    parser.add_argument("-t", "--time", default="10:00", help="Duración total del mix (min:seg). Ej: 5:30")
    return parser.parse_args()


def convertir_a_milisegundos(tiempo_str):
    """Convierte una cadena 'min:seg' a milisegundos."""
    partes = tiempo_str.strip().split(":")
    if len(partes) == 2:
        minutos, segundos = map(int, partes)
        return (minutos * 60 + segundos) * 1000
    raise ValueError("Formato de tiempo inválido. Usa min:seg, por ejemplo: 5:30")


# === EJECUCIÓN PRINCIPAL ===

if __name__ == "__main__":
    args = parse_args()

    carpeta_mp3 = args.root
    archivo_salida = args.dest
    duracion_total = convertir_a_milisegundos(args.time)

    print(f"Creando intromix desde: {carpeta_mp3}")
    print(f"Guardando en: {archivo_salida}")
    print(f"Duración objetivo: {duracion_total // 1000}s")

    mix = crear_intromix(carpeta_mp3, carpeta_efectos, carpeta_intros, duracion_total)

    if mix:
        mix.export(archivo_salida, format="mp3")
        print(f"\n✅ ¡Intromix exportado como {archivo_salida}!")
