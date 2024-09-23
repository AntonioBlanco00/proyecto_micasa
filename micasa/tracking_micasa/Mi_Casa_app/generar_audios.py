import os
from gtts import gTTS
import csv
import config

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

def generar_audio_para_pasos(datos):
    audio_folder = '../Enrique_TTS/Mi_Casa_app/static/audio'

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

if __name__ == '__main__':
    archivo_csv = config.archivo_csv
    datos = obtener_datos_desde_csv(archivo_csv)
    generar_audio_para_pasos(datos)
    print("Audios generados correctamente")

