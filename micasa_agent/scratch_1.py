import socketio
import json
import matplotlib.pyplot as plt
from PyQt6.QtCore import QRect

# Configuración del cliente Socket.IO
zone_id = '1'  # Zone ID
algorithm = '81'  # Algorithm (TWR:80; TDOA:81)
server_url = 'http://158.49.247.176:3000?token=d7c9a1b636324d088f9677d0340ac8cd'


# Crear una instancia del cliente Socket.IO
sio = socketio.Client()

@sio.event
def connect():
    print('Conexión establecida')
    # Enviar el evento 'join'
    sio.emit('join', algorithm + "_" + zone_id)

@sio.event
def say(data):
    # Manejar el evento 'say'
    # print(data)
    try:
        json_data = json.loads(data)  # Convierte la cadena a un objeto JSON (diccionario en Python)
        # print(json_data)
    except json.JSONDecodeError:
        print("Los datos recibidos no son un JSON válido.")
    # print(json_data)
    if json_data['type'] == 'normal':
        # print('Message NORMAL')
        print(json_data['tagaddr'] + 'x: '+ str(json_data['x']) + ' y: ' + str(json_data['y']))
        # if json_data['tagaddr'] == '59b1':
        #     print('x: '+ str(json_data['x']) + ' y: ' + str(json_data['y']))

@sio.event
def disconnect():
    print('Desconectado del servidor')

# Crear cuatro objetos QRect
rect1 = QRect(10, 10, 50, 50)
rect2 = QRect(70, 10, 50, 50)
rect3 = QRect(130, 10, 50, 50)
rect4 = QRect(190, 10, 50, 50)

print(rect1.x(), rect1.y(), rect1.width(), rect1.height())
print(rect2.x(), rect2.y(), rect2.width(), rect2.height())
print(rect3.x(), rect3.y(), rect3.width(), rect3.height())
print(rect4.x(), rect4.y(), rect4.width(), rect4.height())

# Conectar al servidor
try:
    sio.connect(server_url)
except socketio.exceptions.ConnectionError as e:
    print('Error de conexión:', e)

# Mantener el script en ejecución
try:
    while True:
        pass
except KeyboardInterrupt:
    # Desconectar de forma segura al salir
    sio.disconnect()