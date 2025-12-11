# 🎛️ Intromix  
**Generador automático de *intromix* para DJs y creadores.**

Este proyecto permite crear un *intromix* de forma automática usando intros, efectos y una lista de canciones. Solo necesitas organizar tus archivos y ejecutar el script con los parámetros adecuados.

---

## 📁 Estructura general
Asegúrate de tener las siguientes carpetas:

```

intros/       # Intros iniciales del intromix (mp3)
efectos/      # Efectos que sonarán entre pistas (mp3)
portada/      # Portadas posibles para el intromix (jpg o png)

```

---

## ⚙️ Parámetros de ejecución

| Parámetro | Descripción |
|----------|-------------|
| `-r`     | Ruta donde están tus canciones. |
| `-d`     | Ruta donde será generado el *intromix*. |
| `-t`     | Duración total en formato `minutos:segundos`. |
| `-a`     | Nombre del álbum para el archivo final. |

---

## 🧩 Archivo `.env`
Debes incluir un archivo `.env` con los metadatos básicos del proyecto:

```

TITLE=prueba title
ARTIST=Prueba ARTIST
GENRE=binario

```

---

## 🎶 Funcionamiento
- Los archivos en **`intros`** se usan al inicio del *intromix*.  
- Los archivos en **`efectos`** se intercalan entre canciones dentro del mix.  
- Todos los intros y efectos deben estar en **formato `.mp3`**.  
- La carpeta **`portada`** debe contener imágenes `.jpg` o `.png` para usarse como cover del intromix.

---

## 🚀 Flujo general
1. Prepara tus carpetas (`intros`, `efectos`, `portada`).  
2. Añade tus canciones en la ruta indicada con `-r`.  
3. Configura tu `.env`.  
4. Ejecuta el generador con los parámetros deseados.  
5. El sistema creará el *intromix* respetando el tiempo total y los metadatos.  

---

## 📦 Resultado
En la ruta indicada con `-d` se generará:
- Tu archivo final de **intromix**.  
- Metadatos basados en el `.env`.  
- Portada seleccionada automáticamente (o al azar, según implementación).  

---

### ✨ ¡Listo para mezclar sin esfuerzo!
```
