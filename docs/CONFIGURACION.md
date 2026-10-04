# Configuración

## Dónde poner tus ajustes

Todos los ajustes tienen un valor por defecto en el código, pero **no hace falta tocar el código** para cambiarlos:

1. Copia `config_local.ejemplo.py` como `config_local.py`.
2. Escribe en él solo los ajustes que quieras cambiar:
   ```python
   CIUDAD_POR_DEFECTO = "Sevilla"
   NAVEGADOR = "brave"
   TONO = 1.2
   ```
3. Reinicia Olie.

`config_local.py` está en el `.gitignore`: no se sube a GitHub y no se pierde al actualizar el código. Ahí puedes cambiar cualquier ajuste de `asistente_voz.py`.

Los ajustes de la ventana y la animación están al principio de `olie_app.py` y se cambian directamente en ese archivo.

---

## Ajustes del asistente (`asistente_voz.py`)

### Personalidad

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `NOMBRE` | `"Olie"` | Nombre del asistente |
| `TRATAMIENTO` | `"señor"` | Cómo te llama ("señor", "señora", tu nombre…) |
| `CIUDAD_POR_DEFECTO` | `""` | Ciudad para el tiempo cuando no dices ninguna. Si está vacía, te pregunta |

La personalidad completa (el texto con las instrucciones que recibe el modelo) está en la función `personalidad()`. Puedes editarla para que Olie sea más formal, más cercano, más breve…

### Modelo de lenguaje

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `SERVIDOR_LM` | `"http://localhost:1234/v1"` | Dirección del servidor de LM Studio |
| `MODELO_LM` | `"gemma-4-12b"` | Parte del nombre del modelo que quieres usar. Si no lo encuentra, usa el primer modelo de lenguaje disponible |
| `MAX_HISTORIAL` | `8` | Cuántos mensajes de la conversación recuerda |
| `MAX_PASOS` | `6` | Cuántas herramientas seguidas puede usar para una respuesta |

### Reconocimiento de voz

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `USAR_GPU` | `True` | Usar la gráfica NVIDIA para el reconocimiento de voz |
| `MODELO_WHISPER_GPU` | `"large-v3-turbo"` | Modelo con gráfica: el más preciso |
| `MODELO_WHISPER` | `"small"` | Modelo sin gráfica. `"medium"` entiende mejor, pero es más lento |
| `PISTA_WHISPER` | (frase de ejemplo) | Palabras que Olie espera oír. Añade nombres que confunda a menudo |

> Si tu gráfica tiene 6 GB o menos, pon `USAR_GPU = False` para que el reconocimiento de voz no le quite memoria al modelo de lenguaje.

### Voz

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `VOZ_PIPER` | `"es_ES-davefx-medium"` | Voz de [Piper](https://github.com/OHF-Voice/piper1-gpl). Se descarga sola la primera vez |
| `VOZ_HABLANTE` | `None` | Algunas voces tienen varios hablantes (`0`, `1`…) |
| `TONO` | `1.15` | Mayor que 1: más aguda. Menor que 1: más grave |
| `VELOCIDAD` | `1.0` | Mayor que 1: más despacio. Menor que 1: más deprisa |
| `EFECTO_IA` | `False` | Añade un leve eco robótico |
| `PRONUNCIACION` | `{"Olie": "Óli"}` | Cómo pronunciar palabras concretas. Solo cambia la voz, no el texto |

Otras voces en español: `es_ES-sharvard-medium` (dos hablantes), `es_ES-carlfm-x_low`, `es_MX-claude-high`, `es_AR-daniela-high`.

Ejemplo para que pronuncie bien una palabra:
```python
PRONUNCIACION = {"Olie": "Óli", "YouTube": "Yutub"}
```

### Navegador y música

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `NAVEGADOR` | `"predeterminado"` | `"predeterminado"` (el de Windows) o `"brave"` |
| `PLATAFORMA_MUSICA` | `"youtube_music"` | `"youtube_music"` (empieza a sonar sola) o `"spotify"` (hay que pulsar play) |

> **Si YouTube Music no empieza a sonar solo:** algunos navegadores bloquean la reproducción automática. En Brave, ve a `brave://settings/content/autoplay` y añade `music.youtube.com` a los sitios permitidos. Inicia también sesión en YouTube Music una vez.

### Programas que abre por su nombre

La lista `PROGRAMAS` relaciona lo que dices con lo que se abre. Para añadir programas, define la lista completa en tu `config_local.py`, partiendo de la del código:

```python
PROGRAMAS = {
    "calculadora": "calc",
    "obs": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "github": "https://github.com",
    # …
}
```

Puede ser el nombre de un programa (`calc`, `notepad`), una ruta completa a un `.exe`, una web o un enlace de aplicación (`spotify:`, `ms-settings:`). Los nombres van en minúsculas y sin tildes.

### Atajo de teclado

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `ATAJO_MODIFICADORES` | `Ctrl izq + Alt izq` | Teclas que hay que mantener para hablar |
| `PALABRAS_SI` | "sí", "confirmo", "adelante"… | Respuestas que cuentan como "sí" al confirmar un comando |

---

## Ajustes de la app (`olie_app.py`)

| Ajuste | Por defecto | Descripción |
|---|---|---|
| `DESCARGAR_MODELO_AL_CERRAR` | `True` | Al cerrar Olie, descarga el modelo de la gráfica |
| `CERRAR_LM_STUDIO_AL_SALIR` | `True` | Al cerrar Olie, cierra también LM Studio |
| `CONTEXTO_MODELO` | `"8192"` | Contexto con el que se carga el modelo si hay que cargarlo a mano |
| `FPS` | `40` | Fotogramas por segundo de la animación |
| `INTENSIDAD_MOVIMIENTO` | `1.0` | Cuánto se mueve la mascota. `0.5` = la mitad, `0` = quieta (solo parpadea y cambia de expresión) |
| `COLORES` | Tema oscuro | Colores de la ventana |

### Arranque rápido

Por defecto, Olie descarga el modelo al cerrarse y tiene que volver a cargarlo al abrirse (de 10 a 30 segundos, según tu disco). Si pones:

```python
DESCARGAR_MODELO_AL_CERRAR = False
CERRAR_LM_STUDIO_AL_SALIR = False
```

el modelo se queda cargado en segundo plano y Olie arranca en pocos segundos. La contrapartida es que ocupa la memoria de la gráfica (unos 7 GB con Gemma 4 12B) aunque Olie esté cerrado. Cuando necesites la gráfica para otra cosa, cierra LM Studio a mano desde el icono de la bandeja del sistema.

---

## Cambiar la mascota

Las poses están en `mascota.png`: una tira de 8 poses de 300 × 300 píxeles con fondo transparente (primera fila) y sus versiones parpadeando (segunda fila), en este orden:

`inicio`, `normal`, `escuchando`, `pensando`, `hablando`, `contento`, `pregunta`, `triste`

Para usar otra mascota, crea una imagen con la misma estructura y sustituye `mascota.png`. Si alguna pose no tiene versión parpadeando, repite la misma imagen en la segunda fila y quítala de `PARPADEABLES` en `olie_app.py`. Para el icono, sustituye `olie.ico` y vuelve a ejecutar `python crear_acceso_directo.py`.
