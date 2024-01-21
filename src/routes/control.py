import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms

import matplotlib.pyplot as plt
import numpy as np
import os

import uuid
import cv2
import time
import pytz
import datetime
import bson
import mediapipe as mp

from cryptography.fernet import Fernet
from passlib.hash import pbkdf2_sha256
from decouple import config
from PIL import Image
from db import db



key = b'E5bsJkAn2CYlsdDZepGyi69SHnCT77GQw8EUOiCTUO4='
cipher_suite = Fernet(key)

def generar_grafico_estadisticas(data):
    estadisticas = {
        "Facilidad de Uso": data['facilidad_uso'],
        "Utilidad Percibida": data['utilidad'],
        "Aceptación Tecnológica": data['aceptacion_tecnologica'],
        "Motivación para el Uso Continuo": data['motivacion'],
        "Efectividad en la Gestión del Estrés": data['efectividad'],
        "Calidad del Contenido": data['calidad'],
        "Satisfacción General": data['satisfaccion']
    }
 
    # Colores para las calificaciones
    colores = {
        "Excelente": "green",
        "Bueno": "yellow",
        "Aceptable": "orange",
        "Malo": "red"
    }

    # Función para asignar colores
    def asignar_color(valor):
        if valor >= 4:
            return colores["Excelente"]
        elif valor >= 3:
            return colores["Bueno"]
        elif valor >= 2:
            return colores["Aceptable"]
        else:
            return colores["Malo"]

    # Crear gráfico de barras
    fig = plt.figure(figsize=(10, 6))
    for i, (categoria, valor) in enumerate(estadisticas.items()):
        plt.barh(categoria, valor, color=asignar_color(valor))
    plt.xlabel('Valor')
    plt.title('Estadísticas')
    plt.grid(True)

    # Guardar el gráfico en un archivo
    plt.savefig('src/static/images/estadistica/grafico.png')

    # Cerrar la figura
    plt.close(fig)

    return True

def get_usuario(usuario):
    usuario = db['administrador'].find_one({"usuario":usuario})
    return usuario

def insert_usuario(data):
    data['contrasenia'] = pbkdf2_sha256.encrypt(data['contrasenia'])
    db['administrador'].insert_one(data)

def get_sesiones():
    sesion = list(db['sesion'].find())
    for s in sesion:
        s['persona']['nombre'] = cipher_suite.decrypt(s['persona']['nombre']).decode()
        s['persona']['apellido'] = cipher_suite.decrypt(s['persona']['apellido']).decode()
        s['persona']['cedula'] = cipher_suite.decrypt(s['persona']['cedula']).decode()
        s['persona']['email'] = cipher_suite.decrypt(s['persona']['email']).decode()
        s['persona']['telefono'] = cipher_suite.decrypt(s['persona']['telefono']).decode()

    return sesion

def insert_sesion(datos):
    facilidad_uso = float(datos['get_FacilidadUso'])
    utilidad= float(datos['get_Utilidad'])
    aceptacion_tecnologica = float(datos['get_AceptacionTecnologica'])
    motivacion = float(datos['get_Motivacion'])
    efectividad = float(datos['get_Efectividad'])
    calidad = float(datos['get_calidadContenido'])
    satisfaccion = (facilidad_uso + utilidad + aceptacion_tecnologica + motivacion + efectividad + calidad)/6
    satisfaccion = round(satisfaccion, 1)
    sesion = {
        "_id": uuid.uuid4().hex,
        "persona": {
            "nombre": cipher_suite.encrypt(str(datos['get_nombre']).encode()),
            "apellido": cipher_suite.encrypt(str(datos['get_apellido']).encode()),
            "cedula": cipher_suite.encrypt(str(datos['get_cedula']).encode()),
            "email": cipher_suite.encrypt(str(datos['get_email']).encode()),
            "telefono": cipher_suite.encrypt(str(datos['get_telefono']).encode()),
        },
        "carrera":datos['get_carrera'],
        "fecha":datos['get_fecha'],
        "hora_inicio":datos['get_tiempoInicio'],
        "hora_fin":datos['get_tiempoFin'],
        "duracion":datos['get_duracion'],
        "estadisticas": {
            "facilidad_uso": facilidad_uso,
            "utilidad": utilidad,
            "aceptacion_tecnologica": aceptacion_tecnologica,
            "motivacion": motivacion,
            "efectividad": efectividad,
            "calidad": calidad,
            "satisfaccion": satisfaccion,
            "comentarios": datos['get_comentarios']
        },
        "observacion":""
    }

    db['sesion'].insert_one(sesion)

def get_duracion_fecha(inicio, fin):
    duracion = fin - inicio
    minutos = int(duracion // 60)
    segundos = int(duracion % 60)
    var_inicio = datetime.datetime.fromtimestamp(inicio)
    var_fin = datetime.datetime.fromtimestamp(fin)

    ecuador_tz = pytz.timezone('America/Guayaquil')
    var_inicio = var_inicio.astimezone(ecuador_tz)
    var_fin = var_fin.astimezone(ecuador_tz)

    fecha = var_inicio.strftime('%Y-%m-%d')

    hora_inicio = var_inicio.strftime('%H:%M:%S') 
    hora_fin = var_fin.strftime('%H:%M:%S')

    return duracion, minutos, segundos, fecha, hora_inicio, hora_fin 

def get_respiraciones(index_posturas):
    collection = db['postura']
    respiraciones = []
    # Buscar las posturas que coincidan con los índices
    for index in index_posturas:
        postura = collection.find_one({'index_modelo': index})
        if postura:
            respiraciones.append(postura['respiracion'])

    return respiraciones

def get_index_posturas(id_rutina):
    repeticiones, posturas = get_lista_posturas(id_rutina)
    index_posturas = []
    for postura in posturas:
        index_posturas.append(postura['index_modelo'])

    return repeticiones, index_posturas

def get_lista_posturas(id_rutina):
    id_rutina_bson = bson.ObjectId(id_rutina)
    rutina = db['rutina'].find_one({'_id':id_rutina_bson})
    repeticiones = rutina['repeticiones']
    posturas = []
    for id_postura in rutina['posturas']:
        id_postura_bson = bson.ObjectId(id_postura)
        postura = db['postura'].find_one({'_id': id_postura_bson})
        postura.pop('_id', None)
        posturas.append(postura)

    return repeticiones, posturas

def inicializar_modelo():
    modelo_yoga = models.densenet121(pretrained=False)
    modelo_yoga.classifier = nn.Sequential(
        nn.Linear(modelo_yoga.classifier.in_features, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Linear(256, 9)
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    modelo_path = os.path.join(script_dir, '..', 'models', 'DN121_v2.pth')
    print("UBICACION MODELO ", modelo_path)
    modelo_yoga = modelo_yoga.to(device)
    
    modelo_yoga.load_state_dict(torch.load(modelo_path))
    modelo_yoga.eval()

    return modelo_yoga

def get_posturas_rutina(modelo_yoga, app_socket, index_posturas, repeticiones):
    camera = cv2.VideoCapture(1)
    index_posturas_cont = 0
    repeticiones_cont = 0
    lista_respiraciones = get_respiraciones(index_posturas)
    last_prediction_time = time.time()
    app_socket.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
            img_pil = Image.fromarray(color_frame)
            img_processed = transform(img_pil).unsqueeze(0).to(device)
            current_time = time.time()
            # Verificar cada segundo
            if current_time - last_prediction_time >= 1:

                with torch.no_grad():
                    output = modelo_yoga(img_processed)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                # Calcula la precisión
                precision = round(probabilities[index_posturas[index_posturas_cont]].item() * 100, 2)
                if (index_posturas[index_posturas_cont] == 2):
                    precision = precision * 5
                if precision >= 10:
                    
                    controlar_respiraciones(app_socket, index_posturas_cont, lista_respiraciones)
                    index_posturas_cont += 1
                    if index_posturas_cont >= len(index_posturas):
                        repeticiones_cont+=1

                        if(repeticiones_cont >= repeticiones):
                            # Redirige a otra página al finalizar la rutina
                            app_socket.emit('redireccion', {'ruta': '/practicar/feedback'})
                            break
                        else:
                            index_posturas_cont = 0
                            app_socket.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
                    else:
                        # Cambia la imagen de referencia en el HTML
                        app_socket.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})

                # Envia la precisión al cliente
                app_socket.emit('precision_update', {'precision': precision})

                # Actualiza el tiempo de la última predicción
                last_prediction_time = current_time

            # Convierte la matriz de valores de píxeles nuevamente a una imagen para mostrarla en el navegador
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Muestra el video como secuencia de imágenes

def controlar_respiraciones(app_socket, index_posturas_cont, lista_respiracion):
    inhala = lista_respiracion[index_posturas_cont]['inhalar']
    retiene = lista_respiracion[index_posturas_cont]['retener']
    exhala = lista_respiracion[index_posturas_cont]['exhalar']

    app_socket.emit('pop_up', {
        'inhalar': inhala,
        'retener': retiene,
        'exhalar': exhala
    })
    time.sleep(inhala + retiene + exhala + 4)

def cont_landmarks(results):
    cont_landmarks_aux = 0
    for landmark in results:
        if landmark.visibility > 0.9:
            cont_landmarks_aux +=1
    return cont_landmarks_aux

def get_calibracion_rutina(app_socket):
    camera = cv2.VideoCapture(1)
    camera.set(3, 720)
    camera.set(4, 720)
    mpDraw = mp.solutions.drawing_utils
    my_pose = mp.solutions.pose
    pose = my_pose.Pose()
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(imgRGB)
            # print(result.pose_landmarks)
            if result.pose_landmarks:
                res_cont = cont_landmarks(result.pose_landmarks.landmark)
                # print(res_cont)
                if(res_cont == 17):
                    app_socket.emit('redireccion', {'ruta': '/practicar/rutina'})
                    break
                # else:
                #     app_socket.emit('calibrar', {'mensaje': 'Incorrecto'})
                #     # break
                mpDraw.draw_landmarks(frame, result.pose_landmarks, my_pose.POSE_CONNECTIONS)
            ret, buffer = cv2.imencode('.png', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')  # Muestra el video como secuencia de imágenes

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

