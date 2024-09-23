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
import socketio
import json
import random
import math
from PySide2.QtCore import QRect, QPointF, QPoint
import numpy as np
import cv2
import threading
import signal
import sys
import matplotlib.pyplot as plt
import copy

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
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 50

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
            # Configuración del cliente Socket.IO
            self.sio = socketio.Client()
            self.zone_id = '1'  # Zone ID
            self.algorithm = '81'  # Algorithm (TWR:80; TDOA:81)
            self.server_url = 'http://158.49.247.176:3000?token=d7c9a1b636324d088f9677d0340ac8cd'

            # self.people_parents_in_graph = {}

            self.sections = {
                "bathroom": QRect(QPoint(7210, 4120), QSize(2140, 1990)),
                "kitchen": QRect(QPoint(3850, 8370), QSize(3930, 2550)),
                "living_room": QRect(QPoint(0, 8370), QSize(3850, 3100)),
                "corridor": QPolygonF(),
                "room1": QRect(QPoint(0, 4120), QSize(3780, 4120)),
                "room2": QRect(QPoint(3780, 4120), QSize(3420, 4120))
            }

            # Maybe can be change for a vector and using the index
            self.sections = {
                "0" : "bathroom",
                "5" : "kitchen",
                "2" : "living_room",
                "11" : "corridor",
                "8" : "corridor",
                "1" : "room_1",
                "6" : "room_2"
            }

            # self.key_pressed_signal.connect(self.on_key_pressed)
            try:
                self.callbacks()
                self.sio.connect(self.server_url)

            except socketio.exceptions.ConnectionError as e:
                print('Error de conexión:', e)

            # Open schematic.jpeg and create a window to draw it scaled by 0.5
            self.img = cv2.imread('schematic.jpeg')
            self.img = cv2.resize(self.img, (0, 0), fx=0.5, fy=0.5)
            self.person_read = cv2.imread('/home/usuario/robocomp/components/micasa/micasa_agent/src/d.png', cv2.IMREAD_UNCHANGED)
            self.alpha = self.person_read[:,:,3]
            self.alpha = np.divide(self.alpha,255.0).astype('uint8')
            self.alpha = cv2.resize(self.alpha, (30, 30), fx=0.5, fy=0.5)
            self.alpha_inv = 1 - self.alpha
            self.person = self.person_read[:,:,0:3]

            self.person = cv2.resize(self.person, (30, 30), fx=0.5, fy=0.5)

            cv2.namedWindow('Schematic', cv2.WINDOW_NORMAL)
            cv2.imshow('Schematic', self.img)
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
            serial_numbers = self.params_tags.split(',')
            name_list = self.params_tags_names.split(',')
            self.tag_names = {serial: name for serial, name in zip(serial_numbers, name_list)}
            print("----------TAG NAMES------------")
            print(self.tag_names)
        except:
            print("Error reading config params")

        return True

    @QtCore.Slot()
    def compute(self):
        # print("PEOPLE", self.people)
        # Get self.img shape
        height, width, channels = self.img.shape
        # Draw the people in the image
        self.img = self.img_clean.copy()
        for person in self.g.get_nodes_by_type("person"):
            rt_edge = self.rt_api.get_edge_RT(self.g.get_node(person.attrs["parent"].value), person.id)
            tx, ty, _ = rt_edge.attrs['rt_translation'].value
            x, y = self.convertir_a_pixeles(tx, ty, 9350, 8370, width, height)
            window = self.img[y:y+self.person.shape[0], x:x+self.person.shape[1]]
            # for c in range(0,3):
            #     window[:,:,c] = window[:,:,c]*self.alpha_inv+self.person[:,:,c]*self.alpha
            cv2.circle(self.img, (x, y), 15, (255, 0, 255), -1)
            cv2.circle(self.img, (x, y), 15, (0, 0, 0), 10)
            cv2.putText(self.img, person.name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
        # Clean self.img
        cv2.imshow('Schematic', self.img)
        cv2.waitKey(1)
    def startup_check(self):
        print(f"Testing RoboCompVisualElementsPub.TObject from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TObject()
        print(f"Testing RoboCompVisualElementsPub.TData from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TData()
        QTimer.singleShot(200, QApplication.instance().quit)

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
        person_node = self.g.get_node(self.tag_names[tag])
        if fence is not '':
            # Get the corresponding key
            corresponding_key = self.sections[fence]
            parent_node = self.g.get_node(corresponding_key)

            # If person node is in the graph
            if person_node is not None:
                parent_node_id = person_node.attrs['parent'].value
                actual_parent_node = self.g.get_node(parent_node_id)
                print(actual_parent_node)
                # If person node parent node changes (the person changes of room), update the parent node
                if actual_parent_node.name != corresponding_key:
                    print(actual_parent_node.name, "is not", corresponding_key)
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
                angle = random.uniform(0, 2 * math.pi)
                pos_x = parent_node.attrs['pos_x'].value + self.radius * math.cos(angle)
                pos_y = parent_node.attrs['pos_y'].value + self.radius * math.sin(angle)
                new_node = Node(agent_id=self.agent_id, type='person', name=self.tag_names[tag])
                new_node.attrs['pos_x'] = Attribute(float(pos_x), self.agent_id)
                new_node.attrs['pos_y'] = Attribute(float(pos_y), self.agent_id)
                new_node.attrs['parent'] = Attribute(parent_node.id, self.agent_id)
                # try:
                id_result = self.g.insert_node(new_node)
                console.print('Person node created -- ', self.tag_names[tag], style='red')
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
