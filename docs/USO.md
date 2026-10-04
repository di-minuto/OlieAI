# Guía de uso

## Hablar con Olie

Hay tres formas:

| Forma | Cómo |
|---|---|
| **Atajo de teclado** | Mantén **`Ctrl izquierdo + Alt izquierdo`**, habla y suelta. Funciona aunque la ventana esté minimizada. |
| **Botón** | Mantén pulsado el botón **🎙 Mantener** de la ventana mientras hablas. |
| **Escribiendo** | Escribe en la caja de texto de la ventana y pulsa Enter. |

Al empezar a grabar suena un pitido corto. En cuanto sueltas, Olie deja de escuchar y responde.

> **Detalles del atajo:** solo funciona con las teclas del lado **izquierdo**, para que no se active al escribir `@`, `#` o `€` con AltGr. Si mientras lo mantienes pulsas cualquier otra tecla (porque estabas usando otro atajo de Windows), Olie lo ignora.

## La mascota

Olie cambia de expresión según lo que está haciendo:

| Estado | Qué hace |
|---|---|
| En espera | Flota suavemente, respira y parpadea de vez en cuando |
| Escuchando | Abre mucho los ojos y se inclina hacia ti, con anillos de luz |
| Pensando | Se balancea con puntos de luz girando alrededor |
| Hablando | Bota al ritmo de su voz, con ondas de sonido |
| Al terminar | Pone cara contenta y da dos saltitos |
| Esperando confirmación | Inclina la cabeza, con un bocadillo de pregunta |
| Error | Se desanima y aparece un aviso |

## Qué puedes pedirle

### Conversación y preguntas
Cualquier pregunta. Si necesita información actual, buscará en internet sin que se lo pidas.
- "¿Quién ganó el último Mundial?"
- "Explícame qué es un agujero negro"
- "¿Cómo se hace una tortilla de patatas?"

### Noticias
- "¿Qué noticias hay hoy?"
- "¿Qué ha pasado con las elecciones de…?"

### Fútbol
Consulta un calendario real, con horas y resultados, y te dice primero los partidos más destacados.
- "¿Juega hoy España?"
- "¿Qué partidos de la Liga de Naciones hay hoy?"
- "¿Quién juega mañana en LaLiga?"
- "¿Cómo quedó ayer el Real Madrid?"
- "¿Qué partidos de Champions hay esta semana?"

Competiciones: LaLiga, Segunda División, Copa del Rey, Supercopa, Champions, Europa League, Conference League, Premier League, Serie A, Bundesliga, Ligue 1, Liga de Naciones, clasificación para el Mundial, Mundial, Eurocopa y amistosos de selecciones.

### El tiempo
- "¿Qué tiempo hace?" (usa tu ciudad por defecto, o te pregunta cuál)
- "¿Qué tiempo hará mañana en Bilbao?"
- "¿Va a llover hoy?"

### Hora y fecha
- "¿Qué hora es?" · "¿Qué día es hoy?"

### Música
Por defecto usa **YouTube Music**, donde empieza a sonar sola y, al terminar, sigue con una radio de canciones parecidas.
- "Ponme música de Estopa"
- "Pon Bohemian Rhapsody"
- "Ponme algo de lofi" · "Pon música de los 2000"
- "Pon… en Spotify" (en la web de Spotify tendrás que pulsar el play)

Control de la reproducción y del volumen:
- "Pausa" · "Siguiente" · "Anterior"
- "Sube el volumen" · "Baja el volumen" · "Silencio"

### Programas y webs
- "Abre la calculadora" · "Abre Word" · "Abre Spotify" · "Abre la configuración"
- "Abre la web de la Agencia Tributaria"

Programas que reconoce por su nombre: navegador, Chrome, Edge, Firefox, Brave, Opera, WhatsApp, Discord, Steam, bloc de notas, calculadora, explorador, Paint, Word, Excel, PowerPoint, Spotify, configuración, terminal, YouTube y correo. Puedes añadir más (ver [CONFIGURACION.md](CONFIGURACION.md)).

### Archivos y carpetas
- "Créame en el escritorio una lista de la compra con leche, huevos y pan"
- "Crea un archivo de notas en documentos con… y ábrelo"
- "Abre la carpeta de descargas"
- "¿Qué archivos tengo en el escritorio?"

Olie **nunca sobrescribe** un archivo: si ya existe uno con ese nombre, crea `nombre (2).txt`.

### Escribir por ti
- "Escribe: llego en diez minutos" (lo teclea en la ventana que tengas activa)

### Bloquear el PC
- "Bloquea el ordenador"

### Cualquier otra cosa de Windows (con confirmación)
Para lo que no cubren las herramientas anteriores, Olie puede ejecutar comandos de PowerShell:
- "Apaga el ordenador en 10 minutos"
- "Cierra el Bloc de notas"
- "¿Cuánto espacio libre queda en el disco C?"

**Antes de ejecutar cualquier comando, Olie te dice qué va a hacer y espera tu confirmación.** Puedes responder:
- **Con la voz:** mantén el atajo y di "sí" (o "adelante", "hazlo", "confirmo"…). Cualquier otra respuesta lo cancela.
- **Con los botones** "Sí, ejecutar" / "No" que aparecen en la ventana.

Si no respondes en 30 segundos, se cancela.

> ⚠️ **Importante:** la explicación que oyes la redacta el propio modelo, y puede equivocarse. El comando exacto aparece siempre en la conversación como `[Comando propuesto] …`. Échale un vistazo antes de aceptar, sobre todo si tiene que ver con borrar archivos, el registro o los ajustes del sistema. Ante la duda, di que no.

### Varias cosas a la vez
- "Abre Brave y ponme música de Rosalía"
- "Busca la receta de la paella y créame un archivo con los ingredientes"

### Despedirse
- "Adiós" · "Hasta luego" · "Apágate"

Olie se despide y se cierra.

## Al cerrar Olie

Por defecto, al cerrar la ventana Olie **descarga el modelo de la gráfica y cierra LM Studio**, para que la memoria de la gráfica quede libre (para juegos, por ejemplo). La contrapartida es que el siguiente arranque tiene que volver a cargar el modelo.

Si prefieres que arranque casi al instante, consulta la sección [Arranque rápido](CONFIGURACION.md#arranque-rápido).

## Privacidad

- El reconocimiento de voz, el modelo de lenguaje y la voz funcionan **en tu ordenador**. Lo que dices no se envía a ningún servicio de IA externo.
- Solo salen a internet las consultas que lo necesitan: búsquedas (DuckDuckGo), noticias, tiempo (Open-Meteo), partidos (ESPN) y música (YouTube Music o Spotify), igual que si las hicieras tú desde el navegador.
- Olie solo graba **mientras mantienes el atajo** o el botón. El icono de micrófono en uso de Windows aparece mientras la app está abierta porque el micrófono queda preparado, pero lo que suena fuera de esos momentos se descarta.
- La conversación se guarda en `olie.log`, en la carpeta de Olie. Puedes borrarlo cuando quieras.
