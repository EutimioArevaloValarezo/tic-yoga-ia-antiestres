from flask import *
from app import app
from flask_socketio import SocketIO, emit

from PIL import Image

import cv2

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms

import time

def inicializar_modelo(device):
    modelo_yoga = models.densenet121(pretrained=False)
    modelo_yoga.classifier = nn.Sequential(
        nn.Linear(modelo_yoga.classifier.in_features, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Linear(256, 9)
    )

    modelo_yoga = modelo_yoga.to(device)
    modelo_yoga.load_state_dict(torch.load('src/models/DN121_v2.pth'))
    modelo_yoga.eval()
    return modelo_yoga

#posturas
index_posturas = [3, 5]

app_socket = SocketIO(app)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

modelo_yoga = inicializar_modelo(device)

transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])


def get_posturas_rutina(device):
    camera = cv2.VideoCapture(0)  # Accede a la cámara, 0 es la cámara predeterminada
    index_posturas_cont = 0
    last_prediction_time = time.time()
    app_socket.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convierte la imagen a escala de grises para simplificar los valores de píxeles
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(color_frame)
            img_processed = transform(img_pil).unsqueeze(0).to(device)

            # Verifica si ha pasado el tiempo suficiente para realizar una nueva predicción
            current_time = time.time()
            if current_time - last_prediction_time >= 1:
                # Realiza la predicción

                with torch.no_grad():
                    output = modelo_yoga(img_processed)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                    # Calcula la precisión
                    precision = round(probabilities[index_posturas[index_posturas_cont]].item() * 100, 2)
                    if precision > 70 and index_posturas[index_posturas_cont] == output.argmax().item():
                        respiracion(4, 4, 4, 1)
                        index_posturas_cont += 1
                        if index_posturas_cont >= len(index_posturas):
                            # Redirige a otra página al finalizar la rutina
                            app_socket.emit('redireccion', {'redireccionar': 'home.html'})
                            break
                            # print("FINALIZADO")
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


def respiracion(inhala, retiene, exhala, repeticion):
    app_socket.emit('pop_up', {
        'inhalar': inhala,
        'retener': retiene,
        'exhalar': exhala,
        'repeticiones': repeticion
    })
    time.sleep(((inhala + retiene + exhala) * repeticion) + (repeticion * 2))


def get_posturas_rutina2():
    camera = cv2.VideoCapture(0)  # Accede a la cámara, 0 es la cámara predeterminada
    index_posturas_cont = 0
    last_prediction_time = time.time()
    app_socket.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Verifica si ha pasado el tiempo suficiente para realizar una nueva predicción
            current_time = time.time()
            if current_time - last_prediction_time >= 1:

                index_posturas_cont += 1

                if index_posturas_cont >= 10:
                    print("fin")
                    app_socket.emit('redireccion', {'redireccionar': 'home.html'})
                    break
                else:
                    print(index_posturas_cont)
                # Actualiza el tiempo de la última predicción
                last_prediction_time = current_time





@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return e
    
@app.route('/practicar_yoga/rutina')
def practicar_yoga():
    try:
        return render_template('rutina.html')
    except Exception as e:
        return e
    
@app.route('/video_feed')
def video_feed():
    return Response(get_posturas_rutina(device), mimetype='multipart/x-mixed-replace; boundary=frame')