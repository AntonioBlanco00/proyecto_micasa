import os
from PIL import Image, ImageDraw


def convertir_blanco_y_negro(imagen):
    """Convierte una imagen a blanco y negro (escala de grises) y luego a RGB."""
    imagen_gris = imagen.convert('L')
    imagen_rgb = imagen_gris.convert('RGB')
    return imagen_rgb


def aplicar_tacha(imagen):
    """Dibuja una tacha roja en forma de X sobre la imagen."""
    draw = ImageDraw.Draw(imagen)
    width, height = imagen.size
    draw.line([(0, 0), (width, height)], fill="red", width=20)
    draw.line([(width, 0), (0, height)], fill="red", width=20)
    del draw


# Obtener el directorio raíz donde se encuentra el script
directorio_raiz = os.path.dirname(os.path.abspath(__file__))

# Carpeta específica donde se encuentran las imágenes
directorio_imagenes = os.path.join(directorio_raiz, 'static')

# Directorios a excluir
carpetas_excluidas = {'audio1', 'audio2', 'audio3', 'images', 'valoracion'}

# Recorrer todos los directorios dentro del directorio raíz
for directorio_actual, subdirectorios, archivos in os.walk(directorio_raiz):
    # Eliminar las carpetas que no queremos recorrer
    subdirectorios[:] = [d for d in subdirectorios if d not in carpetas_excluidas]

    for archivo in archivos:
        if (archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith(
                '.jpeg')) and not archivo.startswith('bwt_'):
            ruta_imagen = os.path.join(directorio_actual, archivo)
            try:
                # Intentar abrir la imagen
                imagen = Image.open(ruta_imagen)
                # Convertir a blanco y negro
                imagen_bn = convertir_blanco_y_negro(imagen)
                # Aplicar la tacha
                aplicar_tacha(imagen_bn)
                # Guardar la imagen editada
                nombre_imagen_editada = 'bwt_' + archivo
                ruta_imagen_editada = os.path.join(directorio_actual, nombre_imagen_editada)
                imagen_bn.save(ruta_imagen_editada)
                print(f"Imagen procesada y guardada: {nombre_imagen_editada}")
            except FileNotFoundError:
                print(f"Archivo no encontrado: {ruta_imagen}")
            except OSError as e:
                print(f"Error al procesar la imagen {archivo}: {e}")
            except Exception as e:
                print(f"Error inesperado al procesar {archivo}: {e}")
            finally:
                # Cerrar la imagen para liberar memoria
                imagen.close()
