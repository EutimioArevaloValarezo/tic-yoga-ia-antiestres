def inicializar_modelo():
    modelo_yoga = models.densenet121(pretrained=False)
    modelo_yoga.classifier = nn.Sequential(
        nn.Linear(modelo_yoga.classifier.in_features, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Linear(256, 9)
    )

    modelo_yoga = modelo_yoga.to(device)
    modelo_yoga.load_state_dict(torch.load('./models/DN121_v2.pth'))
    modelo_yoga.eval()

    return modelo_yoga


def get_posturas_rutina():
    camera = cv2.VideoCapture(0)  # Accede a la cámara, 0 es la cámara predeterminada
    index_posturas_cont = 0
    last_prediction_time = time.time()
    socketio.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convierte la imagen a escala de grises para simplificar los valores de píxeles
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # color_frame = cv2.cvtColor(gray_frame, cv2.COLOR_BGR)
            img_pil = Image.fromarray(color_frame)
            img_processed = transform(img_pil).unsqueeze(0).to(device)

            # Verifica si ha pasado el tiempo suficiente para realizar una nueva predicción
            current_time = time.time()
            if current_time - last_prediction_time >= 3:
                # Realiza la predicción

                with torch.no_grad():
                    output = modelo_yoga(img_processed)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                    # Calcula la precisión
                    precision = round(probabilities[index_posturas[index_posturas_cont]].item() * 100, 2)
                    if precision > 70 and index_posturas[index_posturas_cont] == output.argmax().item():
                        respiracion(4, 4, 4, 3)
                        index_posturas_cont += 1
                        if index_posturas_cont >= len(index_posturas):
                            # Redirige a otra página al finalizar la rutina
                            socketio.emit('redireccion', {'redireccionar': 'home.html'})
                            break
                            # print("FINALIZADO")
                        else:
                            # Cambia la imagen de referencia en el HTML
                            socketio.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})

                    # Envia la precisión al cliente
                    socketio.emit('precision_update', {'precision': precision})

                # Actualiza el tiempo de la última predicción
                last_prediction_time = current_time

            # Convierte la matriz de valores de píxeles nuevamente a una imagen para mostrarla en el navegador
            ret, buffer = cv2.imencode('.jpg', color_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Muestra el video como secuencia de imágenes


def respiracion(inhala, retiene, exhala, repeticion):
    socketio.emit('pop_up', {
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
    socketio.emit('pose_update', {'pose_index': index_posturas[index_posturas_cont]})
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
                    socketio.emit('redireccion', {'redireccionar': 'home.html'})
                    break
                else:
                    print(index_posturas_cont)
                # Actualiza el tiempo de la última predicción
                last_prediction_time = current_time