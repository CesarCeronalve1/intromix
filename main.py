import eyed3
import os
import sys
import random
import argparse
import datetime
import configparser
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from dotenv import load_dotenv

# === CONFIGURACIÓN GENERAL ===
FADE_DURATION_MS = 1000
DURACION_CLIP_MIN_MS = 5000
DURACION_CLIP_MAX_MS = 10000

# === Cargar variables de entorno ===
load_dotenv()

# === BASE_DIR para .py y .exe ===
if getattr(sys, 'frozen', False):
    # Cuando está empaquetado en .exe, base_dir es la carpeta donde está el ejecutable
    base_dir = os.path.dirname(sys.executable)
else:
    # Cuando se ejecuta como script .py, base_dir es la carpeta del script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Rutas a carpetas efectos, intros y portadas (al lado del .exe o script)
carpeta_efectos = os.path.join(base_dir, "efectos")
carpeta_intros = os.path.join(base_dir, "intros")
carpeta_portadas = os.path.join(base_dir, "portada")
archivo_metadata = os.path.join(base_dir, "metadata.txt")

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


def seleccionar_portada(carpeta_portadas):
    """Muestra lista de imágenes en la carpeta portada y permite seleccionar una."""
    if not os.path.exists(carpeta_portadas):
        print("⚠️ Carpeta de portadas no encontrada.")
        return None
    
    # Buscar imágenes válidas
    imagenes_validas = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        imagenes_validas.extend(list(Path(carpeta_portadas).glob(f"*{ext}")))
        imagenes_validas.extend(list(Path(carpeta_portadas).glob(f"*{ext.upper()}")))
    
    if not imagenes_validas:
        print("⚠️ No se encontraron imágenes en la carpeta de portadas.")
        return None
    
    # Mostrar lista numerada
    print("\n📁 Imágenes disponibles para portada:")
    for i, img in enumerate(imagenes_validas, 1):
        print(f"  [{i}] {img.name}")
    print(f"  [0] No usar portada")
    
    # Permitir al usuario seleccionar
    while True:
        try:
            seleccion = input("\n🔢 Selecciona el número de la imagen (o 0 para omitir): ").strip()
            if seleccion == '':
                print("❌ Por favor ingresa un número.")
                continue
                
            seleccion_int = int(seleccion)
            if seleccion_int == 0:
                return None
            elif 1 <= seleccion_int <= len(imagenes_validas):
                portada_seleccionada = imagenes_validas[seleccion_int - 1]
                print(f"✅ Portada seleccionada: {portada_seleccionada.name}")
                return str(portada_seleccionada)
            else:
                print(f"❌ Por favor selecciona un número entre 0 y {len(imagenes_validas)}")
        except ValueError:
            print("❌ Entrada no válida. Por favor ingresa un número.")


def cargar_metadata_desde_archivo():
    """Carga metadatos desde el archivo metadata.txt si existe."""
    metadatos = {}
    
    if not os.path.exists(archivo_metadata):
        print(f"ℹ️ Archivo metadata.txt no encontrado en {archivo_metadata}")
        return metadatos
    
    try:
        # Leer el archivo como texto y procesar líneas tipo "clave=valor"
        with open(archivo_metadata, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Buscar el primer signo igual
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip().strip('"\'')
                    
                    # Mapear nombres de campos a los usados por eyed3
                    if key == 'artista':
                        metadatos['artist'] = value
                    elif key == 'titulo':
                        metadatos['title'] = value
                    elif key == 'album':
                        metadatos['album'] = value
                    elif key == 'año':
                        metadatos['year'] = value
                    elif key == 'genero':
                        metadatos['genre'] = value
                    elif key == 'comentario':
                        metadatos['comment'] = value
                    elif key == 'subtitulo':
                        metadatos['subtitle'] = value
                    elif key == 'tracknumero':
                        metadatos['track_num'] = value
                    elif key == 'editor':
                        metadatos['publisher'] = value  # editor se mapea a publisher
                    elif key == 'codificado por':
                        metadatos['encoded_by'] = value
                    else:
                        # Si no es un campo mapeado, guardarlo como está
                        metadatos[key] = value
                
        print(f"✅ Metadatos cargados desde {archivo_metadata}")
        
    except Exception as e:
        print(f"⚠️ Error al leer metadata.txt: {e}")
    
    return metadatos


def obtener_metadatos(args):
    """Obtiene los metadatos para el archivo final, combinando archivo y argumentos."""
    # Cargar metadatos desde archivo
    metadatos = cargar_metadata_desde_archivo()
    
    # Sobrescribir con argumentos de línea de comandos si se proporcionan
    if hasattr(args, 'title') and args.title:
        metadatos['title'] = args.title
    
    if hasattr(args, 'artist') and args.artist:
        metadatos['artist'] = args.artist
    
    if hasattr(args, 'album') and args.album:
        metadatos['album'] = args.album
    
    if hasattr(args, 'year') and args.year:
        metadatos['year'] = args.year
    
    if hasattr(args, 'genre') and args.genre:
        metadatos['genre'] = args.genre
    
    if hasattr(args, 'comment') and args.comment:
        metadatos['comment'] = args.comment
    
    if hasattr(args, 'subtitle') and args.subtitle:
        metadatos['subtitle'] = args.subtitle
    
    if hasattr(args, 'track') and args.track:
        metadatos['track_num'] = args.track
    
    # Los siguientes campos solo se pueden establecer desde metadata.txt
    # ya que no hay argumentos de línea de comandos para ellos
    # pero se mantienen si están en el archivo metadata.txt
    
    # Asegurar campos mínimos con valores por defecto
    if 'title' not in metadatos:
        metadatos['title'] = 'intromix'
    
    if 'artist' not in metadatos:
        metadatos['artist'] = 'Non'
    
    # Añadir fecha de creación al comentario si no hay comentario específico
    if 'comment' not in metadatos:
        metadatos['comment'] = f'Creado el {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    else:
        # Agregar fecha al comentario existente
        metadatos['comment'] += f' | Creado el {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    # Asegurar año si no está definido
    if 'year' not in metadatos:
        metadatos['year'] = str(datetime.datetime.now().year)
    
    return metadatos


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


def exportar_con_metadatos(audio, archivo_salida, metadatos, portada_path=None):
    """Exporta el audio con metadatos y portada usando el método correcto."""
    # Primero exportamos el audio sin metadatos
    temp_file = archivo_salida.replace('.mp3', '_temp.mp3')
    audio.export(temp_file, format="mp3")
    
    try:
        # Cargar el archivo MP3
        audiofile = eyed3.load(temp_file)
        if audiofile is None:
            audiofile = eyed3.load(temp_file)
        
        if audiofile.tag is None:
            audiofile.initTag()
        
        # Establecer metadatos básicos
        if 'title' in metadatos:
            audiofile.tag.title = metadatos['title']
        
        if 'artist' in metadatos:
            audiofile.tag.artist = metadatos['artist']
        
        if 'album' in metadatos:
            audiofile.tag.album = metadatos['album']
        
        if 'year' in metadatos:
            audiofile.tag.recording_date = metadatos['year']
        
        if 'genre' in metadatos:
            audiofile.tag.genre = metadatos['genre']
        
        if 'comment' in metadatos:
            audiofile.tag.comments.set(metadatos['comment'])
        
        if 'subtitle' in metadatos:
            audiofile.tag.subtitle = metadatos['subtitle']
        
        if 'track_num' in metadatos:
            try:
                track_num = int(metadatos['track_num'])
                audiofile.tag.track_num = track_num
            except ValueError:
                print(f"⚠️ Número de pista inválido: {metadatos['track_num']}")
        
        # Nuevos campos: editor y codificado por
        if 'publisher' in metadatos:  # editor se mapeó a publisher
            audiofile.tag.publisher = metadatos['publisher']
            print(f"✅ Editor establecido: {metadatos['publisher']}")
        
        if 'encoded_by' in metadatos:
            audiofile.tag.encoded_by = metadatos['encoded_by']
            print(f"✅ Codificado por establecido: {metadatos['encoded_by']}")
        
        # Añadir portada si existe
        if portada_path and os.path.exists(portada_path):
            try:
                with open(portada_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                # Determinar tipo MIME
                if portada_path.lower().endswith('.jpg') or portada_path.lower().endswith('.jpeg'):
                    mime_type = 'image/jpeg'
                elif portada_path.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif portada_path.lower().endswith('.gif'):
                    mime_type = 'image/gif'
                elif portada_path.lower().endswith('.bmp'):
                    mime_type = 'image/bmp'
                else:
                    mime_type = 'image/jpeg'  # Por defecto
                
                audiofile.tag.images.set(3, img_data, mime_type, u"Cover")
                print(f"✅ Portada añadida: {os.path.basename(portada_path)}")
                
            except Exception as e:
                print(f"⚠️ Error al añadir portada: {e}")
        
        # Guardar cambios
        audiofile.tag.save()
        
        # Renombrar el archivo temporal al final
        os.replace(temp_file, archivo_salida)
        print(f"✅ Metadatos aplicados correctamente")
        
    except ImportError:
        print("⚠️ eyed3 no está instalado. Exportando sin metadatos avanzados...")
        print("   Instala con: pip install eyed3")
        # Exportar solo con metadatos básicos
        audio.export(archivo_salida, format="mp3", tags=metadatos)
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        print(f"⚠️ Error al añadir metadatos: {e}")
        print("   Exportando sin metadatos...")
        audio.export(archivo_salida, format="mp3")
        if os.path.exists(temp_file):
            os.remove(temp_file)


# === ARGUMENTOS DE LÍNEA DE COMANDOS ===

def parse_args():
    parser = argparse.ArgumentParser(
        description="Crear un intromix de clips MP3 con transiciones.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -r carpeta_musica -d mix_final.mp3 -t 5:30 -a "Mezcla Especial" --artist "DJ Mix"
  %(prog)s -r . -d resultado.mp3 -t 10:00 --title "Mix Personal" --year "2024"
  %(prog)s -r canciones -d final.mp3 -t 15:00 --genre "Electrónica" --track "1"
        """
    )
    parser.add_argument("-r", "--root", default="carpeta_mp3", 
                       help="Carpeta raíz con los MP3. Usa '.' para carpeta actual.")
    parser.add_argument("-d", "--dest", default="intromix.mp3", 
                       help="Ruta del archivo MP3 de salida.")
    parser.add_argument("-t", "--time", default="10:00", 
                       help="Duración total del mix (min:seg). Ej: 5:30")
    parser.add_argument("-album", "--album", default="", 
                       help="Nombre del álbum para los metadatos.")
    parser.add_argument("-title", default="", 
                       help="Título del mix (sobrescribe metadata.txt).")
    parser.add_argument("-artist", default="", 
                       help="Artista del mix (sobrescribe metadata.txt).")
    parser.add_argument("-year", default="", 
                       help="Año del mix (sobrescribe metadata.txt).")
    parser.add_argument("-genre", default="", 
                       help="Género musical (sobrescribe metadata.txt).")
    parser.add_argument("-comment", default="", 
                       help="Comentario (sobrescribe metadata.txt).")
    parser.add_argument("-subtitle", default="", 
                       help="Subtítulo (sobrescribe metadata.txt).")
    parser.add_argument("-track", default="", 
                       help="Número de pista (sobrescribe metadata.txt).")
    parser.add_argument("-no-portada", action="store_true", 
                       help="Omitir la selección de portada.")
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

    print("=" * 50)
    print(f"🎧 CREADOR DE INTROMIX")
    print("=" * 50)
    print(f"📂 Carpeta origen: {carpeta_mp3}")
    print(f"💾 Archivo salida: {archivo_salida}")
    print(f"⏱️  Duración objetivo: {duracion_total // 1000}s")
    print(f"📄 Archivo metadata: {archivo_metadata if os.path.exists(archivo_metadata) else 'No encontrado'}")
    print("=" * 50)

    # Crear el mix
    mix = crear_intromix(carpeta_mp3, carpeta_efectos, carpeta_intros, duracion_total)

    if mix:
        # Seleccionar portada
        portada_path = None
        if not args.no_portada:
            portada_path = seleccionar_portada(carpeta_portadas)
        
        # Obtener metadatos
        metadatos = obtener_metadatos(args)
        
        print("\n📝 Metadatos que se aplicarán:")
        for key, value in metadatos.items():
            if key in ['title', 'artist', 'album', 'year', 'genre', 'comment', 'subtitle', 'track_num', 'publisher', 'encoded_by']:
                print(f"   {key}: {value}")
        
        # Exportar con metadatos y portada
        exportar_con_metadatos(mix, archivo_salida, metadatos, portada_path)
        
        print(f"\n{'='*50}")
        print(f"✅ ¡Intromix exportado como {archivo_salida}!")
        print(f"{'='*50}")