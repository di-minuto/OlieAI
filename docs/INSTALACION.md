# Guía de instalación

Esta guía parte de cero: un PC con Windows sin nada instalado. Si ya tienes algo (Python, LM Studio…), salta ese paso.

**Tiempo aproximado:** 30–45 minutos, la mayor parte esperando descargas.

## Índice

1. [Qué necesitas](#1-qué-necesitas)
2. [Instalar Python](#2-instalar-python)
3. [Descargar Olie](#3-descargar-olie)
4. [Instalar las librerías](#4-instalar-las-librerías)
5. [Instalar LM Studio](#5-instalar-lm-studio)
6. [Descargar el modelo de IA](#6-descargar-el-modelo-de-ia)
7. [Configurar LM Studio](#7-configurar-lm-studio)
8. [Tus ajustes personales (opcional)](#8-tus-ajustes-personales-opcional)
9. [Crear el acceso directo](#9-crear-el-acceso-directo)
10. [Primer arranque](#10-primer-arranque)

---

## 1. Qué necesitas

| Componente | Mínimo | Recomendado |
|---|---|---|
| Sistema | Windows 10 | Windows 11 |
| Memoria RAM | 16 GB | 16 GB o más |
| Tarjeta gráfica | No obligatoria (todo funcionará en el procesador, pero lento) | NVIDIA con 8 GB o más (por ejemplo, RTX 3060 de 12 GB) |
| Disco | 15 GB libres | Disco SSD (el modelo carga mucho más rápido) |
| Micrófono | Cualquiera | Auriculares con micrófono o micrófono de sobremesa |
| Internet | Para la instalación | Además, para búsquedas, tiempo, fútbol y música |

> **Sobre la tarjeta gráfica:** Olie usa dos modelos de IA a la vez: el de lenguaje (el "cerebro") y el de reconocimiento de voz. Con una gráfica NVIDIA de 12 GB caben los dos y Olie responde en uno o dos segundos. Sin gráfica también funciona, pero cada respuesta puede tardar bastante más y conviene usar modelos pequeños.

---

## 2. Instalar Python

1. Ve a [python.org/downloads](https://www.python.org/downloads/) y descarga la última versión para Windows (3.12 o superior).
2. Ejecuta el instalador y, **antes de pulsar "Install"**, marca la casilla **"Add Python to PATH"**. Es imprescindible.
3. Comprueba que funciona. Abre una terminal (tecla Windows, escribe `cmd` y pulsa Enter) y escribe:
   ```
   python --version
   ```
   Debería mostrar algo como `Python 3.14.0`. Si dice que no reconoce el comando, reinstala Python marcando la casilla del PATH.

---

## 3. Descargar Olie

**Opción A, sin Git (la más sencilla):**
1. En la página del repositorio pulsa el botón verde **Code → Download ZIP**.
2. Descomprime el ZIP en una carpeta fija, por ejemplo `C:\Users\TuNombre\Olie`. No lo dejes en Descargas, porque el acceso directo apuntará a esa carpeta.

**Opción B, con Git:**
```
git clone https://github.com/di-minuto/OlieAI.git
cd OlieAI
```

---

## 4. Instalar las librerías

1. Abre la carpeta de Olie en el Explorador de archivos.
2. Haz clic en la barra de direcciones (arriba, donde aparece la ruta), borra lo que hay, escribe `cmd` y pulsa Enter. Se abrirá una terminal ya situada en esa carpeta.
3. Instala las librerías:
   ```
   pip install -r requirements.txt
   ```
4. **Solo si tienes una gráfica NVIDIA**, instala también las librerías que permiten usarla para el reconocimiento de voz (pesan más de 1 GB):
   ```
   pip install -r requirements-gpu.txt
   ```

Si al final ves `Successfully installed`, todo ha ido bien. Algunos avisos en amarillo son normales.

---

## 5. Instalar LM Studio

[LM Studio](https://lmstudio.ai) es el programa que ejecuta el modelo de IA en tu ordenador. Olie se conecta a él.

1. Ve a [lmstudio.ai](https://lmstudio.ai) y descarga **LM Studio** para Windows.
   > ⚠️ En la misma web también aparece **Bionic**, otra aplicación de la misma empresa. **No es la que necesitas.** Busca el botón que dice "Download LM Studio" (a veces está más abajo en la página).
2. Instálalo y **ábrelo al menos una vez**. Al abrirlo se instala también su herramienta de línea de comandos (`lms`), que Olie usa para encender LM Studio y cargar el modelo automáticamente.

---

## 6. Descargar el modelo de IA

El modelo es el "cerebro" de Olie. Tiene que cumplir dos condiciones:

- **Admitir herramientas**, para poder buscar en internet, abrir programas, etc. En LM Studio se reconocen por el **icono del martillo** 🔨.
- **Caber en la memoria de tu gráfica.**

### Qué modelo elegir

| Memoria de tu gráfica | Tamaño de modelo | Ejemplo |
|---|---|---|
| 12 GB o más | 12B | `google/gemma-4-12b-qat` (el recomendado, ~7 GB) |
| 8 GB | 7B – 9B | Un Qwen de 8B en versión Q4_K_M |
| 6 GB | ~4B | Un Qwen o Gemma de 4B en versión Q4_K_M |
| Sin gráfica | 4B o menos | Funcionará, pero lento |

> Para saber cuánta memoria tiene tu gráfica: pulsa `Ctrl + Shift + Esc` → pestaña **Rendimiento** → **GPU** → "Memoria de GPU dedicada".

### Cómo descargarlo

1. En LM Studio, pulsa el icono de la **lupa** (Discover) en la barra lateral izquierda.
2. Busca el modelo (por ejemplo `gemma-4-12b-qat`).
3. Comprueba que tiene el **icono del martillo** y que LM Studio no lo marca en rojo (eso significaría que no cabe).
4. Si hay varias versiones, elige **Q4_K_M** o **QAT**: es el mejor equilibrio entre calidad y tamaño.
5. Pulsa **Download** y espera.

---

## 7. Configurar LM Studio

Estos ajustes se hacen una sola vez y marcan una diferencia enorme en la velocidad.

### 7.1. Que use la tarjeta gráfica

1. Abre la configuración (icono del engranaje abajo a la izquierda) → **Hardware**.
2. Comprueba que aparece tu gráfica y que está en **ON**.
3. Activa **"Limit Model Offload to Dedicated GPU Memory"**. Así, si un modelo no cabe en la gráfica, LM Studio te avisa en lugar de usar la memoria normal del PC, que es lentísima.
4. En **Runtime** (`Ctrl + Shift + R`), elige el motor **CUDA llama.cpp** si tu gráfica es NVIDIA, o **Vulkan llama.cpp** si es AMD o Intel.

### 7.2. Ajustes de carga del modelo

1. Ve a **My Models** (icono de carpeta en la barra lateral) y pulsa el **engranaje** junto a tu modelo.
2. En la pestaña **Load**:
   - **GPU Offload:** al máximo (todo el modelo en la gráfica).
   - **Context Length:** `8192`. Más contexto ocupa memoria y no aporta nada a un asistente de voz.

Estos ajustes se guardan, y Olie los usará cada vez que cargue el modelo.

### 7.3. Desactivar el razonamiento ("thinking")

Algunos modelos, como Gemma 4, "piensan" en silencio antes de responder. Para un asistente de voz eso solo añade espera, y a veces provoca respuestas vacías.

1. En los ajustes del modelo, ve a la pestaña **Inference**.
2. Busca la opción de razonamiento. Según la versión de LM Studio puede estar en:
   - **Custom Fields → Enable Thinking**: desactívala.
   - **Reasoning → Reasoning Budget**: marca la casilla y pon `0`.
3. Pulsa **Load Model** para recargar el modelo con el cambio.

> Para comprobarlo, abre un chat en LM Studio y escríbele algo: si responde directamente, sin un bloque de "pensando…", ya está.

---

## 8. Tus ajustes personales (opcional)

1. En la carpeta de Olie, copia `config_local.ejemplo.py` y renombra la copia como `config_local.py`.
2. Ábrelo con el Bloc de notas y cambia lo que quieras, por ejemplo tu ciudad:
   ```python
   CIUDAD_POR_DEFECTO = "Sevilla"
   NAVEGADOR = "predeterminado"
   ```

Este archivo no se sube a GitHub, así que tus datos se quedan en tu PC. Consulta [CONFIGURACION.md](CONFIGURACION.md) para ver todos los ajustes.

---

## 9. Crear el acceso directo

En la terminal, dentro de la carpeta de Olie:
```
python crear_acceso_directo.py
```

Aparecerá un icono **Olie** en el escritorio. Si quieres, haz clic derecho sobre él → **Anclar a la barra de tareas** (en Windows 11 puede estar dentro de "Mostrar más opciones").

---

## 10. Primer arranque

1. Haz doble clic en el icono **Olie**. **No hace falta abrir LM Studio antes:** Olie lo enciende y carga el modelo él solo.
2. La primera vez descargará:
   - El modelo de reconocimiento de voz: unos 1,5 GB con gráfica NVIDIA o unos 500 MB sin ella.
   - La voz: unos 60 MB.

   Puede tardar varios minutos. Las siguientes veces arrancará en segundos.
3. Si Windows pregunta por el **acceso al micrófono**, permítelo. Si no te oye, revisa *Configuración → Privacidad y seguridad → Micrófono* y comprueba que las aplicaciones de escritorio pueden usarlo.
4. Cuando oigas "Olie a su servicio", **mantén `Ctrl izquierdo + Alt izquierdo`, habla y suelta.**

En la conversación de la ventana verás si el reconocimiento de voz va por la gráfica (`Reconocimiento de voz: tarjeta gráfica`) y cuánto tarda en estar todo listo.

¡Listo! Sigue con la [guía de uso](USO.md). Si algo falla, mira [PROBLEMAS.md](PROBLEMAS.md).
