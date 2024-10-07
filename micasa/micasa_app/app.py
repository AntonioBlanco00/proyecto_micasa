import csv
import time
import sys

from flask import Flask, render_template, request, url_for, jsonify, make_response, redirect
from flask_socketio import SocketIO, emit
import os
import subprocess

#Imports config
from usuarios import config_user1
from usuarios import config_user2
from usuarios import config_user3

import asyncio


# Verifica el argumento de línea de comandos para cargar la config correcta
config_module = sys.argv[1] if len(sys.argv) > 1 else "config"
config = None

if config_module == "config1":
    config = config_user1
    audiof = "audio1"
elif config_module == "config2":
    config = config_user2
    audiof = "audio2"
elif config_module == "config3":
    config = config_user3
    audiof = "audio3"

app = Flask(__name__)
subprocess.run(["python3", "generar_audios.py", config_module])

#app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

current_page_index = 0
emo_data = None

# def obtener_datos_desde_csv(archivo_csv, audiof):
#     datos = {"titulo": "", "pasos": []}
#
#     with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if row['Titulo']:
#                 datos['titulo'] = row['Titulo']
#             paso = {
#                 "paso": int(row['Paso']),
#                 "instruccion": row['Instruccion'],
#                 "imagen": row['Imagen'],
#                 "bwt_imagen": row['Imagen'],
#                 "audio": f"{audiof}/paso{row['Paso']}.mp3"  # Asegúrate de que esta ruta sea correcta
#             }
#             datos['pasos'].append(paso)
#
#     return datos

# def obtener_datos_desde_csv(archivo_csv, audiof):
#     datos = {"titulo": "", "pasos": []}
#
#     with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         filas = list(reader)  # Convertir el reader a una lista para contar las filas
#
#     # Manejo general para otros archivos CSV
#     for row in filas:
#         if row['Titulo']:
#             datos['titulo'] = row['Titulo']
#         paso = {
#             "paso": int(row['Paso']),
#             "instruccion": row['Instruccion'],
#             "imagen": row['Imagen'],
#             "bwt_imagen": row['Imagen'],
#             "audio": f"{audiof}/paso{row['Paso']}.mp3",  # Asegúrate de que esta ruta sea correcta
#             "timeout": int(row['Timeout']) if row['Timeout'] else 60
#         }
#         datos['pasos'].append(paso)
#
#     return datos

def obtener_datos_desde_csv(archivo_csv, audiof):
    datos = {"titulo": "", "pasos": []}

    try:
        with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            filas = list(reader)  # Convertir el reader a una lista para contar las filas

            if not filas:  # Si no hay filas en el CSV (está vacío)
                print(f"El archivo CSV '{archivo_csv}' está vacío.")
                return datos  # Retorna los datos vacíos para evitar errores en el HTML

            # Procesar las filas del CSV
            for row in filas:
                if row['Titulo']:
                    datos['titulo'] = row['Titulo']
                paso = {
                    "paso": int(row['Paso']),
                    "instruccion": row['Instruccion'],
                    "imagen": row['Imagen'],
                    "bwt_imagen": row['Imagen'],
                    "audio": f"{audiof}/paso{row['Paso']}.mp3",  # Asegúrate de que esta ruta sea correcta
                    "timeout": int(row['Timeout']) if row['Timeout'] else 60
                }
                datos['pasos'].append(paso)

    except FileNotFoundError:
        print(f"El archivo CSV '{archivo_csv}' no fue encontrado.")
        return datos  # Retorna datos vacíos si el archivo no existe

    except Exception as e:
        print(f"Ocurrió un error al leer el archivo CSV: {str(e)}")
        return datos  # Manejar cualquier otro error inesperado

    return datos

def obtener_imagenes_mostradas(datos, paso_actual, cantidad=3):
    paso_actual_numero = paso_actual['paso']
    total_pasos = len(datos['pasos'])

    if total_pasos <= cantidad:
        inicio = 0
        fin = total_pasos
    elif paso_actual_numero <= 1:
        inicio = 0
        fin = cantidad
    elif paso_actual_numero >= total_pasos - 1:
        inicio = total_pasos - cantidad
        fin = total_pasos
    else:
        inicio = paso_actual_numero - 1
        fin = paso_actual_numero + 2

    inicio = max(0, inicio)
    fin = min(total_pasos, fin)

    if fin - inicio < cantidad:
        if inicio == 0:
            fin = min(total_pasos, inicio + cantidad)
        elif fin == total_pasos:
            inicio = max(0, fin - cantidad)

    imagenes_mostradas = []

    for i in range(inicio, fin):
        if i < paso_actual_numero:
            ruta_imagen = datos['pasos'][i]['bwt_imagen']
            partes_ruta = ruta_imagen.split('/')
            nombre_archivo = partes_ruta[-1]
            nombre_base, extension = os.path.splitext(nombre_archivo)
            nuevo_nombre_archivo = f"bwt_{nombre_base}{extension}"  # Agregar el prefijo "bwt_" al nombre del archivo
            partes_ruta[-1] = nuevo_nombre_archivo  # Actualizar el nombre del archivo en las partes de la ruta
            imagenes_mostradas.append('/'.join(partes_ruta))  # Reconstruir la ruta de la imagen
        else:
            imagenes_mostradas.append(datos['pasos'][i]['imagen'])

    return imagenes_mostradas

def manejar_logica_condicional(datos, paso_actual, pasos_total):
    imagenes_mostradas = obtener_imagenes_mostradas(datos, paso_actual)
    return {
        'paso_actual': paso_actual,
        'pasos_total': pasos_total,
        'imagenes_mostradas': imagenes_mostradas,
        'indice_paso_actual': paso_actual['paso']
    }

@app.route('/reset_index', methods=['POST'])
def reset_index():
    global current_page_index
    current_page_index = 0
    print(current_page_index, "---------------------------------------------")
    return jsonify({'message': 'Índice reiniciado a 1'})


# @app.route('/new_index', methods=['POST'])
# def new_index():
#     global current_page_index
#     current_page_index = 1
#     global emo_data
#     emo_data = None
#     print(current_page_index, "---------------------------------------------")
#     return jsonify({'message': 'Índice puesto a 0'})

@app.route('/new_index', methods=['POST'])
def new_index():
    global current_page_index
    archivo_csv = config.archivo_csv

    # Obtener el nombre del archivo sin la ruta
    nombre_archivo = os.path.basename(archivo_csv)

    # Comprobar si el nombre del archivo comienza con 'tarea_'
    if nombre_archivo.startswith('tarea_'):
        current_page_index = 3
    else:
        current_page_index = 1

    global emo_data
    emo_data = None
    print(f"current_page_index establecido en {current_page_index} debido a {nombre_archivo}")

    return jsonify({'message': 'Índice ajustado según el archivo CSV'})

@app.route('/emote_index', methods=['POST'])
def emote_index():
    global current_page_index
    current_page_index = 2
    print(current_page_index, "---------------------------------------------")
    return jsonify({'message': 'Índice puesto a 2'})



html_pages = [
    'page1.html',
    'page2.html',
    'page3.html',
    'page4.html'
]

# @app.route('/')
# def index():
#
#     print("CURRENT PAGE ES", current_page_index)
#     current_page = html_pages[current_page_index]
#
#     archivo_csv = config.archivo_csv
#
#     # print('--->',config.archivo_csv)
#     # if config.archivo_csv == 'tareas/empty.csv':
#          # return render_template(html_pages[0])
#
#     paso = request.args.get('paso', default=0, type=int)
#     datos = obtener_datos_desde_csv(archivo_csv, audiof)
#
#     paso_actual = datos['pasos'][paso] if paso < len(datos['pasos']) else datos['pasos'][0]
#     pasos_total = len(datos['pasos'])
#
#     variables_html = manejar_logica_condicional(datos, paso_actual, pasos_total)
#     variables_html['datos'] = datos  # Añadir 'datos' al diccionario de variables
#
#     variables_html['server_url'] = f"http://{request.host}"
#     variables_html['carpeta_aud'] = f"{audiof}"
#
#     return render_template(current_page, paso=paso, **variables_html)

@app.route('/')
def index():
    print("CURRENT PAGE ES", current_page_index)
    current_page = html_pages[current_page_index]

    archivo_csv = config.archivo_csv
    paso = request.args.get('paso', default=0, type=int)
    datos = obtener_datos_desde_csv(archivo_csv, audiof)

    # Verificar si los datos son vacíos (CSV vacío o error en la lectura) para que no pete
    if not datos['pasos']:
        return render_template('page1_back.html', mensaje="No hay pasos disponibles en el archivo CSV.")

    paso_actual = datos['pasos'][paso] if paso < len(datos['pasos']) else datos['pasos'][0]
    pasos_total = len(datos['pasos'])

    variables_html = manejar_logica_condicional(datos, paso_actual, pasos_total)
    variables_html['datos'] = datos  # Añadir 'datos' al diccionario de variables
    variables_html['server_url'] = f"http://{request.host}"
    variables_html['carpeta_aud'] = f"{audiof}"

    return render_template(current_page, paso=paso, **variables_html)


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

# @app.route('/hacer_cama', methods=['GET'])
# def get_cama():
#     nueva_ruta = 'hacer_cama.csv'  # Cambia esto por la nueva ruta que quieras
#     actualizar_config(nueva_ruta)
#     response = make_response('Operación exitosa', 200)
#     return response
#
# @app.route('/hacer_colacao', methods=['GET'])
# async def get_colacao():
#     nueva_ruta = 'hacer_colacao.csv'  # Cambia esto por la nueva ruta que quieras
#     actualizar_config(nueva_ruta)
#     print("CSV CAMBIADO")
#
#     response = make_response('Operación exitosa', 200)
#     return response
#
# @app.route('/poner_lavavajillas', methods=['GET'])
# def get_lavavajillas():
#     nueva_ruta = 'poner_lavavajillas.csv'  # Cambia esto por la nueva ruta que quieras
#
#     # global current_page_index
#     # current_page_index = 1
#
#     actualizar_config(nueva_ruta)
#     response = make_response('Operación exitosa', 200)
#     return response

@app.route('/obtener_info', methods=['POST'])
def obtener_info():
    global emo_data
    emo_data = request.get_json()  # Recibir datos enviados por JavaScript en formato JSON
    print(emo_data)  # Ver los datos recibidos
    respuesta = {"mensaje": "Datos recibidos con éxito", "datos_recibidos": emo_data}
    return jsonify(respuesta)  # Devolver una respuesta JSON


@app.route('/notify', methods=['GET'])
def notify():
    global current_page_index
    current_page_index = 1
    print("INDEX CAMBIADO, ANTES DEL NOUTIFAI")
    socketio.emit('update_content', {'message': 'El contenido ha sido actualizado!'})
    print("despues DEL NOUTIFAI")
    return "Solicitud recibida", 200

@app.route('/get_valoracion', methods=['GET'])
def get_valoracion():
    global emo_data
    return jsonify(emo_data), 200



if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)  # Para poder conectarse remotamente, por ejemplo desde el móvil.
    #socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)

