import re
import os

def actualizar_config(nueva_ruta):
    try:
        # Ruta base del directorio de tareas
        directorio_tareas = os.path.join('..', 'micasa_app', 'tareas')

        # Nueva ruta completa del archivo CSV
        ruta_csv = os.path.join(directorio_tareas, nueva_ruta)

        # Comprobar si el archivo CSV existe
        if not os.path.exists(ruta_csv):
            # Si no existe, usar un archivo CSV predeterminado
            print(f"El archivo {nueva_ruta} no existe, cargando archivo predeterminado.")
            ruta_csv = os.path.join(directorio_tareas, 'tarea_test.csv')

        # Ruta del archivo de configuración
        archivo_config = os.path.join('..', 'micasa_app', 'usuarios', 'config_user1.py')
        print("ESCRIBIENDO EN: " + archivo_config)

        # Leer el contenido actual del archivo config_user.py
        with open(archivo_config, 'r') as file:
            lineas = file.readlines()

        # Escribir la nueva ruta en el archivo de configuración
        with open(archivo_config, 'w') as file:
            for linea in lineas:
                if linea.startswith('archivo_csv'):
                    # Reemplazar la línea con la nueva ruta (ya sea la proporcionada o la predeterminada)
                    file.write(f"archivo_csv = '{ruta_csv}'\n")
                else:
                    # Mantener las demás líneas sin cambios
                    file.write(linea)

        print("Archivo actualizado correctamente.")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_config}.")
    except Exception as e:
        print(f"Ocurrió un error al actualizar el archivo: {e}")


if __name__ == '__main__':
    nueva_ruta = 'hacer_colacao.csv'  # Cambia esto por la nueva ruta que quieras
    actualizar_config(nueva_ruta)
    print(f'La ruta del archivo CSV ha sido actualizada a: {nueva_ruta}')
