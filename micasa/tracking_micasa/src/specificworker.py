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

from PySide2.QtGui import QPolygonF, QPainter, QPen, QColor, QFont, QImage
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from rich.console import Console
from genericworker import *
import interfaces as ifaces
from PySide2.QtCore import QRect, QPointF, QPoint, QSize, Qt
import sys
import socketio

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

import json
import cv2
import numpy as np
import random
import math

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
import Ice

import subprocess


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 888
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
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)
        #Se toma como punto de refrencia el vértice de arriba a la izquierda

        self.sections = {
            "room_3":QRect(QPoint(3800,1200),QSize(2750,2780)),
            "room_4":QRect(QPoint(3220,4800),QSize(2650,3800)),
            "bathroom_2":QRect(QPoint(0,2640),QSize(2700,1640)),
            "laundry":QRect(QPoint(3800,0),QSize(2400,1170)),
            "terrace":QRect(QPoint(3240,8580),QSize(2250,1200)),
            "bathroom_1": QRect(QPoint(0, 4280), QSize(2200, 2100)),
            "kitchen": QRect(QPoint(6520, 0), QSize(2700, 3000)),
            "living_room": QRect(QPoint(5870, 0), QSize(4130, 4980)),
            "corridor": QRect(QPoint(), QSize()),
            "room_1": QRect(QPoint(0, 6380), QSize(3220, 3250)),
            "room_2": QRect(QPoint(0, 0), QSize(3750, 2640))
        }
        self.img = cv2.imread('plano_vivienda.jpeg')
        self.img = cv2.resize(self.img, (0, 0), fx=0.5, fy=0.5)
        self.person_read = cv2.imread('/home/robolab-micasa/robocomp/components/micasa/tracking_micasa/src/d.png', cv2.IMREAD_UNCHANGED)
        self.alpha = self.person_read[:, :, 3]
        self.alpha = np.divide(self.alpha, 255.0).astype('uint8')
        self.alpha = cv2.resize(self.alpha, (30, 30), fx=0.5, fy=0.5)
        self.alpha_inv = 1 - self.alpha
        self.person = self.person_read[:, :, 0:3]

        self.person = cv2.resize(self.person, (30, 30), fx=0.5, fy=0.5)

        cv2.namedWindow('plano_vivienda', cv2.WINDOW_NORMAL)
        cv2.imshow('plano_vivienda', self.img)
        self.img_clean = self.img.copy()

        self.radius = 100

        self.timer.timeout.connect(self.compute)
        self.timer.start(self.Period)


        # self.sections = {
        #     "0":"bathroom_1",
        #     "7":"bathroom_2",
        #     "13":"lavadero",
        #     "17":"terraza",
        #     "5":"kitchen",
        #     "1":"room1",
        #     "6":"room2",
        #     "9":"room3",
        #     "10":"room4",
        #     "2":"living_room",
        #     "11":"pasillo",
        #     "18":"pasillo",
        #     "20":"pasillo"
        # }
        # print(self.sections.values())
        #
        # print("secciones creadas")
        #
        #
        scale_factor = 10  # Factor de escala para ajustar las dimensiones a un tamaño razonable
        image = QImage(1200, 1200, QImage.Format_ARGB32)
        image.fill(QColor("white"))  # Rellenar de blanco

        painter = QPainter(image)
        painter.setPen(QPen(QColor("black"), 2))  # Configurar el lápiz
        painter.setFont(QFont('Arial', 10))
        # for id, name in self.sections.items():
        #     shape = self.sections[name]
        #     # Aquí va tu código para manejar la forma, e.g., dibujarla
        #     print(f"Dibujando {name} con forma {shape}")

        print("Imagen creada")
        # Dibujar cada sección
        # for name, shape in self.sections.items():
        #     print("Entra al bucle")
        #     print(f"Dibujando {name} con forma {shape}")
        #         # Escalar y dibujar QRect
        #     scaled_rect = QRect(shape.x() // scale_factor, shape.y() // scale_factor, shape.width() // scale_factor,
        #                             shape.height() // scale_factor)
        #     painter.drawRect(scaled_rect)
        #     painter.drawText(scaled_rect.adjusted(5, 5, -5, -5), Qt.AlignCenter, name)
        #     print("------- llega a QRect ----------------")

        for name, shape in self.sections.items():
            print(f"Dibujando {name} con forma {shape}")
            if isinstance(shape, QRect):
                scaled_rect = QRect(shape.x() // scale_factor, shape.y() // scale_factor,
                                    shape.width() // scale_factor, shape.height() // scale_factor)
                painter.drawRect(scaled_rect)
                painter.drawText(scaled_rect.adjusted(5, 5, -5, -5), Qt.AlignCenter, name)
            elif isinstance(shape, QPolygonF):
                scaled_polygon = QPolygonF([QPoint(pt.x() // scale_factor, pt.y() // scale_factor) for pt in shape])
                painter.drawPolygon(scaled_polygon)

        painter.end()  # Finalizar el dibujo

        # Guardar la imagen
        image.save("plano_vivienda.jpeg")

    def __del__(self):
        """Destructor"""
    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        print('SpecificWorker.compute...')
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)c
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])
        self.lista_personas = ifaces.RoboCompVisualElements.TObjects()
        self.lista_personas = self.visualelements_proxy.getVisualObjects(self.lista_personas)

        # print(self.lista_personas)
        # print(type(self.lista_personas.objects))
        #
        height, width, channels = self.img.shape
        # Draw the people in the image
        self.img = self.img_clean.copy()
        for person in self.g.get_nodes_by_type("person"):
            rt_edge = self.rt_api.get_edge_RT(self.g.get_node(person.attrs["parent"].value), person.id)
            tx, ty, _ = rt_edge.attrs['rt_translation'].value
            print(tx, ty)
            # tx, ty, _ = (5050,7909,0)
            x, y = self.convertir_a_pixeles(tx, ty, 9600, 9630, width, height)
            window = self.img[y:y + self.person.shape[0], x:x + self.person.shape[1]]
            # for c in range(0, 3):
            #     window[:, :, c] = window[:, :, c] * self.alpha_inv + self.person[:, :, c] * self.alpha
            cv2.circle(self.img, (x, y), 15, (255, 0, 255), -1)
            cv2.circle(self.img, (x, y), 15, (0, 0, 0), 10)
            cv2.putText(self.img, person.name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Clean self.img
        cv2.imshow('plano_vivienda', self.img)
        # cv2.waitKey(1)

        for obj in self.lista_personas.objects:
            object_id = obj.id + 300 #offset pq los ids del VisEl son 0,1 y 2 y tienen que ser el 300,301 y 302  # Suponiendo que obj tiene un atributo 'id'
            x_value = obj.x  # Suponiendo que obj tiene un atributo 'x'
            y_value = obj.y  # Suponiendo que obj tiene un atributo 'y'
            # print(x_value,-y_value)
            name=self.is_point_in_sections(x_value, -y_value, object_id, self.sections)
            self.update_person_tag_edge(object_id,name,x_value,y_value)



    def startup_check(self):
        print(f"Testing RoboCompVisualElements.TRoi from ifaces.RoboCompVisualElements")
        test = ifaces.RoboCompVisualElements.TRoi()
        print(f"Testing RoboCompVisualElements.TObject from ifaces.RoboCompVisualElements")
        test = ifaces.RoboCompVisualElements.TObject()
        QTimer.singleShot(200, QApplication.instance().quit)


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

    def callbacks(self):
        # =============== SOCKETIO SLOTS  ================
        # =============================================
        @self.sio.event
        def connect():
            print('Conexión establecida')
            # Enviar el evento 'join'
            self.sio.emit('join', self.algorithm + "_" + self.zone_id)

        @self.sio.event
        def disconnect():
            print('Desconectado del servidor')

        @self.sio.event
        def say(data):
            # Manejar el evento 'say'
            # print(data)
            try:
                json_data = json.loads(data)  # Convierte la cadena a un objeto JSON (diccionario en Python)
                if json_data['datatype'] == 81:
                    # Check if ['x'] and ['y'] exists in json_data
                    # print("JSON data", json_data)
                    if 'x' in json_data and 'y' in json_data:
                        # print(json_data['tagaddr'] + 'x: ' + str(json_data['x']) + ' y: ' + str(json_data['y']) + ' fence: ' + self.sections[str(json_data['in_fence'])])
                        self.update_person_tag_edge(json_data['tagaddr'], str(json_data['in_fence']), json_data['x'], json_data['y'])
            except json.JSONDecodeError:
                print("Los datos recibidos no son un JSON válido.")




    def is_point_in_sections(self, x, y, humano_id , sections):
        point = QPoint(x*1000, y*1000)
        for fence, shape in sections.items():
            if isinstance(shape, QRect):
                if shape.contains(point) == True:
                    print( f"El {humano_id} que está en el punto ({x}, {y}) está dentro de la sección '{fence}'")
                    return fence
            elif isinstance(shape, QPolygonF):
                if shape.containsPoint(point,Qt.FillRule.OddEvenFill) == True:  # Qt.FillRule puede ser OddEvenFill o WindingFill
                    print( f"El {humano_id} que está en el punto ({x}, {y}) está dentro de la sección '{fence}'")
                    return fence

        print( f"El {humano_id} que está en el punto ({x}, {y}) está en el corridor")
        return "corridor"


    def update_person_tag_edge(self, humano, fence, x, y):
        """
        Comprueba en cuál de los rectángulos se encuentra el punto (x, y).

        :param fence:
        :param node:
        :param x: Coordenada x del punto
        :param y: Coordenada y del punto
        :return: Índice del rectángulo que contiene el punto, o None si no está en ninguno
        """
        x = x * 1000
        y = y * 1000
        # person_node = self.g.get_nodes_by_type('person')
        person_node=self.g.get_node(humano)
        # print(person_node)
        # print(person_node.objects)
        if fence != '':
            # Get the corresponding key
            # corresponding_key = self.sections[fence]
            # print(corresponding_key,'-------------------------------------')
            corresponding_key=fence
            print(corresponding_key,'-------------------------------------')

            parent_node = self.g.get_node(corresponding_key)

            # If person node is in the graph
            if person_node is not None:
                parent_node_id = person_node.attrs['parent'].value
                actual_parent_node = self.g.get_node(parent_node_id)
                print(actual_parent_node.name,'dklgasladhñls')
                # If person node parent node changes (the person changes of room), update the parent node
                if actual_parent_node.name != corresponding_key:

                    #COmprueba que si la estancia nueva es igual a cocina, en cuyo caso genera un audio de bienvenida a la cocina
                    if corresponding_key == "kitchen":
                        audio_path = os.path.join('./static/audio', f"bienvenida_{person_node.id}.mp3")

                        absolute_audio_path = os.path.abspath(audio_path)
                        print(f"Ruta absoluta del archivo de audio: {absolute_audio_path}")
                        tts = gTTS(text=f"Bienvenido a la cocina {person_node.name}", lang='es')
                        print("AUDIO BIENVENIDA GENERADO")

                        tts.save(audio_path)

                        audio = AudioSegment.from_file(audio_path)
                        play(audio)
                        # Lanzar el script de Flask en un proceso separado
                        subprocess.Popen(["python3", "./Mi_Casa_app/app.py"])


                    new_parent_node=self.g.get_node(corresponding_key)
                    print(actual_parent_node.name, "is not", corresponding_key)
                    self.g.delete_edge(parent_node_id, person_node.id, "RT")
                    self.rt_api.insert_or_assign_edge_RT(new_parent_node, person_node.id, [x, y, 0], [0, 0, 0])
                    # Generate random point at certain radius with respect to the parent node
                    angle = random.uniform(0, 2 * math.pi)
                    pos_x = new_parent_node.attrs['pos_x'].value + self.radius * math.cos(angle)
                    pos_y = new_parent_node.attrs['pos_y'].value + self.radius * math.sin(angle)
                    person_node.attrs['pos_x'] = Attribute(float(pos_x), self.agent_id)
                    person_node.attrs['pos_y'] = Attribute(float(pos_y), self.agent_id)
                    person_node.attrs['parent'] = Attribute(new_parent_node.id, self.agent_id)
                    self.g.update_node(person_node)
                # Else, update the edge
                else:
                    self.rt_api.insert_or_assign_edge_RT(actual_parent_node, person_node.id, [x, y, 0], [0, 0, 0])
            # Else, insert node
            # else:
            #     # pos_x = np.random.randint(180, 500)
            #     # pos_y = np.random.randint(-440, -160)
            #     angle = random.uniform(0, 2 * math.pi)
            #     pos_x = parent_node.attrs['pos_x'].value + self.radius * math.cos(angle)
            #     pos_y = parent_node.attrs['pos_y'].value + self.radius * math.sin(angle)
            #     new_node = Node(agent_id=self.agent_id, type='person', name=person_node.attrs['name'].value)
            #     new_node.attrs['pos_x'] = Attribute(float(pos_x), self.agent_id)
            #     new_node.attrs['pos_y'] = Attribute(float(pos_y), self.agent_id)
            #     new_node.attrs['parent'] = Attribute(parent_node.id, self.agent_id)
            #     # try:
            #     id_result = self.g.insert_node(new_node)
            #     console.print('Person node created -- ', humano, style='red')
            #     # try:
            #     self.rt_api.insert_or_assign_edge_RT(parent_node, new_node.id,
            #                                          [x, y, .0], [.0, .0, .0])
            #     # except:
            #     #     print('Cant update RT edge')
            #
            #     print(' inserted new node  ', id_result)
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




