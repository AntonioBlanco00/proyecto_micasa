import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Definir la ruta relativa
        relative_path = 'usuarios/config_user1.py'
        # Obtener la ruta absoluta basada en el directorio actual
        absolute_path = os.path.join(os.getcwd(), relative_path)

        if event.src_path == absolute_path:
            print(f"Archivo modificado: {event.src_path}")


if __name__ == "__main__":
    # Definir la ruta relativa
    relative_path = 'usuarios'
    # Obtener la ruta absoluta basada en el directorio actual
    path = os.path.join(os.getcwd(), relative_path)

    event_handler = ChangeHandler()

    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)

    observer.start()
    print(f"Observando cambios en: {os.path.join(os.getcwd(), 'usuarios/config_user1.py')}")

    try:
        while True:
            time.sleep(1)  # Mantiene el script en ejecución
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

