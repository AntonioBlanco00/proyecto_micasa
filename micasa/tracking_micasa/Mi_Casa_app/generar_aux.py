import os
from PIL import Image, ImageDraw

def convertir_blanco_y_negro(imagen):
    # Convertir la imagen a escala de grises
    imagen_gris = imagen.convert('L')
    # Convertir la imagen de nuevo a RGB para permitir la superposición de color
    imagen_rgb = imagen_gris.convert('RGB')
    return imagen_rgb

def aplicar_tacha(imagen):
    draw = ImageDraw.Draw(imagen)
    width, height = imagen.size
    draw.line([(0, 0), (width, height)], fill="red", width=20)
    draw.line([(width, 0), (0, height)], fill="red", width=20)
    del draw

# Directorio raíz donde se encuentran los subdirectorios con imágenes
directorio_raiz = '/home/robolab/Desktop/Mi_Casa/static'

# Recorrer todos los directorios dentro del directorio raíz
for directorio_actual, subdirectorios, archivos in os.walk(directorio_raiz):
    for archivo in archivos:
        if (archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg')) and not archivo.startswith('bwt_'):
            ruta_imagen = os.path.join(directorio_actual, archivo)
            imagen = Image.open(ruta_imagen)
            imagen_bn = convertir_blanco_y_negro(imagen)
            aplicar_tacha(imagen_bn)
            nombre_imagen_editada = 'bwt_' + archivo
            ruta_imagen_editada = os.path.join(directorio_actual, nombre_imagen_editada)
            imagen_bn.save(ruta_imagen_editada)

