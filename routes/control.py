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



key = 'E5bsJkAn2CYlsdDZepGyi69SHnCT77GQw8EUOiCTUO4='.encode()
cipher_suite = Fernet(key)

def generar_grafico_estadisticas(data):
    estadisticas = {
        "Facilidad de Uso": data['facilidad_uso'],
        "Utilidad Percibida": data['utilidad'],
        "Aceptación Tecnológica": data['aceptacion_tecnologica'],
        "Calidad del Contenido": data['calidad'],
        "Satisfacción General": data['total']
    }
 
    # Definir los colores
    colores = {0: 'red', 1: 'orange', 2: 'yellow', 3: 'lime', 4: 'darkgreen'}

    # Crear la figura y los ejes
    fig, ax = plt.subplots()

    # Crear las barras
    for i, (nombre, valor) in enumerate(estadisticas.items()):
        ax.bar(i, valor, color=colores[int(valor)])

    # Añadir un distintivo a la barra de "Satisfacción General"
    ax.bar(len(estadisticas)-1, estadisticas["Satisfacción General"], color='blue', alpha=0.3)

    # Añadir los nombres
    ax.set_xticks(range(len(estadisticas)))
    ax.set_xticklabels(estadisticas.keys(), rotation=45, horizontalalignment='right')

    # Guardar la figura
    plt.savefig('./static/images/estadistica/grafico.png', bbox_inches="tight")

    # Cerrar la figura
    plt.close(fig)

    return True

def generar_grafico_hamilton(data):
    try:
        datos = {
            "muscular_antes": data['escala_somatica_antes']['muscular'],
            "sentorial_antes": data['escala_somatica_antes']['sentorial'],
            "respiratorio_antes": data['escala_somatica_antes']['respiratorio'],
            "autonomo_antes": data['escala_somatica_antes']['autonomo'],
            "total_antes": data['escala_somatica_antes']['total_antes'],
            "muscular_despues": data['escala_somatica_despues']['muscular'],
            "sentorial_despues": data['escala_somatica_despues']['sentorial'],
            "respiratorio_despues": data['escala_somatica_despues']['respiratorio'],
            "autonomo_despues": data['escala_somatica_despues']['autonomo'],
            "total_despues": data['escala_somatica_despues']['total_despues']
        }
        # Crear listas de datos 'antes' y 'despues'
        antes = [datos[key] for key in datos if 'antes' in key]
        despues = [datos[key] for key in datos if 'despues' in key]

        # Crear etiquetas para el eje x
        labels = [key.split('_')[0] for key in datos if 'antes' in key]

        # Configurar la ubicación de las etiquetas y el ancho de las barras
        x = np.arange(len(labels))
        width = 0.35

        # Crear la figura y los ejes
        fig, ax = plt.subplots()

        # Agregar las barras 'antes' y 'despues' al gráfico
        rects1 = ax.bar(x - width/2, antes, width, label='Antes')
        rects2 = ax.bar(x + width/2, despues, width, label='Despues')

        # Agregar algunas etiquetas de texto, título y leyenda
        ax.set_ylabel('Valores')
        ax.set_title('Comparativa del antes y después de practicar yoga - Escala de Hamilton')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        plt.ylim(0, 16)

        # Guardar la figura
        plt.savefig('./static/images/estadistica/grafico.png', bbox_inches="tight")

        # Cerrar la figura
        plt.close(fig)
        return True
    except Exception as e:
        print(e)
    

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
        s['persona']['edad'] = cipher_suite.decrypt(s['persona']['edad']).decode()
        s['persona']['genero'] = cipher_suite.decrypt(s['persona']['genero']).decode()
        s['persona']['orientacion'] = cipher_suite.decrypt(s['persona']['orientacion']).decode()

    return sesion

def insert_sesion(datos_antes, datos_despues, nombre_rutina):

    animo_antes = float(datos_antes['get_sentimiento_antes'])
    animo_despues =float(datos_despues['get_sentimiento_despues'])

    muscular_antes = float(datos_antes['get_musculares_antes'])
    sensorial_antes = float(datos_antes['get_sensoriales_antes'])
    respiratirio_antes = float(datos_antes['get_respiratorio_antes'])
    autonomo_antes = float(datos_antes['get_autonomos_antes'])
    total_antes = muscular_antes + sensorial_antes + respiratirio_antes + autonomo_antes

    muscular_despues = float(datos_despues['get_musculares_despues'])
    sensorial_despues = float(datos_despues['get_sensoriales_despues'])
    respiratirio_despues = float(datos_despues['get_respiratorio_despues'])
    autonomo_despues = float(datos_despues['get_autonomos_despues'])
    total_despues = muscular_despues + sensorial_despues + respiratirio_despues + autonomo_despues

    facilidad_uso = float(datos_despues['get_FacilidadUso'])
    utilidad= float(datos_despues['get_Utilidad'])
    aceptacion_tecnologica = float(datos_despues['get_AceptacionTecnologica'])
    calidad = float(datos_despues['get_calidadContenido'])
    satisfaccion = round(((facilidad_uso + utilidad + aceptacion_tecnologica + calidad)/4), 1)

    sesion = {
        "_id": uuid.uuid4().hex,
        "persona": {
            "nombre": cipher_suite.encrypt(str(datos_antes['get_nombre']).encode()),
            "apellido": cipher_suite.encrypt(str(datos_antes['get_apellido']).encode()),
            "cedula": cipher_suite.encrypt(str(datos_antes['get_cedula']).encode()),
            "edad": cipher_suite.encrypt(str(datos_antes['get_edad']).encode()),
            "genero": cipher_suite.encrypt(str(datos_antes['get_genero']).encode()),
            "orientacion": cipher_suite.encrypt(str(datos_antes['get_orientacion']).encode()),
        },
        "rutina": nombre_rutina,
        "facultad":datos_antes['get_facultad'],
        "carrera":datos_antes['get_carrera'],
        "fecha":datos_despues['get_fecha'],
        "hora_inicio":datos_despues['get_tiempoInicio'],
        "hora_fin":datos_despues['get_tiempoFin'],
        "duracion":datos_despues['get_duracion'],
        "hamilton":{
            "escala_somatica_antes": {
                "estado_animo": animo_antes,
                "muscular": muscular_antes,
                "sentorial": sensorial_antes,
                "respiratorio": respiratirio_antes,
                "autonomo": autonomo_antes,
                "total_antes": total_antes
            },

            "escala_somatica_despues": {
                "estado_animo": animo_despues,
                "muscular": muscular_despues,
                "sentorial": sensorial_despues,
                "respiratorio": respiratirio_despues,
                "autonomo": autonomo_despues,
                "total_despues": total_despues
            }
        },
        "satisfaccion": {
            "facilidad_uso": facilidad_uso,
            "utilidad": utilidad,
            "aceptacion_tecnologica": aceptacion_tecnologica,
            "calidad": calidad,
            "total": satisfaccion,
            "comentarios": datos_despues['get_comentarios']
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
    # print("HORAAAAAAAAAAAA: ",hora_fin-hora_inicio)

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
    repeticiones, posturas, rutina = get_lista_posturas(id_rutina)
    index_posturas = []
    for postura in posturas:
        index_posturas.append(postura['index_modelo'])

    return repeticiones, index_posturas, rutina

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

    return repeticiones, posturas, rutina

def inicializar_modelo():
    modelo_yoga = models.densenet121(pretrained=False)
    modelo_yoga.classifier = nn.Sequential(
        nn.Linear(modelo_yoga.classifier.in_features, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Linear(256, 9)
    )

    modelo_path = './models/DN121_v2.pth'

    if config('VAR_STATUS') == 'development':
        modelo_yoga = modelo_yoga.to(device)
        modelo_yoga.load_state_dict(torch.load(modelo_path))
    else:
        
        modelo_yoga = modelo_yoga.to(device)
        modelo_yoga.load_state_dict(torch.load(modelo_path, map_location=torch.device(device)))
    
    modelo_yoga.eval()

    return modelo_yoga

def get_posturas_rutina(modelo_yoga, app_socket, index_posturas, repeticiones):
    camera = cv2.VideoCapture(0)
    index_posturas_cont = 0
    repeticiones_cont = 0
    lista_respiraciones = get_respiraciones(index_posturas)
    last_prediction_time = time.time()
    app_socket.emit('pop_up_intrucciones', {'instrucciones': 'Presentacion de instrucciones'})
    time.sleep(10)
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
            if current_time - last_prediction_time >= 2:

                with torch.no_grad():
                    output = modelo_yoga(img_processed)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                # Calcula la precisión
                precision = round(probabilities[index_posturas[index_posturas_cont]].item() * 100, 2)
                if (index_posturas[index_posturas_cont] == 2):
                    precision = precision * 10
                if precision >= 55:
                    
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
                app_socket.emit('precision_update', {'precision': round(precision*1.82, 2)})

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
    camera = cv2.VideoCapture(0)
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
                if(res_cont >= 25):
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

