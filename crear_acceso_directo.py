"""Crea un acceso directo 'Olie' en el escritorio que abre la app sin ventana negra
y con su propio icono en la barra de tareas.
Ejecútalo una sola vez:  python crear_acceso_directo.py
"""
import os
import subprocess
import sys

ID_APP = "Olie.AsistenteDeVoz"          # debe coincidir con el de olie_app.py

carpeta = os.path.dirname(os.path.abspath(__file__))
app = os.path.join(carpeta, "olie_app.py")
icono = os.path.join(carpeta, "olie.ico")

pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    pythonw = sys.executable

try:
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as k:
        escritorio = winreg.QueryValueEx(k, "Desktop")[0]
except Exception:
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

acceso = os.path.join(escritorio, "Olie.lnk")
if os.path.exists(acceso):
    os.remove(acceso)


def crear_con_pywin32():
    """Acceso directo con identidad propia (así la barra de tareas no lo agrupa con Python)."""
    import pythoncom
    from win32com.shell import shell
    from win32com.propsys import propsys, pscon

    enlace = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None,
                                        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    enlace.SetPath(pythonw)
    enlace.SetArguments(f'"{app}"')
    enlace.SetWorkingDirectory(carpeta)
    enlace.SetIconLocation(icono, 0)
    enlace.SetDescription("Olie, asistente de voz")
    propiedades = enlace.QueryInterface(propsys.IID_IPropertyStore)
    propiedades.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType(ID_APP))
    propiedades.Commit()
    enlace.QueryInterface(pythoncom.IID_IPersistFile).Save(acceso, 0)


def crear_con_powershell():
    comando = (
        f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{acceso}');"
        f"$s.TargetPath = '{pythonw}';"
        f"$s.Arguments = '\"{app}\"';"
        f"$s.WorkingDirectory = '{carpeta}';"
        f"$s.IconLocation = '{icono}';"
        f"$s.Description = 'Olie, asistente de voz';"
        f"$s.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", comando], check=True, capture_output=True)


try:
    crear_con_pywin32()
    print(f"Acceso directo creado en: {acceso}")
except Exception as e:
    print(f"(Sin pywin32: {e}. Lo creo de la forma básica; el icono de la barra puede salir agrupado con Python.)")
    try:
        crear_con_powershell()
        print(f"Acceso directo creado en: {acceso}")
    except Exception as e2:
        print(f"No se pudo crear el acceso directo: {e2}")
        sys.exit(1)

print("Ahora haz clic derecho sobre él y elige 'Anclar a la barra de tareas'.")
