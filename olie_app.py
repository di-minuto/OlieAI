"""
Olie · App de escritorio
------------------------
Interfaz gráfica para el asistente (usa asistente_voz.py como núcleo).
Al abrirla enciende LM Studio y carga el modelo; al cerrarla lo descarga y cierra LM Studio.

Ábrela con el acceso directo del escritorio (créalo una vez con: python crear_acceso_directo.py)
"""

import os
import sys
import math
import queue
import shutil
import threading
import traceback
import subprocess
import time
import random
import tkinter as tk

from PIL import Image, ImageTk

CARPETA = os.path.dirname(os.path.abspath(__file__))
os.chdir(CARPETA)

# Para que Windows muestre el icono de Olie en la barra de tareas (y no el de Python)
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Olie.AsistenteDeVoz")
except Exception:
    pass
sys.path.insert(0, CARPETA)

# ======================= Ajustes de la app =======================
DESCARGAR_MODELO_AL_CERRAR = True   # libera la memoria de la gráfica al cerrar Olie
CERRAR_LM_STUDIO_AL_SALIR = True    # además apaga el servidor y cierra LM Studio por completo
CONTEXTO_MODELO = "8192"

COLORES = {
    "fondo": "#0f141a", "panel": "#161d25", "borde": "#243140", "texto": "#dbe6ef", "tenue": "#7e93a6",
    "tu": "#8fcfff", "olie": "#e7eff6", "herramienta": "#62788c", "info": "#62788c",
    "crema": "#7fd6ff",      # color de los efectos (luz de los ojos)
    "marron": "#1f3a52",     # color de acento oscuro (botones, bocadillos)
}
COLOR_ESTADO = {
    "iniciando": "#7e93a6", "espera": "#7e93a6", "escuchando": "#9fe3ff",
    "pensando": "#c8b6ff", "hablando": "#7fd6ff", "confirmar": "#ffd27a", "error": "#ff7a85",
}
# Poses de la mascota (columnas de mascota.png; la segunda fila son los parpadeos)
POSES = ["inicio", "normal", "escuchando", "pensando", "hablando", "contento", "pregunta", "triste"]
PARPADEABLES = {"inicio", "normal", "escuchando", "pensando", "hablando", "pregunta"}
POSE_ESTADO = {
    "iniciando": "inicio", "espera": "normal", "escuchando": "escuchando", "pensando": "pensando",
    "hablando": "hablando", "confirmar": "pregunta", "error": "triste", "contento": "contento",
}
FPS = 40
INTENSIDAD_MOVIMIENTO = 1.0     # 0.5 = la mitad de movimiento, 0 = quieta (solo parpadea y cambia de pose)
TEXTO_ESTADO = {
    "iniciando": "Iniciando sistemas…", "espera": "En espera · mantén Ctrl izq + Alt izq",
    "escuchando": "Escuchando…", "pensando": "Pensando…", "hablando": "Hablando…",
    "confirmar": "Esperando su confirmación", "error": "Error · revise el registro",
}

cola_ui = queue.Queue()          # mensajes del trabajador a la interfaz
peticiones = queue.Queue()       # audio, texto escrito o botones hacia el trabajador
REGISTRO = open(os.path.join(CARPETA, "olie.log"), "a", encoding="utf-8")


class Salida:
    """Redirige los print() del núcleo a la ventana y a olie.log."""

    def write(self, texto):
        REGISTRO.write(texto)
        REGISTRO.flush()
        for linea in texto.splitlines():
            if linea.strip():
                cola_ui.put(("linea", linea))

    def flush(self):
        pass


sys.stdout = sys.stderr = Salida()


def estado(nombre):
    cola_ui.put(("estado", nombre))


# ======================= LM Studio =======================
def ruta_lms():
    candidatos = [os.path.join(os.path.expanduser("~"), ".lmstudio", "bin", "lms.exe"), shutil.which("lms")]
    return next((c for c in candidatos if c and os.path.exists(c)), None)


def lms(*args, espera=120):
    ruta = ruta_lms()
    if not ruta:
        return None
    try:
        return subprocess.run([ruta, *args], capture_output=True, text=True, timeout=espera,
                              stdin=subprocess.DEVNULL, encoding="utf-8", errors="ignore",
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception as e:
        print(f"(lms {' '.join(args)} ha fallado: {e})")
        return None


def cerrar_lm_studio():
    """Apaga el servidor y cierra LM Studio (no toca Bionic)."""
    import time
    lms("server", "stop", espera=20)
    lms("daemon", "down", espera=20)          # versiones nuevas con servicio en segundo plano
    sin_ventana = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    for forzar in (False, True):
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LM Studio.exe"], capture_output=True, text=True,
                           creationflags=sin_ventana)
        if "LM Studio.exe" not in r.stdout:
            break
        orden = ["taskkill", "/IM", "LM Studio.exe", "/T"] + (["/F"] if forzar else [])
        subprocess.run(orden, capture_output=True, creationflags=sin_ventana)
        time.sleep(3)


def preparar_lm_studio(core):
    import time
    if not core.servidor_disponible():
        if not ruta_lms():
            print("No encuentro la herramienta 'lms' de LM Studio. Abre LM Studio y enciende el servidor a mano.")
        else:
            print("Encendiendo el servidor de LM Studio…")
            lms("server", "start", espera=90)
        for _ in range(60):
            if core.servidor_disponible():
                break
            time.sleep(1)
    if not core.servidor_disponible():
        print("No consigo conectar con LM Studio. Podré hacer órdenes sencillas, pero no conversar.")
        return False

    ids = [m.id for m in core.cliente.models.list().data]
    preferido = core.MODELO_LM.lower()
    elegido = (next((i for i in ids if preferido and preferido in i.lower()), None)
               or next((i for i in ids if "embed" not in i.lower()), None))
    if not elegido:
        print("LM Studio no tiene ningún modelo de lenguaje descargado.")
        return False
    core.MODELO_EN_USO = elegido
    print(f"Cargando el modelo {elegido} en la gráfica (puede tardar unos segundos)…")

    def calentar():
        core.cliente.chat.completions.create(model=elegido, max_tokens=1,
                                             messages=[{"role": "user", "content": "Hola"}])
    try:
        calentar()
    except Exception:
        lms("load", elegido, "--gpu", "max", "--context-length", CONTEXTO_MODELO, espera=300)
        try:
            calentar()
        except Exception as e:
            print(f"(El modelo no responde todavía: {e})")
            return False
    print(f"Modelo listo: {elegido}")
    return True


# ======================= Trabajador (todo lo que no es la ventana) =======================
class Olie:
    def __init__(self):
        self.core = None
        self.grabadora = None
        self.listo = False
        self.modelo_listo = threading.Event()
        self.ocupado = threading.Event()
        self.en_confirmacion = False
        self.grabando = False
        self.cancelado = False
        self.teclas_abajo = set()

    # --- grabación (atajo de teclado o botón) ---
    def empezar(self):
        if not self.listo or self.grabando or (self.ocupado.is_set() and not self.en_confirmacion):
            return
        self.grabando, self.cancelado = True, False
        self.grabadora.empezar()
        self.core.tono_inicio()
        estado("escuchando")

    def terminar(self):
        if not self.grabando:
            return
        self.grabando = False
        audio = self.grabadora.terminar()
        if self.cancelado:
            estado("confirmar" if self.en_confirmacion else "espera")
            return
        peticiones.put(("audio", audio))

    def al_pulsar(self, tecla):
        if tecla in self.core.ATAJO_MODIFICADORES:
            self.teclas_abajo.add(tecla)
            if self.core.ATAJO_MODIFICADORES <= self.teclas_abajo:
                self.empezar()
        elif self.grabando:
            self.cancelado = True        # era otro atajo de teclado

    def al_soltar(self, tecla):
        self.teclas_abajo.discard(tecla)
        if tecla in self.core.ATAJO_MODIFICADORES:
            self.terminar()

    # --- confirmación de comandos (voz o botones) ---
    def confirmar(self, pregunta):
        core = self.core
        self.voz.decir(pregunta)
        self.en_confirmacion = True
        cola_ui.put(("confirmar", True))
        estado("confirmar")
        decision = False
        try:
            while True:
                try:
                    tipo, dato = peticiones.get(timeout=30)
                except queue.Empty:
                    print("  [Sin respuesta: cancelado]")
                    break
                if tipo == "boton":
                    decision = dato
                    break
                texto = dato if tipo == "texto" else core.transcribir(self.whisper, dato) \
                    if len(dato) >= core.FRECUENCIA * core.MIN_FRASE else ""
                if not texto:
                    continue
                print(f"Tú: {texto}")
                t = core.normalizar(texto)
                decision = bool(core.re.search(r"\b(" + "|".join(core.PALABRAS_SI) + r")\b", t)) \
                    and not core.re.search(r"\bno\b", t)
                break
        finally:
            self.en_confirmacion = False
            cola_ui.put(("confirmar", False))
            estado("pensando")
        print("  [Confirmado]" if decision else "  [Cancelado]")
        return decision

    # --- arranque y bucle principal ---
    def ejecutar(self):
        try:
            import time as _t
            inicio = _t.perf_counter()
            estado("iniciando")
            print("Cargando módulos…")
            import asistente_voz as core
            from pynput import keyboard
            self.core = core

            # 1) LM Studio y Gemma: lo más lento, en segundo plano
            def cargar_modelo():
                try:
                    if preparar_lm_studio(core):
                        self.modelo_listo.set()
                        print(f"(Modelo listo en {_t.perf_counter() - inicio:.0f} s)")
                except Exception as e:
                    print(f"(No se pudo preparar LM Studio: {e})")
            hilo_modelo = threading.Thread(target=cargar_modelo, daemon=True)
            hilo_modelo.start()

            # 2) Voz de Piper, a la vez
            resultado_voz = {}
            hilo_voz = threading.Thread(target=lambda: resultado_voz.setdefault("voz", core.Voz()), daemon=True)
            hilo_voz.start()

            # 3) Reconocimiento de voz y micrófono (en este hilo)
            print("Cargando reconocimiento de voz…")
            self.whisper = core.cargar_whisper()
            self.grabadora = core.Grabadora()
            hilo_voz.join()
            self.voz = resultado_voz["voz"]
            decir_original = self.voz.decir

            def decir(texto):
                estado("hablando")
                decir_original(texto)
            self.voz.decir = decir

            core.CONFIRMAR = self.confirmar
            keyboard.Listener(on_press=self.al_pulsar, on_release=self.al_soltar).start()
            self.listo = True
            print(f"(Escuchando desde los {_t.perf_counter() - inicio:.0f} s)")

            if self.modelo_listo.is_set():
                self.voz.decir(f"{core.NOMBRE} a su servicio, {core.TRATAMIENTO}.")
            else:
                self.voz.decir(f"{core.NOMBRE} a su servicio, {core.TRATAMIENTO}. "
                               f"Ya puedo atender órdenes; termino de despertar mi cerebro en unos segundos.")
            estado("espera")
            self.bucle()
        except Exception:
            print("ERROR:\n" + traceback.format_exc())
            estado("error")

    def bucle(self):
        core = self.core
        while True:
            tipo, dato = peticiones.get()
            if tipo == "boton":
                continue
            self.ocupado.set()
            estado("pensando")
            try:
                if tipo == "audio":
                    if len(dato) < core.FRECUENCIA * core.MIN_FRASE:
                        continue
                    texto = core.transcribir(self.whisper, dato)
                    if not texto:
                        core.pitido(440, 150)
                        print("(No he entendido nada)")
                        continue
                else:
                    texto = dato
                print(f"Tú: {texto}")

                if core.es_despedida(texto):
                    self.voz.decir(f"Como desee, {core.TRATAMIENTO}. Hasta pronto.")
                    cola_ui.put(("salir", None))
                    return

                try:
                    respuesta = core.ejecutar_orden(texto)
                    if respuesta is None:
                        if not self.modelo_listo.is_set():
                            print("(Esperando a que termine de cargar el modelo…)")
                            self.modelo_listo.wait(timeout=90)
                        respuesta = core.responder(texto)
                    else:
                        core.historial.append({"role": "user", "content": texto})
                        core.historial.append({"role": "assistant", "content": respuesta})
                except Exception as e:
                    print(f"Error: {e}")
                    respuesta = (f"Me temo que no consigo contactar con el modelo, {core.TRATAMIENTO}. "
                                 f"Compruebe LM Studio.")
                self.voz.decir(respuesta)
            except Exception:
                print("ERROR:\n" + traceback.format_exc())
            finally:
                self.ocupado.clear()
                estado("espera")


# ======================= Ventana =======================
class Ventana:
    def __init__(self, olie):
        self.olie = olie
        self.estado = "iniciando"
        c = COLORES

        self.root = tk.Tk()
        self.root.title("Olie")
        self.root.geometry("480x760")
        self.root.minsize(400, 600)
        self.root.configure(bg=c["fondo"])
        icono = os.path.join(CARPETA, "olie.ico")
        if os.path.exists(icono):
            try:
                self.root.iconbitmap(default=icono)
            except tk.TclError:
                pass
            try:   # icono grande para la barra de tareas (el de iconbitmap solo es el pequeño)
                base = Image.open(icono)
                self._iconos = [ImageTk.PhotoImage(base.resize((lado, lado), Image.LANCZOS))
                                for lado in (256, 64, 32, 16)]
                self.root.iconphoto(True, *self._iconos)
            except Exception:
                pass
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        # Núcleo animado
        self.lienzo = tk.Canvas(self.root, height=300, bg=c["fondo"], highlightthickness=0)
        self.lienzo.pack(fill="x", pady=(10, 0))
        self.etiqueta = tk.Label(self.root, text=TEXTO_ESTADO["iniciando"], bg=c["fondo"], fg=c["tenue"],
                                 font=("Segoe UI Semibold", 10))
        self.etiqueta.pack(pady=(0, 8))

        # Conversación
        marco = tk.Frame(self.root, bg=c["borde"], padx=1, pady=1)
        marco.pack(fill="both", expand=True, padx=14)
        self.chat = tk.Text(marco, bg=c["panel"], fg=c["texto"], wrap="word", relief="flat", padx=12, pady=10,
                            font=("Segoe UI", 10), insertbackground=c["texto"], state="disabled", cursor="arrow")
        barra = tk.Scrollbar(marco, command=self.chat.yview, bg=c["panel"], troughcolor=c["panel"],
                             relief="flat", width=10)
        self.chat.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.chat.pack(side="left", fill="both", expand=True)
        self.chat.tag_configure("tu_nombre", foreground=c["tu"], font=("Segoe UI Semibold", 9))
        self.chat.tag_configure("tu", foreground=c["tu"], spacing3=8)
        self.chat.tag_configure("olie_nombre", foreground="#5cc4ff", font=("Segoe UI Semibold", 9))
        self.chat.tag_configure("olie", foreground=c["olie"], spacing3=8)
        self.chat.tag_configure("herramienta", foreground=c["herramienta"], font=("Consolas", 8), spacing3=4)
        self.chat.tag_configure("info", foreground=c["info"], font=("Segoe UI", 8), spacing3=4)

        # Confirmación (oculta hasta que haga falta)
        self.marco_conf = tk.Frame(self.root, bg=c["fondo"])
        tk.Label(self.marco_conf, text="¿Autoriza el comando?", bg=c["fondo"], fg=c["crema"],
                 font=("Segoe UI Semibold", 10)).pack(side="left", padx=(14, 10))
        for texto, valor, color in (("Sí, ejecutar", True, "#1f8f4e"), ("No", False, "#8f2a33")):
            tk.Button(self.marco_conf, text=texto, bg=color, fg="white", relief="flat", padx=14, pady=4,
                      activebackground=color, font=("Segoe UI", 9),
                      command=lambda v=valor: peticiones.put(("boton", v))).pack(side="left", padx=4)

        # Entrada de texto y botón de hablar
        abajo = tk.Frame(self.root, bg=c["fondo"])
        abajo.pack(fill="x", padx=14, pady=12)
        self.entrada = tk.Entry(abajo, bg=c["panel"], fg=c["texto"], relief="flat", font=("Segoe UI", 10),
                                insertbackground=c["texto"], highlightthickness=1,
                                highlightbackground=c["borde"], highlightcolor="#3d7fb0")
        self.entrada.pack(side="left", fill="x", expand=True, ipady=8)
        self.entrada.bind("<Return>", self.enviar_texto)
        self.boton_voz = tk.Label(abajo, text="🎙  Mantener", bg=c["marron"], fg=c["crema"], padx=14, pady=8,
                                  font=("Segoe UI", 10), cursor="hand2")
        self.boton_voz.pack(side="left", padx=(8, 0))
        self.boton_voz.bind("<ButtonPress-1>", lambda e: self.olie.empezar())
        self.boton_voz.bind("<ButtonRelease-1>", lambda e: self.olie.terminar())

        self.poses_pil = {}
        self.parpadeos = {}
        ruta_hoja = os.path.join(CARPETA, "mascota.png")
        try:
            hoja = Image.open(ruta_hoja).convert("RGBA")
            lado = hoja.width // len(POSES)
            for n, nombre in enumerate(POSES):
                caja = (n * lado, 0, (n + 1) * lado, lado)
                self.poses_pil[nombre] = hoja.crop(caja)
                if hoja.height >= 2 * lado and nombre in PARPADEABLES:
                    self.parpadeos[nombre] = hoja.crop((caja[0], lado, caja[2], 2 * lado))
            self.lado = lado
        except Exception as e:
            print(f"(No se pudo cargar la mascota: {e})")

        # estado de la animación fluida
        self.pose_actual = self.pose_anterior = None
        self.t_cambio = 0.0
        self.escala, self.vel_escala = 1.0, 0.0
        self.ang = self.dy = 0.0
        self.sx = self.sy = 1.0
        self.nivel_mic = self.amp_voz = 0.0
        self.proximo_parpadeo = time.time() + 3
        self.fin_parpadeo = 0.0
        self.contento_hasta = 0.0
        self.foto = None
        self.item_mascota = None
        self.t0 = time.perf_counter()
        self.t_ultimo = self.t0
        self.cache = {}                     # imágenes ya transformadas (evita que la textura "hierva")
        self.ultima_clave = None
        self.ultima_pos = None
        # muelles suaves: [valor, velocidad]
        self.m = {"dy": [0.0, 0.0], "ang": [0.0, 0.0], "sx": [1.0, 0.0], "sy": [1.0, 0.0], "pop": [1.0, 0.0]}
        self.amp_suave = 0.0
        self.mic_suave = 0.0
        self.t_contento = -10.0

        self.root.after(40, self.animar)
        self.root.after(50, self.leer_cola)

    # --- conversación ---
    def escribir(self, texto, etiqueta):
        self.chat.configure(state="normal")
        self.chat.insert("end", texto + "\n", etiqueta)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def mostrar_linea(self, linea):
        nombre = self.olie.core.NOMBRE if self.olie.core else "Olie"
        if linea.startswith("Tú:"):
            self.escribir("TÚ", "tu_nombre")
            self.escribir(linea[3:].strip(), "tu")
        elif linea.startswith(f"{nombre}:"):
            self.escribir(nombre.upper(), "olie_nombre")
            self.escribir(linea[len(nombre) + 1:].strip(), "olie")
        elif linea.strip().startswith("["):
            self.escribir(linea.strip(), "herramienta")
        else:
            self.escribir(linea.strip(), "info")

    def enviar_texto(self, _evento=None):
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.entrada.delete(0, "end")
        if self.olie.en_confirmacion or (self.olie.listo and not self.olie.ocupado.is_set()):
            peticiones.put(("texto", texto))

    def leer_cola(self):
        try:
            while True:
                tipo, dato = cola_ui.get_nowait()
                if tipo == "linea":
                    self.mostrar_linea(dato)
                elif tipo == "estado":
                    if self.estado == "hablando" and dato == "espera":
                        self.contento_hasta = time.time() + 1.6
                    self.estado = dato
                    self.etiqueta.configure(text=TEXTO_ESTADO.get(dato, dato),
                                            fg=COLOR_ESTADO.get(dato, COLORES["tenue"]))
                elif tipo == "confirmar":
                    if dato:
                        self.marco_conf.pack(fill="x", pady=(8, 0), before=self.entrada.master)
                    else:
                        self.marco_conf.pack_forget()
                elif tipo == "salir":
                    self.root.after(300, self.cerrar)
        except queue.Empty:
            pass
        self.root.after(50, self.leer_cola)

    # --- núcleo animado ---
    def animar(self):
        if self.poses_pil:
            self.animar_fluido()
        self.root.after(1000 // FPS, self.animar)

    # ---------- Animación de la mascota ----------
    def _amplitud_voz(self):
        voz = getattr(self.olie, "voz", None)
        env = getattr(voz, "envolvente", None) if voz else None
        if env is None:
            return None
        i = int((time.time() - voz.t0_audio) / voz.paso_env)
        return float(env[i]) if 0 <= i < len(env) else 0.0

    # ---------- utilidades del motor fluido ----------
    def _muelle(self, nombre, objetivo, dt, frecuencia=1.6, amortiguacion=0.9):
        """Muelle críticamente amortiguado: se acerca al objetivo con suavidad, sin temblores."""
        v = self.m[nombre]
        w = 2 * math.pi * frecuencia
        aceleracion = w * w * (objetivo - v[0]) - 2 * amortiguacion * w * v[1]
        v[1] += aceleracion * dt
        v[0] += v[1] * dt
        return v[0]

    def _imagen(self, pose, parpadea, mezcla, sx, sy, ang):
        """Devuelve la imagen transformada, reutilizando las ya calculadas."""
        sx, sy = round(sx / 0.004) * 0.004, round(sy / 0.004) * 0.004     # pasos del 0,4 %
        ang = round(ang / 0.25) * 0.25                                    # pasos de 0,25 grados
        anterior, paso = mezcla
        clave = (pose, parpadea, anterior, paso, sx, sy, ang)
        img = self.cache.get(clave)
        if img is None:
            base = self.parpadeos[pose] if parpadea else self.poses_pil[pose]
            if anterior and paso < 8:
                base = Image.blend(self.poses_pil[anterior], base, paso / 8)
            base = base.convert("RGBa")                # alfa premultiplicado: bordes limpios al transformar
            w = max(10, round(self.lado * sx))
            h = max(10, round(self.lado * sy))
            if (w, h) != base.size:
                base = base.resize((w, h), Image.LANCZOS)
            if ang:
                base = base.rotate(ang, resample=Image.BICUBIC, expand=True)
            img = ImageTk.PhotoImage(base.convert("RGBA"))
            if len(self.cache) > 220:
                self.cache.clear()
            self.cache[clave] = img
        return img, round(self.lado * sy)

    def animar_fluido(self):
        ahora = time.perf_counter()
        dt = min(0.05, max(0.001, ahora - self.t_ultimo))
        self.t_ultimo = ahora
        t = ahora - self.t0
        reloj = time.time()
        lz = self.lienzo
        ancho = lz.winfo_width() or 480
        cx, suelo = ancho / 2, 292
        crema = COLORES["crema"]

        est = self.estado
        if est == "espera" and reloj < self.contento_hasta:
            if self.t_contento < t - 2:
                self.t_contento = t
            est = "contento"
        pose = POSE_ESTADO.get(est, "normal")
        if pose != self.pose_actual:
            self.pose_anterior, self.pose_actual = self.pose_actual, pose
            self.t_cambio = t
            self.m["pop"][1] -= 0.55               # pequeño "respiro" elástico al cambiar de pose

        # volumen de la voz y del micro, suavizados (subida rápida, bajada lenta)
        amp = self._amplitud_voz()
        if amp is None:
            amp = 0.0
        k = 1 - math.exp(-dt / (0.06 if amp > self.amp_suave else 0.22))
        self.amp_suave += (amp - self.amp_suave) * k
        grabadora = getattr(self.olie, "grabadora", None)
        mic = min(1.0, (getattr(grabadora, "nivel", 0.0) or 0.0) * 30) if grabadora else 0.0
        self.mic_suave += (mic - self.mic_suave) * (1 - math.exp(-dt / 0.25))

        # objetivos de movimiento (lentos y orgánicos)
        respiro = math.sin(2 * math.pi * t / 4.2)
        flota = 8 * respiro
        estira = 0.012 * math.cos(2 * math.pi * t / 4.2)
        if est == "escuchando":
            obj = dict(dy=-7 + 2 * respiro, ang=4.5, sy=1.03 + estira * 0.5, sx=0.985)
        elif est == "pensando":
            obj = dict(dy=-3 + 3 * math.sin(2 * math.pi * t / 2.8), ang=5 * math.sin(2 * math.pi * t / 3.4),
                       sy=1 + estira, sx=1 - estira * 0.6)
        elif est == "hablando":
            a = self.amp_suave
            obj = dict(dy=-2 + 3 * respiro - 7 * a, ang=2 * math.sin(2 * math.pi * t / 2.6),
                       sy=1 + 0.035 * a, sx=1 - 0.02 * a)
        elif est == "confirmar":
            obj = dict(dy=-3 + 2 * respiro, ang=7 + 1.5 * math.sin(2 * math.pi * t / 2.2), sy=1, sx=1)
        elif est == "error":
            obj = dict(dy=7 + 1.5 * respiro, ang=-3, sy=0.97, sx=1.02)
        elif est == "contento":
            obj = dict(dy=2 * respiro, ang=2 * math.sin(2 * math.pi * t / 1.4), sy=1, sx=1)
        else:   # espera, iniciando
            obj = dict(dy=flota, ang=2 * math.sin(2 * math.pi * t / 7.5), sy=1 + estira, sx=1 - estira * 0.6)

        i_m = INTENSIDAD_MOVIMIENTO
        obj = dict(dy=obj["dy"] * i_m, ang=obj["ang"] * i_m,
                   sx=1 + (obj["sx"] - 1) * i_m, sy=1 + (obj["sy"] - 1) * i_m)
        dy = self._muelle("dy", obj["dy"], dt, 1.4, 0.85)
        ang = self._muelle("ang", obj["ang"], dt, 1.1, 0.9)
        sx = self._muelle("sx", obj["sx"], dt, 2.2, 0.8)
        sy = self._muelle("sy", obj["sy"], dt, 2.2, 0.8)
        pop = self._muelle("pop", 1.0, dt, 2.6, 0.45)

        # saltitos de alegría: dos botes que se apagan, con aplastamiento al caer
        if est == "contento":
            tc = t - self.t_contento
            for inicio, altura in ((0.05, 16), (0.6, 9)):
                f = (tc - inicio) / 0.42
                if 0 <= f <= 1:
                    dy -= altura * math.sin(math.pi * f)
                    if f > 0.85:
                        sy -= 0.04 * (f - 0.85) / 0.15
                        sx += 0.025 * (f - 0.85) / 0.15
                elif 1 < f < 1.35:
                    rebote = math.sin(math.pi * (f - 1) / 0.35)
                    sy -= 0.04 * rebote
                    sx += 0.025 * rebote

        # parpadeo aleatorio
        if reloj > self.proximo_parpadeo:
            self.fin_parpadeo = reloj + 0.12
            self.proximo_parpadeo = reloj + (0.3 if random.random() < 0.2 else random.uniform(2.8, 6.0))
        parpadea = reloj < self.fin_parpadeo and pose in self.parpadeos

        # fundido entre poses (8 pasos con suavizado)
        progreso = min(1.0, (t - self.t_cambio) / 0.28)
        paso = round((progreso * progreso * (3 - 2 * progreso)) * 8)
        mezcla = (self.pose_anterior, paso) if self.pose_anterior in self.poses_pil and paso < 8 else (None, 8)

        foto, alto = self._imagen(pose, parpadea, mezcla, sx * pop, sy * (2 - pop), ang)
        self.foto = foto
        y = round(suelo - 6 - alto / 2 + dy)
        x = round(cx)

        # sombra (más pequeña y suave cuanto más alto flota)
        lz.delete("sombra")
        s = 74 * (1 + dy / 70)
        lz.create_oval(cx - s, suelo - 6, cx + s, suelo + 6, fill="#080b0f", outline="", tags="sombra")
        if self.item_mascota is None or not lz.find_withtag("mascota"):
            self.item_mascota = lz.create_image(x, y, image=foto, tags="mascota")
        else:
            if (x, y) != self.ultima_pos:
                lz.coords(self.item_mascota, x, y)
            lz.itemconfigure(self.item_mascota, image=foto)
        self.ultima_pos = (x, y)
        lz.tag_raise("mascota", "sombra")
        cy = y

        # efectos (todos lentos y continuos)
        lz.delete("fx")
        if est == "escuchando":
            for n in range(3):
                f = (t * 0.45 + n / 3) % 1
                r = 140 + f * 50 + self.mic_suave * 12
                lz.create_oval(cx - r, cy - r, cx + r, cy + r, outline=crema, width=2.4 * (1 - f) + 0.4, tags="fx")
            lz.tag_lower("fx", "mascota")
        elif est == "pensando":
            for n in range(3):
                angulo = t * 1.6 + n * 2.1
                px, py = cx + math.cos(angulo) * 160, cy - 40 + math.sin(angulo) * 34
                r = 7 + 2 * math.sin(angulo)
                item = lz.create_oval(px - r, py - r, px + r, py + r, fill=crema, outline="", tags="fx")
                if math.sin(angulo) < 0:
                    lz.tag_lower(item, "mascota")
        elif est == "hablando":
            for n in range(3):
                f = (t * 0.9 + n / 3) % 1
                r = 25 + f * 50
                grosor = (2.5 * (1 - f) + 0.8) * (0.6 + self.amp_suave * 0.8)
                lz.create_arc(cx + 115 - r, cy - 40 - r, cx + 115 + r, cy - 40 + r, start=-35, extent=70,
                              style="arc", outline=crema, width=grosor, tags="fx")
        elif est == "confirmar":
            bote = 3 * math.sin(2 * math.pi * t / 1.6)
            lz.create_oval(cx + 120, cy - 145 + bote, cx + 170, cy - 95 + bote, fill=crema, outline="", tags="fx")
            lz.create_text(cx + 145, cy - 120 + bote, text="?", fill=COLORES["marron"],
                           font=("Segoe UI Black", 20), tags="fx")
        elif est == "contento":
            brillo = max(0.0, 1 - (t - self.t_contento) / 1.4)
            if brillo > 0:
                for n in range(4):
                    a = math.radians(-60 + n * 30)
                    d1 = 150 + (1 - brillo) * 18
                    lz.create_line(cx + math.cos(a) * d1, cy - 40 + math.sin(a) * d1,
                                   cx + math.cos(a) * (d1 + 16 * brillo), cy - 40 + math.sin(a) * (d1 + 16 * brillo),
                                   fill=crema, width=3, capstyle="round", tags="fx")
        elif est == "error":
            lz.create_oval(cx + 120, cy - 145, cx + 170, cy - 95, fill=COLORES["marron"], outline="", tags="fx")
            lz.create_text(cx + 145, cy - 120, text="!", fill="#ff7a85", font=("Segoe UI Black", 20), tags="fx")

    def cerrar(self):
        def apagar():
            try:
                import sounddevice as sd
                sd.stop()
            except Exception:
                pass
            if DESCARGAR_MODELO_AL_CERRAR or CERRAR_LM_STUDIO_AL_SALIR:
                lms("unload", "--all", espera=20)
            if CERRAR_LM_STUDIO_AL_SALIR:
                cerrar_lm_studio()
            os._exit(0)
        self.root.withdraw()
        threading.Thread(target=apagar, daemon=True).start()
        self.root.after(40000, lambda: os._exit(0))

    def iniciar(self):
        self.root.mainloop()


if __name__ == "__main__":
    olie = Olie()
    ventana = Ventana(olie)
    threading.Thread(target=olie.ejecutar, daemon=True).start()
    ventana.iniciar()
