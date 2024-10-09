import os
import signal
import sys
import time
import subprocess

def restart_flask_app(pid, config, port):
    # Matar el proceso del servidor Flask usando el PID proporcionado
    try:
        os.kill(pid, signal.SIGINT)
        print(f"Proceso {pid} del servidor Flask ha sido terminado.")
    except ProcessLookupError:
        print(f"No se pudo encontrar el proceso {pid}. Puede que ya haya sido cerrado.")

    # Esperar un poco para asegurarse de que el proceso se haya cerrado
    time.sleep(1)

    # Volver a ejecutar el comando original
    print(sys.argv)
    command = [sys.executable, 'app.py', config, str(port)] # Mantiene los mismos argumentos
    print(f"Reiniciando Flask app con el comando: {command}")
    subprocess.Popen(command)  # Inicia el nuevo proceso

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Por favor proporciona el PID del proceso Flask.")
        sys.exit(1)

    pid = int(sys.argv[1])
    restart_flask_app(pid, sys.argv[2], int(sys.argv[3]))
