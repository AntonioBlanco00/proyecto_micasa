import csv
from flask import Flask, render_template_string, request, url_for, jsonify
import os
import subprocess
import config
import signal

app = Flask(__name__)
subprocess.run(["python3", "./Mi_Casa_app/generar_audios.py"])


def obtener_datos_desde_csv(archivo_csv):
    datos = {"titulo": "", "pasos": []}

    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Titulo']:
                datos['titulo'] = row['Titulo']
            paso = {
                "paso": int(row['Paso']),
                "instruccion": row['Instruccion'],
                "imagen": row['Imagen'],
                "bwt_imagen": row['Imagen'],
                "audio": f"audio/paso{row['Paso']}.mp3"  # Asegúrate de que esta ruta sea correcta
            }
            datos['pasos'].append(paso)

    return datos

def obtener_imagenes_mostradas(datos, paso_actual, cantidad=5):
    paso_actual_numero = paso_actual['paso']
    total_pasos = len(datos['pasos'])

    if total_pasos <= cantidad:
        inicio = 0
        fin = total_pasos
    elif paso_actual_numero <= 1:
        inicio = 0
        fin = cantidad
    elif paso_actual_numero >= total_pasos - 2:
        inicio = total_pasos - cantidad
        fin = total_pasos
    else:
        inicio = paso_actual_numero - 1
        fin = paso_actual_numero + 4

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

@app.route('/')
def index():
    archivo_csv = config.archivo_csv
    paso = request.args.get('paso', default=0, type=int)
    datos = obtener_datos_desde_csv(archivo_csv)

    paso_actual = datos['pasos'][paso] if paso < len(datos['pasos']) else datos['pasos'][0]
    pasos_total = len(datos['pasos'])

    variables_html = manejar_logica_condicional(datos, paso_actual, pasos_total)
    variables_html['datos'] = datos  # Añadir 'datos' al diccionario de variables

    return render_template_string(html_template, paso=paso, **variables_html)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("AAAAAAAAAAAAAAAAAAAAAAAA")
    shutdown_server()
    return jsonify(message="Server shutting down...")

def shutdown_server():
    # Enviar señal de terminación al proceso principal
    os.kill(os.getpid(), signal.SIGINT)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ datos['titulo'] }}</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            font-size: 1.5vw; /* Tamaño de fuente más pequeño relativo al ancho de la pantalla */
        }
        .audio-container {
            width: 100%;
            display: flex;
            justify-content: center;
            padding: 10px 0;
            position: absolute;
            top: 0;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            width: 90vw; /* 90% del ancho de la pantalla */
            height: 80vh; /* 80% de la altura de la pantalla */
        }
        .images-container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .images-container img {
            max-width: 25vw; /* 25% del ancho de la pantalla */
            max-height: 25vh; /* 25% de la altura de la pantalla */
            margin: 2vw; /* Margen relativo al ancho de la pantalla */
            border: 0.5vw solid black; /* Borde relativo al ancho de la pantalla */
        }
        .btn {
            padding: 1vw; /* Padding relativo al ancho de la pantalla */
            margin: 0.5vw; /* Margen relativo al ancho de la pantalla */
            cursor: pointer;
            font-size: 1.5vw; /* Tamaño de fuente relativo al ancho de la pantalla */
        }
        .anterior {
            background-color: orange;
        }
        .siguiente, .comenzar, .finalizar {
            background-color: green;
            color: white;
        }
        .finalizado {
            font-size: 3vw; /* Tamaño de fuente relativo al ancho de la pantalla */
            margin-top: 2vh; /* Margen superior relativo a la altura de la pantalla */
            display: none;
        }
    </style>
</head>
<body>
    {% if paso_actual is not none %}
        <div class="audio-container">
            <audio controls>
                <source src="{{ url_for('static', filename=paso_actual['audio']) }}" type="audio/mpeg">
                Tu navegador no soporta el elemento de audio.
            </audio>
        </div>
        <div class="container">
            <h2>{{ paso_actual['instruccion'] }}</h2>
            <div class="images-container">
                {% for imagen in imagenes_mostradas %}
                    <img src="{{ url_for('static', filename=imagen) }}" alt="Paso {{ loop.index }}">
                {% endfor %}
            </div>
            <div>   
                {% if paso > 0 %}
                    <button class="btn anterior" onclick="window.location.href='/?paso={{ paso - 1 }}'">Anterior</button>
                {% endif %}
                {% if paso < pasos_total - 1 %}
                    <button class="btn siguiente" onclick="window.location.href='/?paso={{ paso + 1 }}'">Siguiente</button>
                {% elif paso == pasos_total - 1 %}
                    <button class="btn finalizar" id="finalizar-btn">FINALIZAR</button>
                {% endif %}
            </div>
        </div>
        <div id="mensaje-final" class="finalizado">
            ¡Has completado todos los pasos, enhorabuena!
        </div>
    {% else %}
        <div class="finalizado">
            ¡Has completado todos los pasos, enhorabuena!
        </div>
    {% endif %} 

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function(){
            $("#finalizar-btn").click(function(){
                $(".images-container img").each(function(){
                    let src = $(this).attr("src");
                    if (!src.includes("bwt_")) {
                        let partes = src.split('/');
                        let nombre_archivo = partes[partes.length - 1];
                        let nombre_base = "bwt_" + nombre_archivo;
                        partes[partes.length - 1] = nombre_base;
                        $(this).attr("src", partes.join('/'));
                    }
                });
                $("#mensaje-final").show();
                // Enviar solicitud para cerrar el servidor Flask
                $.post("/shutdown", function(data) {
                    console.log(data.message);
                });
            });
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  # Para poder conectarse remotamente, por ejemplo desde el móvil.
