import bson
from decouple import config

from flask import render_template, jsonify, Response, request, session
from flask_socketio import SocketIO

from app import app
from db import db

from routes.control import get_posturas_rutina, get_calibracion_rutina, get_lista_posturas, get_index_posturas

app_socket = SocketIO(app)
app.secret_key = str(config('KEY_SESSION'))


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
        posturas = get_lista_posturas(id_rutina)
        return jsonify(posturas)
    except Exception as e:
        return jsonify(e)

@app.route('/post_rutina', methods=['POST'])
def post_rutina():
    try:
        id_rutina = request.form.get('get_rutina')
        posturas = get_index_posturas(id_rutina)
        session['index_posturas'] = posturas
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
        return render_template('rutina.html')
    except Exception as e:
        return jsonify(e)
        
@app.route('/practicar_rutina')
def practicar_rutina():
    index_posturas = session.get('index_posturas', None)
    print(index_posturas)
    return Response(get_posturas_rutina(app_socket, index_posturas), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/practicar/feedback')
def feedback():
    try:
        return render_template('feedback.html')
    except Exception as e:
        return jsonify(e)