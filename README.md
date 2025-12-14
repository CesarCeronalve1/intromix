# Manual de Usuario: Intromix Creator

## Descripción

**Intromix Creator** es una herramienta para crear un *mix* de música a partir de archivos MP3. El programa permite combinar clips aleatorios de una carpeta de música, añadir efectos de transición y una intro personalizada, y exportar el resultado en formato MP3 con metadatos como título, artista, género, año y portada (opcional).

## Requisitos

Para usar el programa, necesitarás tener Python instalado, junto con algunas librerías adicionales. Además, es necesario tener **FFmpeg** instalado en tu sistema para manipular los archivos de audio.

### Instalación de Dependencias

1. **Instala las librerías necesarias**:
    Abre una terminal y ejecuta el siguiente comando para instalar las dependencias requeridas:
    
    ```
    pip install eyed3 pydub python-dotenv
    ```

2. **Instala FFmpeg**:
    FFmpeg es necesario para que `pydub` funcione correctamente. Descárgalo e instálalo desde [FFmpeg](https://ffmpeg.org/download.html).

## Uso

### Estructura de Carpetas

Para usar el programa correctamente, organiza tus archivos en las siguientes carpetas:

- **`musica/`**: Carpeta que contiene los archivos MP3 que deseas mezclar.
- **`efectos/`**: Carpeta con efectos de transición en formato MP3.
- **`intros/`**: Carpeta con intros en formato MP3 (opcional).
- **`portada/`**: Carpeta con imágenes en formato JPG, PNG, GIF o BMP para la portada (opcional).

### Ejecución del Programa

Abre una terminal y navega al directorio donde tienes el archivo `intromix_creator.py`. Luego, usa el siguiente comando para generar un *mix*:

```
python intromix_creator.py -r <ruta_carpeta_musica> -d <ruta_destino_mix> -t <duracion_mix> [opciones adicionales]
Argumentos
-r, --root (Requerido): Carpeta donde están tus archivos MP3.

Ejemplo: -r ./musica

-d, --dest (Requerido): Ruta y nombre del archivo MP3 de salida.

Ejemplo: -d mix_final.mp3

-t, --time (Requerido): Duración total del mix en formato min:seg.

Ejemplo: -t 5:30 para 5 minutos y 30 segundos.

Opciones Adicionales
-album, --album: Nombre del álbum para los metadatos.

-title: Título del mix (sobrescribe metadata.txt si existe).

-artist: Artista del mix (sobrescribe metadata.txt).

-year: Año del mix (sobrescribe metadata.txt).

-genre: Género musical para el mix (sobrescribe metadata.txt).

-comment: Comentario para el mix (sobrescribe metadata.txt).

-subtitle: Subtítulo para el mix (sobrescribe metadata.txt).

-track: Número de pista para los metadatos.

-no-portada: Omitir la selección de portada. Si no se usa, el programa pedirá que selecciones una imagen de la carpeta portada.

Ejemplos de Uso
Crear un mix de 5 minutos con archivo de salida y metadatos personalizados:



python intromix_creator.py -r ./musica -d mix_final.mp3 -t 5:30 --title "Mix Electrónico" --artist "DJ Max" --year "2024"
Crear un mix de 10 minutos sin portada:



python intromix_creator.py -r ./musica -d mix_final.mp3 -t 10:00 -no-portada
Crear un mix de 15 minutos con efectos y intros:



python intromix_creator.py -r ./musica -d mix_final.mp3 -t 15:00 -album "Mezcla Especial" -artist "DJ Max" --genre "House"
Archivos de Configuración
metadata.txt
Puedes definir metadatos predeterminados en un archivo llamado metadata.txt. Aquí puedes establecer valores para el título, artista, álbum, género, año, comentario y otros campos. El archivo debe seguir este formato:

txt

artista = DJ Max
titulo = Mix Electrónico
album = Especial
año = 2024
genero = Electrónica
comentario = Mix creado con Intromix Creator
Selección de Portada
Si tienes imágenes en la carpeta portada/, el programa te pedirá que selecciones una imagen para usarla como portada del archivo MP3 exportado. Si no deseas una portada, puedes usar la opción -no-portada.

Exportación
Una vez que el mix esté listo, el programa lo exportará como un archivo MP3 con los metadatos y portada aplicados (si corresponde). Si no se aplican metadatos o portada, el archivo se exportará solo con el audio.

Notas Adicionales
Si la duración del mix es menor que la duración de los archivos MP3 disponibles, el programa repetirá los clips hasta alcanzar la duración deseada.

Los efectos de transición y las intros son opcionales, pero pueden hacer que tu mix suene más profesional y dinámico.

Solución de Problemas
El programa no encuentra archivos MP3: Asegúrate de que la carpeta musica/ contenga archivos MP3 válidos.

No puedo agregar una portada: Verifica que la carpeta portada/ contenga imágenes en formatos soportados (JPG, PNG, GIF, BMP).

Error al cargar los efectos o intros: Asegúrate de que las carpetas efectos/ e intros/ contengan archivos MP3.

Licencia
Este proyecto está licenciado bajo la Licencia MIT