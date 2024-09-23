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
import datetime

from PySide2.QtCore import QTimer
from PySide2.QtGui import QPolygonF, QPainter, QPen, QColor, QFont, QImage
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import socketio
import json
import random
import math
from PySide2.QtCore import QRect, QPointF, QPoint, QSize, Qt
import numpy as np
import cv2
import psycopg2
from collections import defaultdict, deque
import threading
import signal
import sys
import requests
import matplotlib.pyplot as plt
import copy
import time

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    # key_pressed_signal = pyqtSignal(str)
    # Crear una instancia del cliente Socket.IO
    def __init__(self, proxy_map, startup_check=False,max_length=5):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 500

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 23
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)
        self.rt_api = rt_api(self.g)

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

        if startup_check:
            self.startup_check()
        else:
            # # Configuración del cliente Socket.IO
            self.sio = socketio.Client()
            self.zone_id = '1'  # Zone ID
            self.algorithm = '80'  # Algorithm (TWR:80; TDOA:81)
            self.server_url = 'http://192.168.1.23:3000?token=3b7a0215a4b1c18578e6ad52fabdd21d'
            # self.people_parents_in_graph = {}

            api_url = "http://192.168.1.23/api/zone/query.html?access_token=3b7a0215a4b1c18578e6ad52fabdd21d&username=admin&password=admin&_=1705662394612"

            # Realizar la solicitud GET
            response = requests.get(api_url)
            self.heartrate_time=datetime.datetime.now()
            self.api_rest_tags= 'http://192.168.1.23/api/tag/getexisttag.html?access_token=3b7a0215a4b1c18578e6ad52fabdd21d'
            # Verificar el código de estado de la respuesta
            if response.status_code == 200:
                # Procesar la respuesta JSON
                data = response.json()
                print("Respuesta:", data)
                # self.server_url = 'http://192.168.1.23:3000?token=' + token_id
            # self.key_pressed_signal.connect(self.on_key_pressed)
            try:
                self.callbacks()
                self.sio.connect(self.server_url)
                print('correctful')
            except socketio.exceptions.ConnectionError as e:
                print('Error de conexión:', e)

            self.sections = {
            #     "bathroom": QRect(QPoint(7210, 4120), QSize(2140, 1990)),
            #     "kitchen": QRect(QPoint(11850, 6800), QSize(3500, 2000)),
                "robolab2": QRect(QPoint(6130, 0), QSize(5950, 9700)),
            #     # "corridor": QPolygonF(),
                "robolab1": QRect(QPoint(0, 0), QSize(6100, 9700)),
                "kitchen": QRect(QPoint(12100, 0), QSize(2900, 6800))
             }

            # Maybe can be change for a vector and using the index
            self.sections = {
                # "0" : "bathroom",
                # "5" : "kitchen",
                "5" : "kitchen",
                # "11" : "corridor",
                # "8" : "corridor",
                "2" : "robolab1",
                "3" : "robolab2"
            }

            # self.sio = None  # Debes inicializar SocketIO donde corresponda
            self.track_data = defaultdict(lambda: {'x': deque(maxlen=max_length), 'y': deque(maxlen=max_length), 'in_fence': None})
            # print (self.track_data, '-----')

            # Open schematic.jpeg and create a window to draw it scaled by 0.5
            self.img = cv2.imread('/home/robolab-micasa/robocomp/components/micasa_agent/PruebaRobolab_MiCasa')
            if self.img is None or self.img.size == 0:
                raise ValueError("La imagen no se ha cargado correctamente")

            self.img = cv2.resize(self.img, (0, 0), fx=0.5, fy=0.5)
            self.img = cv2.resize(self.img, (0, 0), fx=0.5, fy=0.5)
            self.person_read = cv2.imread('/home/robolab-micasa/Descargas/d.png', cv2.IMREAD_UNCHANGED)
            self.alpha = self.person_read[:,:,3]
            self.alpha = np.divide(self.alpha,255.0).astype('uint8')
            self.alpha = cv2.resize(self.alpha, (30, 30), fx=0.5, fy=0.5)
            self.alpha_inv = 1 - self.alpha
            self.person = self.person_read[:,:,0:3]

            self.person = cv2.resize(self.person, (30, 30), fx=0.5, fy=0.5)

            cv2.namedWindow('PruebaMicasa.png', cv2.WINDOW_NORMAL)
            cv2.imshow('PruebaMicasa.png', self.img)
            self.img_clean = self.img.copy()

            self.radius = 100

            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        pass

    def setParams(self, params):
        try:
            self.params_tags = str(params["tags_sn"])
            self.params_tags_names = str(params["tags_names"])
            self.serial_numbers = self.params_tags.split(',')
            name_list = self.params_tags_names.split(',')
            self.tag_names = {serial: name for serial, name in zip(self.serial_numbers, name_list)}
            print("----------TAG NAMES------------")
            print(self.serial_numbers)
        except:
            print("Error reading config params")

        return True

    @QtCore.Slot()
    def compute(self):
         # Obtener la forma de self.img
        # print('compute')
        # print(self.sio, 'perrrooooo funcionaaaa')
        now_hrate = datetime.datetime.now()
        if (now_hrate - self.heartrate_time).total_seconds() >= 10:
            self.insert_heartrate()
            self.heartrate_time = now_hrate
        height, width, channels = self.img.shape
        # Dibujar las personas en la imagen
        self.img = self.img_clean.copy()
        for person in self.g.get_nodes_by_type("person"):
            # print(person)
        #     print ('-------------------------')
            rt_edge = self.rt_api.get_edge_RT(self.g.get_node(person.attrs["parent"].value), person.id)
            tx, ty, _ = rt_edge.attrs['rt_translation'].value
            x, y = self.convertir_a_pixeles(tx, ty, 9350, 8370, width, height)

            # Asegurarse de que las coordenadas están dentro de los límites de la imagen
            if y + self.person.shape[0] > height or x + self.person.shape[1] > width:
                continue

            window = self.img[y:y+self.person.shape[0], x:x+self.person.shape[1]]

            if window.shape[:2] != self.person.shape[:2]:
                window = cv2.resize(window, (self.person.shape[1], self.person.shape[0]))

            for c in range(0, 3):
                window[:, :, c] = window[:, :, c] * self.alpha_inv + self.person[:, :, c] * self.alpha

            cv2.putText(self.img, person.name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Limpiar self.img
        cv2.imshow('PruebaMicasa.png', self.img)
        cv2.waitKey(1)
        # print(self.track_data.keys(), '--------------------')
        for tag in self.track_data.keys():
            if len(self.track_data[tag]['x']) == 5 and len(self.track_data[tag]['y']) == 5:
                # print(tag, '-----------------MIAUMIAU-------------------------')
                avg_x = sum(self.track_data[tag]['x']) / len(self.track_data[tag]['x'])
                avg_y = sum(self.track_data[tag]['y']) / len(self.track_data[tag]['y'])

                print(f'Average x for {tag}: {avg_x}')
                print(f'Average y for {tag}: {avg_y}')

                # Llamada al método de inserción de la base de datos
                self.insert_db(tag, avg_x, avg_y)
                self.track_data[tag]['x'].clear()
                self.track_data[tag]['y'].clear()




        # all_tags = requests.get(self.api_rest_tags)
        # print('---------------------------',all_tags.json())
         #bateria, heartrate, activo o no activo, si carga o no, steps


        # # print("PEOPLE", self.people)
        # # Get self.img shape
        # height, width, channels = self.img.shape
        # # Draw the people in the image
        # self.img = self.img_clean.copy()
        # for person in self.g.get_nodes_by_type("person"):
        #     rt_edge = self.rt_api.get_edge_RT(self.g.get_node(person.attrs["parent"].value), person.id)
        #     tx, ty, _ = rt_edge.attrs['rt_translation'].value
        #     x, y = self.convertir_a_pixeles(tx, ty, 9350, 8370, width, height)
        #     window = self.img[y:y+self.person.shape[0], x:x+self.person.shape[1]]
        #     for c in range(0,3):
        #         window[:,:,c] = window[:,:,c]*self.alpha_inv+self.person[:,:,c]*self.alpha
        #     # cv2.circle(self.img, (x, y), 15, (255, 0, 255), -1)
        #     # cv2.circle(self.img, (x, y), 15, (0, 0, 0), 10)
        #     cv2.putText(self.img, person.name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        #
        # # Clean self.img
        # cv2.imshow('PruebaMicasa.png', self.img)
        # cv2.waitKey(1)
    def startup_check(self):
        print(f"Testing RoboCompVisualElementsPub.TObject from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TObject()
        print(f"Testing RoboCompVisualElementsPub.TData from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TData()
        QTimer.singleShot(200, QApplication.instance().quit)

    def insert_heartrate(self):

        self.api_rest_tags= 'http://192.168.1.23/api/tag/getexisttag.html?access_token=3b7a0215a4b1c18578e6ad52fabdd21d'
        response_api = requests.get(self.api_rest_tags)
        # print(response_api.text, 'perroroorororoorororo-------------------------------------------------------------')
        # heartrate_data = json.loads(response_api.json())
        # print(response_api.json()['data'].keys(), 'perroroorororoorororo-------------------------------------------------------------')
        if response_api.status_code == 200:

            json = response_api.json()['data']
            # print(json, '---------------------------fkfladlagfsdgaflkudgasfoldkusg----------------------')
            for tag in self.tag_names.keys():
                if tag in response_api.json()['data'].keys():
                    # print(tag, json[tag]['heartrate'], '----------hoooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo-------------------------------------')
                    # print(tag, json[tag]['act'], '----------hoooooooooooooooslllllllllllllllllllllllllllllllñllllllllllllllllllllllllllllllllo-------------------------------------')
                    tag_heartrate=json[tag]['heartrate']
                    tag_act=json[tag]['act']
                    if tag_heartrate is not None:
                        try:
                            conn = psycopg2.connect(
                                dbname="postgres",
                                user="postgres",
                                password="opticalflow",
                                host="localhost",
                                port="5432"
                            )
                            cursor = conn.cursor()

                            cursor.execute("INSERT INTO heartrate_measurements (measurement_time, tag, heartrate, tag_act) VALUES (NOW(), %s, %s, %s)",(tag, tag_heartrate, tag_act))
                            print('--------------------------------------INSERTANDO PULSO --------------------------------')
                            conn.commit()
                            cursor.execute("SELECT heartrate FROM heartrate_measurements WHERE tag = %s ORDER BY measurement_time DESC LIMIT 1", (tag,))
                            valorhr = cursor.fetchone()
                            cursor.execute("SELECT tag_act FROM heartrate_measurements WHERE tag = %s ORDER BY measurement_time DESC LIMIT 1", (tag,))
                            valoract = cursor.fetchone()



                            cursor.close()
                            conn.close()
                            self.update_heartrate(tag, valorhr, valoract)

                        except Exception as e:
                            print(f"Error al insertar en la base de datos: {e}")

        else:
            print(f'Error en la solicitud: {response_api.status_code}')


    def update_heartrate(self, tag, valor, valor2):
        # if self.LAI is not None and self.LAImax is not None and self.LAeq is not None:
        name_node = self.g.get_node(tag)

        if name_node is not None:
            name_node.attrs["heartrate"] = Attribute(float(valor[0]), int(time.time()), self.agent_id)
            name_node.attrs["tag_act"] = Attribute(float(valor2[0]), int(time.time()), self.agent_id)

            print('--------------------------------------nodo actualizado reloj-------------------------------------------------------')
            self.g.update_node(name_node)

    def update_person_tag_edge(self, tag, fence, x, y):
        """
        Comprueba en cuál de los rectángulos se encuentra el punto (x, y).

        :param fence:
        :param node:
        :param x: Coordenada x del punto
        :param y: Coordenada y del punto
        :return: Índice del rectángulo que contiene el punto, o None si no está en ninguno
        """
        x = round(float(x) * 1000)
        y = round(float(y) * 1000)
        person_node = self.g.get_node(tag)
        # print(person_node)
        if fence != '':
            # Get the corresponding key
            try:
                corresponding_key = self.sections[fence]
                # print(corresponding_key, '----------------------------------------------------------------')
                parent_node = self.g.get_node(corresponding_key)
                # print(corresponding_key,'---------------------------------')
                # If person node is in the graph
                if person_node is not None:
                    parent_node_id = person_node.attrs['parent'].value
                    actual_parent_node = self.g.get_node(parent_node_id)
                    # If person node parent node changes (the person changes of room), update the parent node
                    if actual_parent_node.name != corresponding_key:
                        # print(actual_parent_node.name, "is not", corresponding_key)
                        self.g.delete_edge(parent_node_id, person_node.id, "RT")
                        self.rt_api.insert_or_assign_edge_RT(parent_node, person_node.id, [x, y, 0], [0, 0, 0])
                        # Generate random point at certain radius with respect to the parent node
                        angle = random.uniform(0, 2 * math.pi)
                        pos_x = parent_node.attrs['pos_x'].value + self.radius * math.cos(angle)
                        pos_y = parent_node.attrs['pos_y'].value + self.radius * math.sin(angle)
                        person_node.attrs['pos_x'] = Attribute(float(pos_x), self.agent_id)
                        person_node.attrs['pos_y'] = Attribute(float(pos_y), self.agent_id)
                        person_node.attrs['parent'] = Attribute(parent_node.id, self.agent_id)
                        self.g.update_node(person_node)
                    # Else, update the edge
                    else:
                        self.rt_api.insert_or_assign_edge_RT(actual_parent_node, person_node.id, [x, y, 0], [0, 0, 0])
                # Else, insert node
                else:
                    # pos_x = np.random.randint(180, 500)
                    # pos_y = np.random.randint(-440, -160)
                    # print(self.serial_numbers.values)
                    angle = random.uniform(0, 2 * math.pi)
                    pos_x = parent_node.attrs['pos_x'].value + self.radius * math.cos(angle)
                    pos_y = parent_node.attrs['pos_y'].value + self.radius * math.sin(angle)
                    new_node = Node(agent_id=self.agent_id, type='person', name=tag)
                    new_node.attrs['pos_x'] = Attribute(float(pos_x), self.agent_id)
                    new_node.attrs['pos_y'] = Attribute(float(pos_y), self.agent_id)
                    new_node.attrs['parent'] = Attribute(parent_node.id, self.agent_id)
                    new_node.attrs['heartrate'] = Attribute(parent_node.id, self.agent_id)
                    new_node.attrs['tag_act'] = Attribute(parent_node.id, self.agent_id)


                    # try:
                    id_result = self.g.insert_node(new_node)
                    console.print('Person node created -- ', tag, style='red')
                    # try:
                    self.rt_api.insert_or_assign_edge_RT(parent_node, new_node.id,
                                                             [x, y, .0], [.0, .0, .0])
                    # except:
                    #     print('Cant update RT edge')

                    print(' inserted new node  ', id_result)
                    # except:
                    #     print('cant insert node')
                # Update to root
                # else:
                #     self.delete_edge(actual_parent.id, node.id, "RT")
                #     self.rt_api.insert_or_assign_edge_RT(self.g.get_node("root"), node.id, [x, y, 0], [0, 0, 0])
                #     self.g.update_node(node)

            except KeyError:
                # print(f"Error: La clave '{fence}' no existe en 'self.sections'.")
                return



    def plot_tags(self, tag_positions):
        """
        Función para graficar las posiciones de varios tags en un plano 2D.

        Parámetros:
        - tag_positions (dict): Diccionario con los identificadores de los tags como claves y
                                las coordenadas (x, y) como valores en forma de tuplas o listas.
        """
        # Configurar la figura y el eje
        fig, ax = plt.subplots()

        # Iterar sobre el diccionario de posiciones de tags
        for tag, (x, y) in tag_positions.items():
            ax.plot(x, y, 'o', label=f'Tag {tag}')  # Dibuja cada posición como un punto
            ax.text(x, y, f' {tag}', fontsize=9)    # Opcional: etiqueta cada punto con el identificador del tag

        ax.set_xlabel('Posición X')  # Etiqueta del eje X
        ax.set_ylabel('Posición Y')  # Etiqueta del eje Y
        ax.set_title('Posición de Tags')  # Título del gráfico
        ax.legend()  # Mostrar leyenda
        plt.grid(True)  # Mostrar una cuadrícula para facilitar la visualización
        plt.show()  # Mostrar el gráfico

    def insert_db(self, tag, avg_x, avg_y):
        """ Inserta los datos de ubicación en la base de datos. """
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="opticalflow",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()
            if tag is not None and avg_x is not None and avg_y is not None and self.track_data[tag]['in_fence'] is not None:
                # print(f"Inserting into DB - tag: {tag}, room: {self.track_data[tag]['in_fence']}, x: {avg_x}, y: {avg_y}")
                cursor.execute("INSERT INTO people_location (ubication_time, tag_name, room, posicion_x, posicion_y) VALUES (NOW(), %s, %s, %s, %s)",(tag, self.track_data[tag]['in_fence'], avg_x, avg_y))
                # print('--------------------------------------INSERTANDO--------------------------------')
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error al insertar en la base de datos: {e}")

    def callbacks(self):
        # =============== SOCKETIO SLOTS  ================
        # =============================================
        @self.sio.event
        def connect():
            print('Conexión establecida')
            # Enviar el evento 'join'
            self.sio.emit('join', self.algorithm + "_" + self.zone_id)


        def disconnect():
            print('Desconectado del servidor')
        @self.sio.event

        # def say(data):
        #     # Manejar el evento 'say'
        #     # print(data)
        #     try:
        #         json_data = json.loads(data)
        #         print("JSON data", json_data)
        #         # Convierte la cadena a un objeto JSON (diccionario en Python)
        #         if json_data['datatype'] == 80:
        #
        #             # Check if ['x'] and ['y'] exists in json_data
        #             # print("JSON data", json_data)
        #             if 'x' in json_data and 'y' in json_data:
        #                 # print(json_data['tagaddr'] + 'x: ' + str(json_data['x']) + ' y: ' + str(json_data['y']) + ' fence: ' + self.sections[str(json_data['in_fence'])])
        #                 self.update_person_tag_edge(json_data['tagaddr'], str(json_data['in_fence']), json_data['x'], json_data['y'])
        #                 conn = psycopg2.connect(
        #                     dbname="postgres",
        #                     user="postgres",
        #                     password="opticalflow",
        #                     host="localhost",
        #                     port="5432"
        #                 )
        #                 cursor = conn.cursor()
        #
        #
        #                 cursor.execute("INSERT INTO people_location (ubication_time,tag_name,room, posicion_x, posicion_y) VALUES (NOW(),%s,%s,%s,%s)",(json_data['tagaddr'], str(self.sections.get(json_data['in_fence'])),json_data['x'],json_data['y']))
        #                 print('-----------------------------INSERCION--------------------------------------')
        #                 conn.commit()
        #                 cursor.close()
        #                 conn.close()
        #     except json.JSONDecodeError:
        #         print("Los datos recibidos no son un JSON válido.")

        def say(data):
            # print('-----------------------------sayyyyyyy------------------------------------')
            try:
                json_data = json.loads(data)
                # print("JSON data", json_data)
                if json_data['datatype'] == 80:
                    # print(json_data['tagaddr'])
                    tag = json_data.get('tagaddr')
                    if tag is None:
                        print("Advertencia: 'tagaddr' no encontrado en los datos recibidos.")
                        # Maneja el caso de no encontrar 'tagaddr' como sea adecuado para tu aplicación

                    x = json_data.get('x', 0)  # Si no existe 'x', se asigna 0
                    y = json_data.get('y', 0)  # Si no existe 'y', se asigna 0

                    in_fence = json_data.get('in_fence')
                    self.update_person_tag_edge(tag, in_fence, x, y)
                    if x is not None and y is not None and in_fence is not None and tag is not None:
                        self.track_data[tag]['x'].append(x)
                        self.track_data[tag]['y'].append(y)
                        self.track_data[tag]['in_fence'] = str(self.sections.get(in_fence))



            except json.JSONDecodeError:
                print("Los datos recibidos no son un JSON válido.")


        # Usar LocationTracker en tu aplicación
    def convertir_a_pixeles(self, x_mm, y_mm, ancho_hab_mm, alto_hab_mm, ancho_img_px, alto_img_px):
        """
        Convierte las coordenadas de una habitación en milímetros a coordenadas de imagen en píxeles.

        :param x_mm: Coordenada x en la habitación en milímetros.
        :param y_mm: Coordenada y en la habitación en milímetros.
        :param ancho_hab_mm: Ancho de la habitación en milímetros.
        :param alto_hab_mm: Alto de la habitación en milímetros.
        :param ancho_img_px: Ancho de la imagen en píxeles.
        :param alto_img_px: Alto de la imagen en píxeles.
        :return: Coordenadas (x, y) en píxeles.
        """

        # Calcular la relación de escala
        escala_x = ancho_img_px / ancho_hab_mm
        escala_y = alto_img_px / alto_hab_mm

        # Convertir las coordenadas en x
        x_px = x_mm * escala_x

        # Convertir e invertir las coordenadas en y
        y_px = alto_img_px - (y_mm * escala_y)
        return int(x_px), int(y_px)

    ######################
    # From the RoboCompVisualElementsPub you can publish calling this methods:
    # self.visualelementspub_proxy.setVisualObjects(...)

    ######################
    # From the RoboCompVisualElementsPub you can use this types:
    # RoboCompVisualElementsPub.TObject
    # RoboCompVisualElementsPub.TData

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
