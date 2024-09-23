import os
from gtts import gTTS
import csv
import sys

#Imports config
from usuarios import config_user1
from usuarios import config_user2
from usuarios import config_user3

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
                "bwt_imagen": row['Imagen']  # La nueva columna bwt_imagen tiene el mismo valor que la columna imagen
            }
            datos['pasos'].append(paso)

    return datos

def generar_audio_para_pasos(datos, config_module):
    if config_module == "config1":
        audio_folder = './static/audio1'
    elif config_module == "config2":
        audio_folder = './static/audio2'
    elif config_module == "config3":
        audio_folder = './static/audio3'
    else:
        audio_folder = './static/audio1'

    # Elimina los archivos de audio existentes
    if os.path.exists(audio_folder):
        for file in os.listdir(audio_folder):
            file_path = os.path.join(audio_folder, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    else:
        os.makedirs(audio_folder)

    # Genera nuevos audios
    for paso in datos['pasos']:
        texto = paso['instruccion']
        audio_path = os.path.join(audio_folder, f"paso{paso['paso']}.mp3")

        # Generar y guardar el audio, sobrescribiendo si existe
        tts = gTTS(text=texto, lang='es')
        tts.save(audio_path)

        paso['audio'] = os.path.join('audio', f"paso{paso['paso']}.mp3")

    # Generar audios de aviso, fin sin terminar y fin. Aqui con otro switch puedo personalizar audios para cada usuario.
    texto_aviso = "¿Sigues ahí?"
    texto_despedida = "No se terminó la tarea. No hay problema, puedes continuarla cuando desees. Si necesitas ayuda, aquí estoy para asistirte."
    texto_final = "¡Enhorabuena! Has terminado tu tarea"

    tts = gTTS(text=texto_aviso, lang='es')
    tts.save(audio_folder + "/aviso.mp3")

    tts = gTTS(text=texto_despedida, lang='es')
    tts.save(audio_folder + "/despedida.mp3")

    tts = gTTS(text=texto_final, lang='es')
    tts.save(audio_folder + "/final.mp3")

if __name__ == '__main__':
    config_module = sys.argv[1] if len(sys.argv) > 1 else "config"
    config = None

    if config_module == "config1":
        config = config_user1
    elif config_module == "config2":
        config = config_user2
    elif config_module == "config3":
        config = config_user3

    archivo_csv = config.archivo_csv
    datos = obtener_datos_desde_csv(archivo_csv)
    generar_audio_para_pasos(datos, config_module)
    print("Audios generados correctamente")

