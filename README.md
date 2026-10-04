<div align="center">

<img src="docs/olie.gif" alt="Olie, el asistente de voz" width="360">

# Olie

**Asistente de voz para Windows que funciona en tu propio ordenador.**

Le hablas manteniendo un atajo de teclado, te entiende, busca lo que haga falta, maneja tu PC y te contesta con voz.
Todo con un modelo de IA local: sin suscripciones, sin claves de API y sin enviar tu voz a ningún servicio externo.

[Instalación](docs/INSTALACION.md) · [Uso](docs/USO.md) · [Configuración](docs/CONFIGURACION.md) · [Cómo funciona](docs/COMO_FUNCIONA.md) · [Problemas](docs/PROBLEMAS.md)

</div>

---

## Qué puede hacer

- 💬 **Conversar** con un modelo de lenguaje local a través de [LM Studio](https://lmstudio.ai).
- 🔎 **Buscar en internet** y leer páginas web para responder sobre temas actuales.
- 📰 **Noticias** recientes, filtradas por fecha.
- ⚽ **Fútbol:** partidos de hoy, mañana o de la semana, con horas y resultados (LaLiga, Champions, Liga de Naciones, Premier y más), con los destacados primero.
- 🌦️ **El tiempo** actual y de mañana en cualquier ciudad.
- 🎵 **Música** en YouTube Music (empieza a sonar sola y sigue con canciones parecidas) o en Spotify, con control de volumen y reproducción.
- 🖥️ **Manejar el PC:** abrir programas y carpetas, crear archivos, escribir texto, bloquear el equipo.
- ⚙️ **Cualquier tarea de Windows** mediante PowerShell, **siempre pidiendo confirmación** antes.
- 🫧 **Una mascota animada** que escucha, piensa, habla, se alegra y parpadea.

## Qué necesitas

| | |
|---|---|
| **Sistema** | Windows 10 u 11 |
| **Python** | 3.12 o superior |
| **LM Studio** | Con un modelo que admita herramientas (icono 🔨), por ejemplo Gemma 4 12B |
| **Gráfica** | Recomendada una NVIDIA con 8 GB o más (con 12 GB caben el modelo y el reconocimiento de voz a la vez) |
| **Micrófono** | Cualquiera |

## Instalación rápida

> ¿Es tu primera vez con Python o LM Studio? Sigue la **[guía de instalación paso a paso](docs/INSTALACION.md)**, que lo explica todo desde cero.

```
git clone https://github.com/di-minuto/OlieAI.git
cd OlieAI
pip install -r requirements.txt
pip install -r requirements-gpu.txt      # solo con gráfica NVIDIA
python crear_acceso_directo.py
```

En **LM Studio**:
1. Descarga un modelo con el icono 🔨 (recomendado: `google/gemma-4-12b-qat`).
2. En sus ajustes de carga: **GPU Offload** al máximo y **Context Length** en `8192`.
3. Desactiva el razonamiento (*thinking*).

Después abre **Olie** desde el icono del escritorio. No hace falta abrir LM Studio antes: Olie lo enciende y carga el modelo él solo.

## Uso

**Mantén `Ctrl izquierdo + Alt izquierdo`, habla y suelta.** También puedes mantener el botón 🎙 de la ventana o escribirle.

| Dile… | Y Olie… |
|---|---|
| "¿Qué tiempo hace mañana en Madrid?" | Consulta la previsión |
| "¿Juega hoy España?" | Mira el calendario de partidos |
| "¿Qué noticias hay hoy?" | Busca las últimas noticias |
| "Ponme música de los 2000" | Busca canciones y las pone en YouTube Music |
| "Sube el volumen" · "Pausa" · "Siguiente" | Controla la reproducción |
| "Créame en el escritorio una lista de la compra con leche y pan" | Crea el archivo |
| "Abre Brave y ponme lofi" | Encadena las dos cosas |
| "Apaga el ordenador en 10 minutos" | Te pide confirmación y lo ejecuta |

Más ejemplos en la **[guía de uso](docs/USO.md)**.

## Cómo funciona

```
 Tú hablas ──► Whisper ──► Modelo local (LM Studio) ──► Piper ──► Olie te responde
              (voz a texto)        │                     (texto a voz)
                                   ▼
                     Herramientas: internet, noticias, fútbol,
                     tiempo, música, archivos, programas, PowerShell
```

Los detalles (arranque en paralelo, órdenes rápidas, herramientas, seguridad y animación) están en **[cómo funciona](docs/COMO_FUNCIONA.md)**.

## Configuración

Copia `config_local.ejemplo.py` como `config_local.py` y cambia ahí lo que quieras: tu ciudad, el navegador, la voz, el nombre del asistente… Ese archivo no se sube al repositorio. Todos los ajustes están explicados en **[configuración](docs/CONFIGURACION.md)**.

## Privacidad

El reconocimiento de voz, el modelo de lenguaje y la voz funcionan **en tu ordenador**. Solo salen a internet las consultas que lo necesitan (búsquedas, noticias, tiempo, partidos y música), igual que si las hicieras tú desde el navegador. Olie solo graba mientras mantienes el atajo.

## Estructura

```
olie_app.py                App con interfaz y mascota animada
asistente_voz.py           Núcleo: voz, herramientas y modelo (también funciona en consola)
config_local.ejemplo.py    Plantilla para tus ajustes personales
crear_acceso_directo.py    Crea el acceso directo con su icono
ver_microfonos.py          Diagnóstico del micrófono
Olie (consola).bat         Versión de consola, para depurar
mascota.png                Poses y parpadeos de la mascota
olie.ico                   Icono
requirements.txt           Librerías necesarias
requirements-gpu.txt       Librerías para usar la gráfica NVIDIA
docs/                      Documentación
```

## Créditos

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) · reconocimiento de voz
- [Piper](https://github.com/OHF-Voice/piper1-gpl) · síntesis de voz (voz `es_ES-davefx-medium`)
- [LM Studio](https://lmstudio.ai) · servidor del modelo local
- [ddgs](https://pypi.org/project/ddgs/) · búsquedas en DuckDuckGo
- [Open-Meteo](https://open-meteo.com) · datos del tiempo
- Calendario de fútbol del servicio público (no oficial) de ESPN
- Mascota diseñada con ayuda de IA
