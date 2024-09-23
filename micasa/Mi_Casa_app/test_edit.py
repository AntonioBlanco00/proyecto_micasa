import re
# FUNCIONA A LA PERFECCIÓN LA FUNCIÓN
def actualizar_config(nueva_ruta):
    archivo_config = 'config.py'

    # Leer el contenido actual del archivo config.py
    with open(archivo_config, 'r') as file:
        lineas = file.readlines()

    # Escribir la nueva ruta en el archivo
    with open(archivo_config, 'w') as file:
        for linea in lineas:
            if linea.startswith('archivo_csv'):
                # Reemplazar la línea con la nueva ruta
                file.write(f'archivo_csv = \'{nueva_ruta}\'\n')
            else:
                # Mantener las demás líneas sin cambios
                file.write(linea)


if __name__ == '__main__':
    nueva_ruta = './Mi_Casa_app/hacer_cama.csv'  # Cambia esto por la nueva ruta que quieras
    actualizar_config(nueva_ruta)
    print(f'La ruta del archivo CSV ha sido actualizada a: {nueva_ruta}')
