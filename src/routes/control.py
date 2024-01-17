import cv2
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import time
import bson
import mediapipe as mp

from PIL import Image
from db import db

def get_index_posturas(id_rutina):
    posturas = get_lista_posturas(id_rutina)
    index_posturas = []
    for postura in posturas:
        index_posturas.append(postura['index_modelo'])

    return index_posturas

def get_lista_posturas(id_rutina):
    id_rutina_bson = bson.ObjectId(id_rutina)
    rutina = db['rutina'].find_one({'_id':id_rutina_bson})
    posturas = []
    for id_postura in rutina['posturas']:
        id_postura_bson = bson.ObjectId(id_postura)
        postura = db['postura'].find_one({'_id': id_postura_bson})
        postura.pop('_id', None)
        posturas.append(postura)

    return posturas

def inicializar_modelo():
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

def get_posturas_rutina(app_socket, index_posturas):
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
                        respiracion(app_socket,4, 4, 4, 1)
                        index_posturas_cont += 1
                        if index_posturas_cont >= len(index_posturas):
                            # Redirige a otra página al finalizar la rutina
                            app_socket.emit('redireccion', {'ruta': '/practicar/feedback'})
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


def respiracion(app_socket, inhala, retiene, exhala, repeticion):
    app_socket.emit('pop_up', {
        'inhalar': inhala,
        'retener': retiene,
        'exhalar': exhala,
        'repeticiones': repeticion
    })
    time.sleep(((inhala + retiene + exhala) * repeticion) + (repeticion * 2))

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
                if(res_cont == 33):
                    app_socket.emit('redireccion', {'ruta': '/practicar/rutina'})
                    break
                else:
                    app_socket.emit('calibrar', {'mensaje': 'Incorrecto'})
                    # break
                mpDraw.draw_landmarks(frame, result.pose_landmarks, my_pose.POSE_CONNECTIONS)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Muestra el video como secuencia de imágenes

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

modelo_yoga = inicializar_modelo()

transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])