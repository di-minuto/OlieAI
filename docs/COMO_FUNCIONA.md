# Cómo funciona Olie

## Visión general

```
                         ┌──────────────────────────────────────┐
 Mantienes el atajo ───► │ Micrófono (siempre preparado, solo   │
                         │ guarda audio mientras mantienes)     │
                         └──────────────────┬───────────────────┘
                                            ▼
                         ┌──────────────────────────────────────┐
                         │ Whisper (faster-whisper)             │
                         │ voz → texto, en la gráfica si puede  │
                         └──────────────────┬───────────────────┘
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │ ¿Es una orden rápida? (hora, tiempo, música,  │
                    │ volumen, abrir programa…)                     │
                    └───────┬───────────────────────────┬───────────┘
                         sí │                           │ no
                            ▼                           ▼
                 ┌────────────────────┐   ┌──────────────────────────────┐
                 │ Se ejecuta directa │   │ Modelo de lenguaje local     │
                 │ (instantáneo)      │   │ (LM Studio) + herramientas   │
                 └─────────┬──────────┘   └──────────────┬───────────────┘
                           └──────────────┬──────────────┘
                                          ▼
                         ┌──────────────────────────────────────┐
                         │ Piper: texto → voz                   │
                         │ (la mascota bota al ritmo de la voz) │
                         └──────────────────────────────────────┘
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `olie_app.py` | La aplicación: ventana, mascota animada, arranque de LM Studio y bucle principal |
| `asistente_voz.py` | El núcleo: grabación, transcripción, voz, herramientas y conexión con el modelo. Ejecutado directamente funciona en modo consola |
| `config_local.py` | Tus ajustes personales (no se sube a GitHub) |
| `crear_acceso_directo.py` | Crea el acceso directo del escritorio con su icono y su propia identidad en la barra de tareas |
| `ver_microfonos.py` | Lista los micrófonos y mide el volumen, para diagnosticar problemas |
| `Olie (consola).bat` | Abre la versión de consola, útil para ver todos los mensajes en directo |
| `mascota.png` | Las 8 poses de la mascota y sus parpadeos |
| `olie.ico` | Icono de la app |

## El arranque

Al abrir la app, tres cosas se cargan **a la vez** para tardar lo menos posible:

1. **LM Studio y el modelo.** Si el servidor no está encendido, Olie lo enciende con la herramienta `lms` de LM Studio. Después lanza una petición mínima al modelo, y LM Studio lo carga en la gráfica con los ajustes guardados. Si eso falla, lo carga con `lms load` y GPU al máximo.
2. **La voz** (Piper).
3. **El reconocimiento de voz** (Whisper). Primero intenta usar la gráfica NVIDIA y, si no puede, usa el procesador con un modelo más ligero.

En cuanto el reconocimiento de voz está listo, Olie ya te escucha. Las órdenes rápidas funcionan aunque el modelo aún esté cargando; las preguntas esperan a que termine.

## Las órdenes rápidas

Algunas peticiones son tan claras que no hace falta el modelo de lenguaje: se reconocen con patrones de texto y se ejecutan al instante. Son la hora y la fecha, el tiempo, poner música, el control multimedia (pausa, siguiente, volumen…), abrir programas, y despedirse.

Si la frase pide varias cosas a la vez ("abre Brave **y** pon música"), no se usa la vía rápida: se le pasa al modelo, que puede encadenar varias herramientas.

## Las herramientas del modelo

El modelo de lenguaje decide por sí mismo cuándo usar cada herramienta. En la conversación verás cuál usa: `[Olie usa buscar_en_internet: …]`.

| Herramienta | Qué hace | Fuente |
|---|---|---|
| `buscar_en_internet` | Búsqueda web general | DuckDuckGo |
| `buscar_noticias` | Noticias recientes, filtrables por día, semana o mes | DuckDuckGo News |
| `leer_pagina` | Lee el texto de una web para tener más detalle | La propia web |
| `partidos_futbol` | Calendario de partidos con horas y resultados, destacados primero | Servicio público de ESPN |
| `consultar_tiempo` | Tiempo actual y de mañana | Open-Meteo |
| `poner_musica` | Busca una canción y la abre en modo radio | YouTube Music o Spotify |
| `control_multimedia` | Pausa, siguiente, anterior, volumen, silencio | Teclas multimedia de Windows |
| `abrir_programa` | Abre programas por su nombre | Windows |
| `abrir_web` | Abre una web en el navegador | — |
| `crear_archivo` | Crea archivos de texto sin sobrescribir nunca | — |
| `abrir_carpeta` | Abre Escritorio, Documentos, Descargas… (también si están en OneDrive) | — |
| `listar_archivos` | Lista el contenido de una carpeta | — |
| `escribir_texto` | Teclea un texto en la ventana activa | — |
| `bloquear_pc` | Bloquea el equipo | — |
| `ejecutar_comando` | Ejecuta PowerShell **tras tu confirmación** | Windows |

### Seguridad de los comandos

`ejecutar_comando` es la herramienta más potente y la más delicada. Por eso:

- **Siempre pide confirmación** por voz o con botones antes de ejecutar nada. Si no hay respuesta en 30 segundos, se cancela.
- El comando exacto se muestra en la conversación antes de pedir confirmación.
- El modelo tiene instrucciones de **no obedecer nunca órdenes que aparezcan dentro de páginas web** o resultados de búsqueda: solo te obedece a ti. Esto protege frente a webs que intenten "colarle" instrucciones.
- Los comandos tienen un límite de 60 segundos.

## La mascota

La animación está pensada para que se sienta orgánica y no tiemble:

- **Muelles amortiguados:** posición, inclinación y escala se mueven hacia su objetivo como un objeto con peso, acelerando y frenando con suavidad.
- **Caché de imágenes:** las transformaciones se calculan en pasos mínimos (0,4 % de escala, 0,25° de giro) y se reutilizan, así que la textura no "hierve" al moverse.
- **Reloj real:** la animación avanza según el tiempo transcurrido, no según los fotogramas, así que va siempre a la misma velocidad.
- **Reacción a la voz:** mientras habla, la amplitud de su voz (calculada cada 20 ms) mueve la mascota, suavizada con subida rápida y bajada lenta.
- **Parpadeo** aleatorio cada 3–6 segundos, a veces doble.
- **Fundido** entre poses con un pequeño "respiro" elástico.

## Hilos

- **Hilo principal:** la ventana (Tkinter) y la animación.
- **Hilo de trabajo:** carga de modelos, escucha, transcripción, herramientas y voz. Se comunica con la ventana mediante colas, nunca tocándola directamente.
- **Hilo del teclado:** detecta el atajo en todo Windows (pynput).
- **Callback del micrófono:** guarda el audio en un búfer circular. Así, al pulsar el atajo, también se aprovechan las 0,3 s anteriores y no se pierde el principio de la frase.
