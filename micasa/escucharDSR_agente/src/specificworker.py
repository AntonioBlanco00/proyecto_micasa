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
# import cv2
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import csv
import random
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
#import pydsr
# import socketio
# import json
# import random
# import math
# #from PyQt6.QtCore import QRect, QPointF, QPoint
# import numpy as np
# # import cv2
# import threading
# import signal
# import sys
# import matplotlib.pyplot as plt
# import copy
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import psycopg2
import re
import time
from psycopg2 import sql

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 373
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)
        self.rt_api = rt_api(self.g)

        self.temperature = None
        self.humidity = None
        self.illumination = None
        self.device_name=None
        self.LAI = None
        self.LAImax = None
        self.LAeq = None
        self.applicationId=None
        self.state = None
        self.voltage = None

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
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


        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "sensores_micasa")
        print('---------------------------------------------CONECTADO EN EL INIT-------------------------------------------------------' )
        # self.client.username_pw_set('Proyecto-MiCasa', 'opticalflow')

        self.client.on_connect = self.on_connect
        self.client.connect("192.168.1.116", 1883, 60)

        # Conecta al broker MQTT
        broker_address = "192.168.1.116"
        broker_port = 1883
        topic = 'application/+/device/+/event/up'

        self.client.username_pw_set(username="Proyecto-MiCasa", password="opticalflow")
        self.client.connect(broker_address)
        self.client.subscribe(topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

        print("-----------SUSCRITO--------------")


    def __del__(self):
        """Destructor"""


    @QtCore.Slot()


    def compute(self):
        print('--------------------COMPUTE-----------------------')

        return True
    def setParams(self, params):

        return True
    def startup_check(self):
        print(f"Testing RoboCompVisualElementsPub.TObject from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TObject()
        print(f"Testing RoboCompVisualElementsPub.TData from ifaces.RoboCompVisualElementsPub")
        test = ifaces.RoboCompVisualElementsPub.TData()
        QTimer.singleShot(200, QApplication.instance().quit)



    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        if rc == 0:
            client.subscribe("application/+/device/+/event/up")  # Suscribe solo si la conexión es exitosa
            print("-------------------------------------------   CONECTADO     ----------------------------------------------")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):

        payload = msg.payload.decode("utf-8")
        parsed_data = self.parse_json_like_string(payload)
        # print("------------------------------------------------------_", parsed_data)

        self.applicationId = parsed_data.get('applicationId')

        try:
            if self.applicationId == 'd5d4d22f-20ac-432e-abc7-a8c2facafed6':
                self.on_message_ambiental(msg)
            elif self.applicationId == '82a77e91-32c9-4fe3-a228-73c4eec5385e':
                self.on_message_sonido(msg)
            elif self.applicationId == '82a77e91-32c9-4fe3-a228-73c4eec5385e':
                self.on_message_actuador(msg)
        except Exception as e:
            print(f"Error on_message {e}")
    def on_message_ambiental (self, msg):
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="opticalflow",
            host="localhost",
            port="5432"
        )
        payload = msg.payload.decode("utf-8")
        # print("Received message:", payload)
        data = {}

        parsed_data = self.parse_json_like_string(payload)
        # print("------------------------------------_", parsed_data)
        # for key, value in parsed_data.items():
        #     print(f"Clave: {key}, Valor: {value}")
        #
        #     # Si necesitas manejar estructuras anidadas, puedes hacer comprobaciones y bucles adicionales aquí
        #     if isinstance(value, dict):
        #         for subkey, subvalue in value.items():
        #             print(f"   Subclave: {subkey}, Subvalor: {subvalue}")

        self.device_name = parsed_data.get('deviceName')
        self.applicationId = parsed_data.get('applicationId')
        self.temperature = None
        self.humidity = None
        self.illumination = None

        # Ejemplo de acceso a valores en un objeto anidado dentro de 'object'
        if 'object' in parsed_data is not None:
            object_data = parsed_data['object']
            temperature_str = object_data.get('temperature')
            if temperature_str is not None:
                self.temperature = float(temperature_str)
            else:
                # Manejo del caso donde temperature no está disponible
                self.temperature = None  # O puedes establecer un valor predeterminado
                print("Advertencia: No se encontró 'temperature' en el mensaje recibido.")

            # Convertir humedad de manera segura
            humidity_str = object_data.get('humidity')
            if humidity_str is not None:
                self.humidity = float(humidity_str)
            else:
                self.humidity = None
                print("Advertencia: No se encontró 'humidity' en el mensaje recibido.")

            # Convertir iluminación de manera segura
            illumination_str = object_data.get('illumination')
            if illumination_str is not None:
                self.illumination = float(illumination_str)
            else:
                self.illumination = None
                print("Advertencia: No se encontró 'illumination' en el mensaje recibido.")

    #

        # Regex para capturar pares clave-valor
        # inserta valores en la BBDD
        cursor = conn.cursor()
        if self.temperature is not None and self.humidity is not None and self.illumination is not None:
            print(f"Device Name: {self.device_name}")
            print(f"Humidity: {self.humidity}")

            print(f"Temperature: {self.temperature}")
            print(f"Illumination: {self.illumination}")

            print('-----------------------------------Insertando valores--------------')
            cursor.execute("INSERT INTO ambiental_measurements (measurement_time,sensor_name,temperature, humidity, illumination) VALUES (NOW(),%s,%s,%s,%s)",(self.device_name, self.temperature, self.humidity, self.illumination))
            conn.commit()
            cursor.execute("SELECT temperature, humidity, illumination FROM ambiental_measurements WHERE sensor_name = %s ORDER BY measurement_time DESC LIMIT 1", (self.device_name,))

        # Obtener el resultado
            valor = cursor.fetchone()
            print (valor)
        # Cierra la conexión
            cursor.close()
            conn.close()
            # self.obtener_valor_sensor()
            self.update_sensor_ambiental(self.device_name, valor)

    def on_message_sonido(self,msg):
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="opticalflow",
            host="localhost",
            port="5432"
        )
        payload = msg.payload.decode("utf-8")
        # print("Received message:", payload)
        data = {}
        parsed_data = self.parse_json_like_string(payload)
        # print("------------------------------------_", parsed_data)

        # for key, value in parsed_data.items():
        #     print(f"Clave: {key}, Valor: {value}")
        #
        #     # Si necesitas manejar estructuras anidadas, puedes hacer comprobaciones y bucles adicionales aquí
        #     if isinstance(value, dict):
        #         for subkey, subvalue in value.items():
        #             print(f"   Subclave: {subkey}, Subvalor: {subvalue}")

        self.device_name = parsed_data.get('deviceName')
        self.applicationId = parsed_data.get('applicationId')
        self.LAI = None
        self.LAImax = None
        self.LAeq = None

        # Ejemplo de acceso a valores en un objeto anidado dentro de 'object'
        if 'object' in parsed_data:
            object_data = parsed_data['object']
            self.LAI = object_data.get('LAI')  # Convertir a float para asegurar el tipo correcto
            self.LAImax = object_data.get('LAImax')
            self.LAeq = object_data.get('LAeq')


        # Regex para capturar pares clave-valor
        # inserta valores en la BBDD
        cursor = conn.cursor()
        if self.LAI is not None and self.LAImax is not None and self.LAeq is not None:
            print(f"Device Name: {self.device_name}")

            print(f"LAI: {self.LAI}")
            print(f"LAImax: {self.LAImax}")
            print(f"LAeq: {self.LAeq}")
            print('-----------------------------------Insertando valores--------------')
            cursor.execute("INSERT INTO sound_measurements (measurement_time,sensor_name,LAI, LAImax, LAeq) VALUES (NOW(),%s,%s,%s,%s)", (self.device_name, self.LAI, self.LAImax, self.LAeq))
            conn.commit()
            cursor.execute("SELECT lai, laimax, laeq FROM sound_measurements WHERE sensor_name = %s ORDER BY measurement_time DESC LIMIT 1", (self.device_name,))

        # Obtener el resultado
            valor = cursor.fetchone()
            print (valor)
        # Cierra la conexión
            cursor.close()
            conn.close()
            # self.obtener_valor_sensor()
            self.update_sensor_sonido(self.device_name, valor)
            # Cierra la conexión




    def on_message_actuador(self,msg):
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="opticalflow",
            host="localhost",
            port="5432"
        )
        payload = msg.payload.decode("utf-8")
        # print("Received message:", payload)
        data = {}
        parsed_data = self.parse_json_like_string(payload)
        # print("------------------------------------_", parsed_data)

        # for key, value in parsed_data.items():
        #     print(f"Clave: {key}, Valor: {value}")
        #
        #     # Si necesitas manejar estructuras anidadas, puedes hacer comprobaciones y bucles adicionales aquí
        #     if isinstance(value, dict):
        #         for subkey, subvalue in value.items():
        #             print(f"   Subclave: {subkey}, Subvalor: {subvalue}")

        self.device_name = parsed_data.get('deviceName')
        self.applicationId = parsed_data.get('applicationId')
        self.state = None
        self.voltage = None


        # Ejemplo de acceso a valores en un objeto anidado dentro de 'object'
        if 'object' in parsed_data:
            object_data = parsed_data['object']
            self.state = object_data.get('state')  # Convertir a float para asegurar el tipo correcto
            self.voltage = float(object_data.get('voltage'))




        # Regex para capturar pares clave-valor
        # inserta valores en la BBDD
        cursor = conn.cursor()
        if self.state is not None and self.voltage is not None:
            print(f"Device Name: {self.device_name}")
            print(f"state: {self.state}")
            print(f"voltage: {self.voltage}")

            print('-----------------------------------Insertando valores--------------')
            cursor.execute("INSERT INTO actuador_measurements (tiempo, sensor_name, estado, voltage) VALUES (NOW(),%s,%s,%s)",  (self.device_name, self.state, self.voltage))
            conn.commit()
            cursor.execute("SELECT estado, voltage FROM actuador_measurements WHERE sensor_name = %s ORDER BY tiempo DESC LIMIT 1", (self.device_name,))

        # Obtener el resultado
            valor = cursor.fetchone()
            print (valor)
        # Cierra la conexión
            cursor.close()
            conn.close()
            # self.obtener_valor_sensor()
            self.update_sensor_ambiental(self.device_name, valor)
        # Cierra la conexión
            cursor.close()
            conn.close()
            self.update_sensor_actuador(self.device_name)


    def parse_nested_json_like_string(self,value):
        if value.startswith('{'):
            return self.parse_json_like_string(value[1:-1])  # Remove the enclosing {}
        elif value.startswith('['):
        # Assume a simple list of objects (the most common case in your example)
            items = []
            for item in value[1:-1].split('},{'):
                items.append(self.parse_json_like_string('{' + item + '}'))
            return items
        return value


    def parse_json_like_string(self,payload):
        pattern = r'\"([^\"]+)\":(?:\"([^\"]*)\"|\[([^\[\]]*)\]|(\{[^\{\}]*\})|(\d+\.\d+|\d+|true|false|null))'
        results = re.findall(pattern, payload)
        parsed_data = {}
        for match in results:
            key = match[0]
            value = next(filter(None, match[1:]))  # El primer grupo no None es nuestro valor

            if value.startswith('{') or value.startswith('['):
                parsed_data[key] = self.parse_nested_json_like_string(value)
            else:
                parsed_data[key] = value
        return parsed_data

    def update_sensor_ambiental(self, name, valor):
        # if valor[0] is not None and valor[1] is not None and valor[2] is not None:

        name_node = self.g.get_node(name)
        if name_node is not None:
            name_node.attrs["temperature"] = Attribute(float(valor[0]), int(time.time()), self.agent_id)
            name_node.attrs["humidity"] = Attribute(float(valor[1]), int(time.time()), self.agent_id)
            name_node.attrs["illumination"] = Attribute(float(valor[2]), int(time.time()), self.agent_id)
            self.g.update_node(name_node)
            print('------------------------nodo actualizado ambiental---------------------')

    def update_sensor_sonido(self, name, valor):
        # if self.LAI is not None and self.LAImax is not None and self.LAeq is not None:
        name_node = self.g.get_node(name)

        if name_node is not None:
            name_node.attrs["LAI"] = Attribute(float(valor[0]), int(time.time()), self.agent_id)
            name_node.attrs["LAImax"] = Attribute(float(valor[1]), int(time.time()), self.agent_id)
            name_node.attrs["LAeq"] = Attribute(float(valor[2]), int(time.time()), self.agent_id)
            print('------------------------nodo actualizado sonido---------------------')
            self.g.update_node(name_node)

    def update_sensor_actuador(self, name, valor):
        # if self.state is not None and self.voltage is not None:
        name_node = self.g.get_node(name)
        if name_node is not None:
            name_node.attrs["state"] = Attribute(valor[0], int(time.time()), self.agent_id)
            name_node.attrs["voltage"] = Attribute(valor[1], int(time.time()), self.agent_id)
            self.g.update_node(name_node)
            print('------------------------nodo actualizado actuador---------------------')


    def update_node_att(self, id: int, attribute_names: [str]):
        # self.update_sensor_ambiental('ambiental_cocina')
        #console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        pass
    def update_node(self, id: int, type: str):
        #console.print(f"UPDATE NODE: {id} {type}", style='green')
        pass
    def delete_node(self, id: int):
        #console.print(f"DELETE NODE:: {id} ", style='green')
        pass

    def update_edge(self, fr: int, to: int, type: str):

        #console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')
        pass

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        #console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')
        pass

    def delete_edge(self, fr: int, to: int, type: str):
        #console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')
        pass
