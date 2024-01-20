import time

from decouple import config
from flask import redirect, url_for, render_template, jsonify, Response, request, session
from flask_socketio import SocketIO
from app import app
from db import db
from routes.sesion import insert_sesion
from routes.control import get_posturas_rutina, get_calibracion_rutina, get_lista_posturas, get_index_posturas, inicializar_modelo, get_duracion_fecha

app_socket = SocketIO(app)
app.secret_key = str(config('KEY_SESSION'))

modelo_yoga = inicializar_modelo()

@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return jsonify(e)

@app.route('/practicar/seleccionar')
def seleccionar():
    try:
        rutinas = db['rutina'].find()
        return render_template('seleccionar_rutina.html', rutinas=rutinas)
    except Exception as e:
        print(getattr(e, 'message', repr(e)))

@app.route('/rutina/<id_rutina>', methods=['GET'])
def get_rutina(id_rutina):
    try:
        _, posturas = get_lista_posturas(id_rutina)
        return jsonify(posturas)
    except Exception as e:
        return jsonify(e)

@app.route('/post_rutina', methods=['POST'])
def post_rutina():
    try:
        id_rutina = request.form.get('get_rutina')
        repeticiones, posturas = get_index_posturas(id_rutina)
        session['index_posturas'] = posturas
        session['repeticiones'] = repeticiones
        return render_template('calibrar.html')
    except Exception as e:
        return jsonify(e)

@app.route('/practicar/calibrar')
def calibrar():
    try:
        return render_template('calibrar.html')
    except Exception as e:
        return jsonify(e)

@app.route('/calibrar_posicion')
def calibrar_posicion():
    return Response(get_calibracion_rutina(app_socket), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/practicar/rutina')
def rutina():
    try:
        session['iniciar_rutina'] = time.time()
        return render_template('rutina.html')
    except Exception as e:
        return jsonify(e)
        
@app.route('/practicar_rutina')
def practicar_rutina():
    index_posturas = session.get('index_posturas', None)
    repeticiones = session.get('repeticiones', None)
    return Response(get_posturas_rutina(modelo_yoga, app_socket, index_posturas, repeticiones), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/practicar/feedback')
def feedback():
    try:
        # return render_template('feedback.html')
        iniciar_rutina = session.get('iniciar_rutina', None)
        finalizar_rutina = time.time() 
        _, minutos, segundos, fecha, hora_inicio, hora_fin = get_duracion_fecha(iniciar_rutina, finalizar_rutina)
        return render_template('feedback.html', 
                                tiempo_inicio=hora_inicio,
                                tiempo_fin=hora_fin,
                                minutos = minutos,
                                segundos = segundos,
                                fecha=fecha)
    except Exception as e:
        return jsonify(e)

@app.route('/guardar_sesion', methods=['POST'])
def guardar_sesion():
    try:

        campos = [
            'get_fecha', 'get_tiempoInicio', 'get_tiempoFin', 'get_duracion',
            'get_nombre', 'get_apellido', 'get_cedula', 'get_email', 'get_telefono',
            'get_facultad', 'get_carrera', 'get_FacilidadUso', 'get_Utilidad',
            'get_AceptacionTecnologica', 'get_Motivacion', 'get_Efectividad',
            'get_Satisfaccion', 'get_comentarios'
        ]
        datos = {campo: request.form.get(campo) for campo in campos}
        insert_sesion(datos)
        # print(datos)
        return redirect(url_for('home'))
    except Exception as e:
        return jsonify(e)