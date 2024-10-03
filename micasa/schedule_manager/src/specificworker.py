#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2024 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *

import requests
from requests.exceptions import RequestException
import time
from datetime import datetime, timedelta
import csv


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 1500

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        #self.agent_id = 752
        #self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            # signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            # signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            # signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            # signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            # signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            # signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        #self.csv_path = '../Mi_Casa_app/usuarios/rutina_diaria_user1.csv'
        # Print csv_path
        #print(f"CSV Path: {self.csv_path}")
        # TODO: Cargar csv. con agenda en un diccionario.
        # TODO: Leer csv. desde csv_path  y almacenar en un diccionario.
        #self.lista_tareas = self.csv_a_lista_tareas(self.csv_path)


        # Inicializar variables
        self.task_on_course = None

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        self.flag = False

        self.satisfaccion_map = {
            'triste': 1,
            'descontento': 2,
            'neutral': 3,
            'contento': 4,
            'muy-contento': 5
        }


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # # TODO: Leer url_base, usuario, ruta_cs
        print("Params read. Starting...", params)
        self.ip = params["ip"]
        self.port = params["port"]
        self.user = params["user"]
        self.csv_path = params["csv_path"]

        self.agent_id = params["agent_id"]
        self.g = DSRGraph(0, "pythonAgent", int(self.agent_id))

        self.task_list = self.csv_to_list(self.csv_path)

        print("Task List:")
        for task in self.task_list:
            print(task)

        self.update_hour = params["update_hour"]
        self.update_hour = datetime.strptime(self.update_hour, "%H:%M:%S").time()

        self.base_url = 'http://' + self.ip + ':' + self.port + '/'

        user_to_reloj = {
            1: "b3ca",
            2: "81b6",
            3: "fc66"
            }

        self.reloj = user_to_reloj.get(int(self.user), "Desconocido")

        print("------------- RELOJ ASIGNADO -------------")
        print("El reloj asignado al usuario " + str(self.user) + " es: " + self.reloj)
        print("------------- RELOJ ASIGNADO -------------")

        # self.actualizar_config('empty.csv') #To load black screen

        return True

    @QtCore.Slot()
    def compute(self):
        print("-------------------------------- COMPUTE ---------------------------------------------")
        # ------------------------------ GET USER DATA ------------------------------------------
        self.current_room = self.get_room()
        #HARDCODEADO PARA TESTING
        # self.current_room = "house"
        print('Current_room:', self.current_room)

        # ------------------------------ GET TIME DATA ------------------------------------------
        self.actual_time = time.strftime("%H:%M:%S")
        self.actual_day = time.strftime("%A")
        print(f"Día actual: {self.actual_day}", f"Hora actual: {self.actual_time}")
        # ------------------------------ UPDATE TASKS ------------------------------------------
        # Aquí hay que añadir también que se generen las imágenes si se plantea que ellos añadan más.
        # self.update_tasks(self.update_hour)

        # Filter task_list from csv by execution hour window
        filtered_tasks = self.task_filtered_time(self.task_list, self.actual_time, self.actual_day)

        # Print filtered tasks 'Completada' == 'Si' or 'Timeout'
        print("------TAREAS FILTRADAS--------")
        for task in filtered_tasks:
            if task['Completada'] == 'Si' or task['Completada'] == 'Timeout':
                print(f"Tarea {task['Rutina']} marcada como {task['Completada']}")
            else:
                print(f"Tarea {task['Rutina']} aún no completada, ubicación {task['Habitación']}")

        print("------TAREA EN CURSO--------")

        if self.task_on_course != None:
            print(f"Tarea {self.task_on_course['ID']} {self.task_on_course['Rutina']} ")
        # ------------------------------ Asignar Nueva Tarea ------------------------------
        # If not task_on_course equal to empty string

        if self.task_on_course is None:
            location_filtered_tasks = self.task_filtered_location(filtered_tasks, self.current_room)
            if len(location_filtered_tasks) > 0:
                # For task in filtered_tasks, if Completada == No task_on_course = task
                # TODO: Filtrar tarea en curso por orden de prioridad, en caso de ser necesario
                # TODO: Añadir filtro de ubicación
                print("Tareas filtradas por dia/hora:", len(filtered_tasks))
                for task in location_filtered_tasks:
                    if task['Completada'] == 'No':
                        self.task_on_course = task
                        print(f"Ejecutar tarea: {task['Rutina']}")
                        self.task_on_course['Hora Inicio Tarea'] = self.actual_time
                        self.actualizar_config(self.task_on_course['Juego'])
                        time.sleep(5) # In order to refresh flask server.
                        self.lanzar_app()
                        break
            else:
                print('No existe tarea disponible')
                # self.actualizar_config('empty.csv')
        # ------------------------------ Completar Tarea ------------------------------
        else:
            # ------------------------------- ACTUALIZAR EJECUCIÓN DE TAREA ------------------------------
            # TODO: Actualizar task con la ejecución de la tarea en el servidor. Si Completada == Si,
            #  se actualiza el csv con la info de la tarea (hay que guardar la hora de fin de la tarea)

            self.get_server_data()

            #   Check if task 'Completada' == No
            if self.task_on_course['Completada'] == 'No':
                # time_init_task = datetime.strptime(self.task_on_course['Hora Inicio Tarea'], "%H:%M:%S").time()
                # actual_time = datetime.now().time()
                #
                # # Sum Timeout to init time and get time_limit
                # timeout_seconds = int(self.task_on_course['Timeout'])  # Cast
                # timeout_delta = timedelta(seconds=timeout_seconds)
                # time_limit = (datetime.combine(datetime.today(), time_init_task) + timedelta(
                #     seconds=timeout_seconds)).time()
                pass
                # ------------------------------- TIMEOUT ------------------------------
                # if actual_time > time_limit:
                #     # Marcar la tarea como Timeout, completar todos los campos
                #     self.task_on_course['Completada'] = 'Timeout'
                #     self.task_on_course['Hora Fin Tarea'] = actual_time.strftime("%H:%M:%S")
                #     self.task_on_course['Satisfaccion'] = '1'
                #     #   Update task in csv
                #     self.save_updated_task(self.task_on_course)
                #     # Update task_list
                #     self.task_list = self.update_task_list(self.task_list, self.task_on_course)
                #     # Reset task on course
                #     self.task_on_course = None
                # else: #   Wait for Timeout or Confirmation
                #     counter = datetime.combine(datetime.today(), time_limit) - datetime.combine(datetime.today(),
                #                                                                                 actual_time)
                #     print(f"Tiempo restante para Timeout: {counter}")
                #     pass
                # ------------------------------- TASK COMPLETED ------------------------------
            elif self.task_on_course['Completada'] == 'Si' or self.task_on_course['Completada'] == 'Timeout':
                # Update task_list
                self.task_list = self.update_task_list(self.task_list, self.task_on_course)
                #  Update task in csv
                self.save_updated_task(self.task_on_course)
                # Reset task on course
                self.task_on_course = None


        # TODO: Obtener posición de la persona

        # TODO: comprobar si hay tarea en curso,
        #     TODO: Si hay tarea en curso, ver diferencia de tiempo entre actual e inicio de tarea.
        #       TODO: Si t>timeout. Finalizar Tarea y marcar timeout. Liberar tarea.
        #         TODO: Si existe confirmación de la tarea, almacenar info y Liberar tarea.
        #           TODO: Si t<Timeout, esperar (continue).
        # TODO: Filtrar tareas del DIC por ubicación y hora.


        # TODO: Filtrar tarea (notificación o juego)
        # TODO: Ejecutar. Almacenar T_inicio

        # TODO: Crear funciones para: almacenar resultado de ejecución y escribir csv.

        # for persona in self.lista_personas.objects:
        #     id_persona = persona.id + 300
        #     # if self.habitacion[persona.id] != self.get_room(id_persona):
        #     #     self.habitacion[persona.id] = self.get_room(id_persona)
        #     #     print(f"-------------- PERSONA {id_persona} ----------------")
        #     #     print(self.habitacion[persona.id])
        #     # else:
        #     #     pass
        #
        #     self.habitacion[persona.id] = self.get_room(id_persona)
        #
        #
        #
        #
        #
        #     if self.habitacion[persona.id] == "kitchen" and self.flag == False:
        #         self.flag = True
        #         print(f"{id_persona} está en la cocina")
        #         self.get_colacao()
        #         print("LANZAR NOTIFY")
        #         response = requests.get(f'{self.base_url}/notify')
        #         print(response.text)

    def get_server_data(self):
        # Realizar la solicitud GET
        response = requests.get(self.base_url + 'get_valoracion')
        # Verificar la respuesta del servidor
        if response.status_code == 200:
            data = response.json()
            # print(f"Datos recibidos: {data}")
            if data is not None:
                if data['timeout'] == 'Timeout':
                    print("La tarea ha sido completada")
                    print("Timeout en la valoración, se deja a 0")
                    self.task_on_course['Completada'] = 'Si'
                    t_fin = datetime.now() - timedelta(seconds=60)
                    self.task_on_course['Hora Fin Tarea'] = t_fin.strftime("%H:%M:%S")
                    self.task_on_course['Satisfaccion'] = '-1'
                elif data['timeout'] == 'Timeout tarea':
                    self.task_on_course['Hora Fin Tarea'] = datetime.now().strftime("%H:%M:%S")
                    self.task_on_course['Satisfaccion'] = '-1'
                    self.task_on_course['Completada'] = 'Timeout'
                    print("La tarea no ha sido completada")
                else:
                    print("La tarea ha sido completada")
                    self.task_on_course['Completada'] = 'Si'
                    self.task_on_course['Hora Fin Tarea'] = datetime.now().strftime("%H:%M:%S")
                    self.task_on_course['Satisfaccion'] = str(self.satisfaccion_map.get(data['satisfaccion'], 0))
                    print("Valoración recibida: " + data['satisfaccion'])
                    print("Valor en la escala: " + str(self.satisfaccion_map.get(data['satisfaccion'], 0)))

        else:
            print(f"Error: {response.status_code}")

    def startup_check(self):
        print(f"Testing RoboCompVisualElements.TRoi from ifaces.RoboCompVisualElements")
        test = ifaces.RoboCompVisualElements.TRoi()
        print(f"Testing RoboCompVisualElements.TObject from ifaces.RoboCompVisualElements")
        test = ifaces.RoboCompVisualElements.TObject()
        print(f"Testing RoboCompVisualElements.TObjects from ifaces.RoboCompVisualElements")
        test = ifaces.RoboCompVisualElements.TObjects()
        QTimer.singleShot(200, QApplication.instance().quit)


    def csv_to_list(self, ruta_csv):
        task_list = []
        try:
            # Abre el archivo CSV
            with open(ruta_csv, mode='r', encoding='utf-8') as file:
                lector_csv = csv.DictReader(file, delimiter=';')
                # Convierte cada fila en un diccionario
                for fila in lector_csv:
                    task_list.append(dict(fila))
                file.close()

        except Exception as e:
            print(f"Error al leer el archivo CSV: {e}")

        return task_list

    def task_filtered_time(self, task_list, actual_time, actual_day):
        tasks_filtered = []
        # Filter task_list by day
        print(len(task_list))
        print(actual_day)
        for task in task_list:
            if task['DAY'] == actual_day:
                if task['Hora Inicio'] <= self.actual_time <= task['Hora Fin']:
                    tasks_filtered.append(task)



        return tasks_filtered

    def task_filtered_location(self, task_list, location):
        tasks_filtered = []
        for task in task_list:
            if task['Habitación'] == location or task['Habitación'] == 'house':
                tasks_filtered.append(task)
        return tasks_filtered

    def get_room(self):
        node = self.g.get_node(self.reloj)
        room = self.g.get_name_from_id(node.attrs["parent"].value)
        return room

    def generate_and_play_audio(self, audio_path, message):
        """
        Genera y reproduce un archivo de audio.

        :param audio_path: Ruta del archivo de audio
        :param message: Mensaje de bienvenida
        """
        tts = gTTS(text=message, lang='es')
        tts.save(audio_path)
        audio = AudioSegment.from_file(audio_path)
        play(audio)

    ###########################################################################################
    # GETS
    # def get_cama(self):
    #     response = requests.get(f'{self.base_url}/hacer_cama')
    #     if response.status_code == 200:
    #         print("Respuesta de /hacer_cama:", response.text)
    #     else:
    #         print("Error al acceder a /hacer_cama:", response.status_code)
    #
    # def get_colacao(self):
    #     response = requests.get(f'{self.base_url}/hacer_colacao')
    #     if response.status_code == 200:
    #         print("Respuesta de /hacer_colacao", response.text)
    #     else:
    #         print("Error al acceder a /hacer_colacao:", response.status_code)
    #
    # def get_lavavajillas(self):
    #     response = requests.get(f'{self.base_url}/poner_lavavajillas')
    #     if response.status_code == 200:
    #         print("Respuesta de poner_lavavajillas:", response.text)
    #     else:
    #         print("Error al acceder a poner_lavavajillas:", response.status_code)

    ###########################################################################################
    # A la función le pasas el nombre del csv de la secuencia/tarea, incluyendo el .csv
    def actualizar_config(self, nueva_ruta):
        archivo_config = '../Mi_Casa_app/usuarios/config_user' + self.user + '.py'
        print("ESCRIBIENDO EN: " + archivo_config)
        # Ejemplo: nueva_ruta = './Mi_Casa_app/hacer_cama.csv'
        nueva_ruta = 'tareas/' + nueva_ruta
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

    # Function to save the updated task to the CSV file
    def save_updated_task(self, task):
        # Get current week
        week = datetime.now().isocalendar()[1]
        # create csv_result_path to save the file (_result_week)
        self.csv_result_path = self.csv_path.replace('.csv', f'_result_{week}.csv')

        try:
            # Check if exists a file with the same name + _result_week
            if os.path.exists(self.csv_result_path):
                pass
            else:
                # Create a new file with the same name + _result_week
                with open(self.csv_result_path, mode='w', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=task.keys(), delimiter=';')
                    writer.writeheader()
                    writer.writerows(self.task_list)
                    file.close()
        except Exception as e:
            print(f"Error Creating the CSV_result file: {e}")
            return False

        # Read the current tasks from the CSV file
        tasks = self.csv_to_list(self.csv_result_path)

        # Find the task to update
        for i, t in enumerate(tasks):
            if t['ID'] == task['ID']:
                # Print the task to update
                print(f"Updating task: {task['Rutina']}")
                tasks[i] = task
                break
        try:
            with open(self.csv_result_path, mode='w', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=tasks[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(tasks)
                file.close()
        except Exception as e:
            print(f"Error writing to the CSV file: {e}")
            return False

        return True

    # Function to update task_list with the task_on_course
    def update_task_list(self, task_list, task_on_course):
        for task in task_list:
            if task['ID'] == task_on_course['ID']:
                task.update(task_on_course)
                break
        return task_list

    def lanzar_app(self):
        url = self.base_url + 'notify'
        max_retries = 10
        delay = 1.5
        attempt = 0

        while attempt < max_retries:
            try:
                response = requests.get(url)

                if response.status_code == 200:
                    print("Solicitud realizada correctamente en el intento", attempt + 1)
                    print("Respuesta del servidor:", response.text)
                    return response  # Salir si la solicitud fue exitosa
                else:
                    # Si el código no es 200, manejar el error
                    print(f"Error en la solicitud. Código de estado: {response.status_code}")

            except RequestException as e:
                # Captura de errores en la solicitud (conexión fallida, tiempo de espera, etc.)
                print(f"Error al realizar la solicitud en el intento {attempt + 1}: {e}")

            # Incrementar el número de intentos
            attempt += 1

            if attempt < max_retries:
                # Esperar 1.5 segundos antes de volver a intentarlo
                print(f"Reintentando en {delay} segundos...")
                time.sleep(delay)
            else:
                print("Número máximo de reintentos alcanzado. La solicitud ha fallado.")

    ######################
    # From the RoboCompVisualElements you can call this methods:
    # self.visualelements_proxy.getVisualObjects(...)
    # self.visualelements_proxy.setVisualObjects(...)

    ######################
    # From the RoboCompVisualElements you can use this types:
    # RoboCompVisualElements.TRoi
    # RoboCompVisualElements.TObject
    # RoboCompVisualElements.TObjects

    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

    def update_node(self, id: int, type: str):
        console.print(f"UPDATE NODE: {id} {type}", style='green')

    def delete_node(self, id: int):
        console.print(f"DELETE NODE:: {id} ", style='green')

    def update_edge(self, fr: int, to: int, type: str):

        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')
