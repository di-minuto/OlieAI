# Solución de problemas

**Lo primero:** casi todos los problemas dejan rastro. Mira la conversación de la ventana, el archivo `olie.log` de la carpeta de Olie, o abre `Olie (consola).bat` para ver los mensajes en directo.

## Instalación

### `pip` no se reconoce como comando
Python no se añadió al PATH. Reinstala Python marcando **"Add Python to PATH"**, o usa `python -m pip install -r requirements.txt`.

### Error al instalar `pyaudio` o "Microsoft Visual C++ 14.0 is required"
Olie no usa PyAudio (usa `sounddevice`). Si te aparece, estás instalando una lista de librerías antigua: usa la de `requirements.txt`.

### Avisos de "symlinks" o "HF_TOKEN" la primera vez
Son avisos de la librería que descarga el modelo de reconocimiento de voz, no errores. Puedes ignorarlos y esperar a que termine la descarga.

## LM Studio y el modelo

### "No encuentro la herramienta 'lms' de LM Studio"
Abre LM Studio una vez después de instalarlo para que se instale su herramienta de línea de comandos. Mientras tanto puedes encender el servidor a mano: en LM Studio, pestaña **Developer** → interruptor **Status: Running**.

### "No consigo conectar con LM Studio"
- Comprueba que LM Studio está instalado y que tienes al menos un modelo descargado.
- Si cambiaste el puerto del servidor, ajusta `SERVIDOR_LM` en `config_local.py`.

### Responde vacío o "el modelo no me ha dado respuesta"
El modelo tiene activado el modo de razonamiento y gasta el espacio pensando. Desactívalo: ajustes del modelo → **Inference** → **Custom Fields → Enable Thinking** (apagado) o **Reasoning → Reasoning Budget** = `0`. Recarga el modelo.

### Responde muy lento o el PC se arrastra
- El modelo no está en la gráfica. En LM Studio: **GPU Offload** al máximo, motor **CUDA llama.cpp** (NVIDIA) y **"Limit Model Offload to Dedicated GPU Memory"** activado.
- El modelo es demasiado grande para tu gráfica. Usa uno más pequeño (ver la tabla de la [guía de instalación](INSTALACION.md#qué-modelo-elegir)).
- Con 6 GB de gráfica o menos, pon `USAR_GPU = False` para que el reconocimiento de voz no compita por la memoria.

### "Este modelo no admite herramientas"
El modelo no puede buscar ni manejar el PC. Descarga uno con el **icono del martillo** en LM Studio.

### Arranca despacio
Cargar un modelo de 7 GB lleva de 10 a 30 segundos según el disco. Para arrancar casi al instante, consulta [Arranque rápido](CONFIGURACION.md#arranque-rápido).

## Voz y micrófono

### No me oye ("No he entendido nada")
1. Ejecuta `python ver_microfonos.py`: lista los micrófonos, marca el predeterminado y dibuja una barra que se mueve al hablar.
2. Si la barra no se mueve, revisa en Windows *Configuración → Sistema → Sonido* qué micrófono es el predeterminado y su volumen.
3. Revisa *Configuración → Privacidad y seguridad → Micrófono* y permite el acceso a las aplicaciones de escritorio.

### Me entiende mal
- Comprueba que el reconocimiento va por la gráfica (al arrancar debe decir `Reconocimiento de voz: tarjeta gráfica (large-v3-turbo)`).
- Sin gráfica, cambia `MODELO_WHISPER` a `"medium"`.
- Si confunde siempre las mismas palabras (nombres propios, por ejemplo), añádelas a `PISTA_WHISPER`.
- Empieza a hablar justo al pulsar y suelta al terminar la frase.

### "Library cublas64_12.dll is not found"
Faltan las librerías de NVIDIA para el reconocimiento de voz:
```
pip install -r requirements-gpu.txt
```
Mientras tanto, Olie funciona con el procesador.

### Olie se cierra de golpe al arrancar
Puede ser un problema con las librerías de la gráfica. Pon `USAR_GPU = False` en `config_local.py` y avísanos en un *issue* con el contenido de `olie.log`.

### La voz suena entrecortada o repetida
El ordenador está saturado. Asegúrate de que el modelo está en la gráfica y no en el procesador (ver "Responde muy lento").

### Pronuncia mal una palabra
Añádela a `PRONUNCIACION` en `config_local.py`, escrita como suena:
```python
PRONUNCIACION = {"Olie": "Óli", "YouTube": "Yutub"}
```

## Atajo de teclado

### El atajo no hace nada
- Usa las teclas del lado **izquierdo**: `Ctrl izquierdo + Alt izquierdo`.
- Si mientras lo mantienes pulsas otra tecla, se cancela a propósito (para no interferir con otros atajos).
- Algunos programas que se ejecutan como administrador no dejan que otras apps lean el teclado mientras están en primer plano. Prueba con otra ventana activa.

## Música

### YouTube Music se abre pero no suena
El navegador bloquea la reproducción automática. En Brave: `brave://settings/content/autoplay` → añade `music.youtube.com` a los permitidos. Inicia sesión en YouTube Music una vez.

### Spotify abre la página pero no reproduce
La web de Spotify no permite empezar a reproducir sin pulsar el play. Usa YouTube Music (`PLATAFORMA_MUSICA = "youtube_music"`), que sí suena sola.

### Sale "Obtener una aplicación para abrir este vínculo de 'spotify'"
No tienes la aplicación de Spotify instalada. Olie lo detecta y abre la versión web; si te sigue saliendo, actualiza Olie.

## Icono y acceso directo

### En la barra de tareas sale el icono de Python
1. Desancla el icono antiguo de la barra de tareas.
2. Ejecuta de nuevo `python crear_acceso_directo.py`.
3. Ancla el nuevo acceso directo y abre Olie siempre desde él.
4. Si sigue igual, reinicia el PC: Windows guarda los iconos en caché.

### El acceso directo no funciona después de mover la carpeta
El acceso directo apunta a la carpeta donde estaba Olie. Vuelve a ejecutar `python crear_acceso_directo.py` desde la nueva ubicación.

## Fútbol, tiempo y búsquedas

### No encuentra partidos de una competición
El calendario depende del servicio público de ESPN. Si alguna competición no aparece, Olie probará con una búsqueda de noticias. Puedes preguntar especificando la competición: "¿Qué partidos de la Premier hay hoy?".

### Las respuestas de actualidad son pobres
Un modelo local pequeño razona peor que los grandes asistentes en la nube. Usar el modelo más grande que quepa en tu gráfica mejora mucho los resultados.

---

¿No está tu problema? Abre un [issue](https://github.com/di-minuto/OlieAI/issues) con lo que hiciste, lo que pasó y el contenido de `olie.log` (revísalo antes y borra lo que no quieras compartir).
