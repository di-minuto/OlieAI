"""Muestra los micrófonos disponibles y mide el volumen del predeterminado durante 5 segundos."""
import numpy as np
import sounddevice as sd

print("Micrófonos disponibles:\n")
for i, d in enumerate(sd.query_devices()):
    if d["max_input_channels"] > 0:
        marca = "  <-- predeterminado" if i == sd.default.device[0] else ""
        print(f"  {i}: {d['name']}{marca}")

print("\nHabla durante 5 segundos para medir el volumen...\n")
def mostrar(indata, frames, t, status):
    nivel = float(np.sqrt(np.mean(indata ** 2)))
    print(f"\r  Volumen: {nivel:.4f}  " + "#" * int(min(nivel * 1000, 60)) + " " * 60, end="")

with sd.InputStream(samplerate=16000, channels=1, dtype="float32", callback=mostrar):
    sd.sleep(5000)
print("\n\nListo.")
