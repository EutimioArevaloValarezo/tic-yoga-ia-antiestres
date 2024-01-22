import time
import uuid

from decouple import config
from flask import redirect, url_for, render_template, jsonify, Response, request, session
from flask_socketio import SocketIO
from functools import wraps
from app import app
from db import db
from passlib.hash import pbkdf2_sha256

from routes.control import inicializar_modelo, get_lista_posturas, get_index_posturas, get_calibracion_rutina, get_posturas_rutina, get_duracion_fecha, insert_sesion,insert_usuario, get_usuario, get_sesiones, generar_grafico_estadisticas

app_socket = SocketIO(app)
app.secret_key = str(config('KEY_SESSION')).encode()
modelo_yoga = inicializar_modelo()

def requerir_logeo(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logeado' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    
    return wrap

@app.route('/')
def home():
    iniciar_rutina = session.get('logeado', None)
    if iniciar_rutina is None:
        session.clear()
    return render_template('home.html')


@app.route('/practicar/seleccionar')
def seleccionar():
    rutinas = db['rutina'].find()
    return render_template('seleccionar_rutina.html', rutinas=rutinas)

@app.route('/rutina/<id_rutina>', methods=['GET'])
def get_rutina(id_rutina):
    _, posturas = get_lista_posturas(id_rutina)
    return jsonify(posturas)


@app.route('/post_rutina', methods=['POST'])
def post_rutina():
    id_rutina = request.form.get('get_rutina')
    repeticiones, posturas = get_index_posturas(id_rutina)
    session['index_posturas'] = posturas
    session['repeticiones'] = repeticiones
    return render_template('calibrar.html')


@app.route('/practicar/calibrar')
def calibrar():
    return render_template('calibrar.html')

@app.route('/calibrar_posicion')
def calibrar_posicion():
    return Response(get_calibracion_rutina(app_socket), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/practicar/rutina')
def rutina():
    session['iniciar_rutina'] = time.time()
    return render_template('rutina.html')
        
@app.route('/practicar_rutina')
def practicar_rutina():
    index_posturas = session.get('index_posturas', None)
    repeticiones = session.get('repeticiones', None)
    return Response(get_posturas_rutina(modelo_yoga, app_socket, index_posturas, repeticiones), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/practicar/feedback')
def feedback():
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


@app.route('/guardar_sesion', methods=['POST'])
def guardar_sesion():
    campos = [
        'get_fecha', 'get_tiempoInicio', 'get_tiempoFin', 'get_duracion',
        'get_nombre', 'get_apellido', 'get_cedula', 'get_email', 'get_telefono',
        'get_facultad', 'get_carrera', 'get_FacilidadUso', 'get_Utilidad',
        'get_AceptacionTecnologica', 'get_Motivacion', 'get_Efectividad',
        'get_calidadContenido', 'get_comentarios'
    ]
    datos = {campo: request.form.get(campo) for campo in campos}
    insert_sesion(datos)
    return redirect(url_for('home'))

    
@app.route('/iniciar_sesion')
def iniciar_sesion():
    usuario = db['administrador']
    # Verificar si la colección está vacía
    if usuario.count_documents({}) == 0:

        data = {
            '_id': uuid.uuid4().hex,
            'nombre': 'Eutimio',
            'apellido': 'Arévalo',
            'usuario':config('INIT_USUARIO'),
            'contrasenia':config('INIT_PASS')
        }
        insert_usuario(data)
    return render_template('admin/login.html')

    
@app.route('/iniciar_sesion_usuario', methods=['POST'])
def iniciar_sesion_usuario():
    usuario = request.form.get('get_usuario')
    contrasenia = request.form.get('get_contrasenia')
    administrador = get_usuario(usuario)
    if administrador and pbkdf2_sha256.verify(contrasenia, administrador['contrasenia']):
        session['logeado'] = True
        session['user'] = administrador
        return jsonify(administrador), 200
    else:
        return jsonify({ 'error': 'Credenciales incorrectas' }), 401
    
@app.route('/editar_administrador', methods=['POST'])
def editar_administrador():
    switch = request.form.get('get_switch')
    nombre = request.form.get('get_nombre')
    apellido = request.form.get('get_apellido')
    usuario = request.form.get('get_usuario')
    user = session.get('user', None)

    if(switch):
        pass_actual = request.form.get('get_contrasenia_actual')
        pass_nueva = request.form.get('get_contrasenia_nueva')
        if pbkdf2_sha256.verify(pass_actual, user['contrasenia']):
            pass_nueva = pbkdf2_sha256.encrypt(pass_nueva)
            db['administrador'].update_one({'_id': user['_id']}, {'$set': {'contrasenia': pass_nueva}})
            return jsonify({ 'success': 'Se ha actualizado los datos y la contraseña correctamente' }), 200
        else:
            return jsonify({ 'error': 'No se ha podido actualizar la contraseña, verifica la información' }), 401
    else:
        res = db['administrador'].update_one({'_id': user['_id']}, {'$set': {'nombre': nombre, 'apellido': apellido, 'usuario': usuario}})
        if res:
            return jsonify({ 'success': 'Se han actualizado los datos correctamente' }), 200
        return jsonify({ 'error': 'No se han podido actualizar los datos' }), 401

@app.route('/cerrar_sesion_usuario')
def cerrar_sesion_usuario():
    session.clear()
    return redirect('/')

@app.route('/admin/editar_usuario')
@requerir_logeo
def editar_usuario():
    return render_template('admin/editar_usuario.html')

@app.route('/admin/gestionar_administradores')
@requerir_logeo
def gestionar_administradores():
    administradores = db['administrador'].find()
    return render_template('admin/gestionar_administradores.html', administradores=administradores)

@app.route('/get_administrador', methods=['POST'])
def get_administrador():
    id_admin = request.form.get('id_admin')
    admin = db['administrador'].find_one({ '_id':id_admin })
    if admin:
        return jsonify({'usuario': admin['usuario']})
    else:
        return jsonify({ 'error': 'Error grave' })
    
@app.route('/agregar_administrador', methods=['POST'])
def agregar_administrador():
    nombre = request.form.get('get_nombre')
    apellido = request.form.get('get_apellido')
    usuario = request.form.get('get_usuario')
    contrasenia = config('INIT_PASS')

    administrador = {
        "_id": uuid.uuid4().hex,
        "nombre": nombre,
        "apellido": apellido,
        "usuario": usuario,
        "contrasenia": pbkdf2_sha256.encrypt(contrasenia)
    }

    if db['administrador'].find_one({ 'usuario': usuario }):
        return jsonify({ 'error': 'Ya existe un usuario con este nombre' }), 400
    
    if db['administrador'].insert_one(administrador):
        return jsonify({'success': 'Se ha creado correctamente el usuario :'+str(usuario)}), 200

    return jsonify({ 'error': 'Se produjo un error' }), 400

@app.route('/eliminar_administrador', methods=['POST'])
def eliminar_administrador():
    id_admin = request.form.get('name_eliminar_admin')
    admin = db['administrador'].find_one({ '_id':id_admin })
    aux_admin = session.get('user', None)
    if admin['usuario'] == aux_admin['usuario']:
        session.clear()
        db['administrador'].delete_one(admin)
        return redirect('/')
    
    db['administrador'].delete_one(admin)

    return redirect(url_for('gestionar_administradores'))
    
@app.route('/resetear_contrasenia_administrador', methods=['POST'])
def resetear_contrasenia_administrador():
    id_admin = request.form.get('name_resetear_pass')
    admin = db['administrador'].find_one({ '_id':id_admin })
    aux_admin = session.get('user', None)
    new_contrasenia = config('INIT_PASS')
    new_contrasenia = pbkdf2_sha256.encrypt(new_contrasenia)
    if admin['usuario'] == aux_admin['usuario']:
        db['administrador'].update_one({'_id': admin['_id']}, {'$set': {'contrasenia': new_contrasenia}})
        admin = db['administrador'].find_one({ '_id': aux_admin['_id'] })
        session['user'] = admin
        return redirect(url_for('gestionar_administradores'))

    db['administrador'].update_one({'_id': admin['_id']}, {'$set': {'contrasenia': new_contrasenia}})
    return redirect(url_for('gestionar_administradores'))


@app.route('/admin/ver_sesiones')
@requerir_logeo
def ver_sesiones():
    sesiones = get_sesiones()
    return render_template('admin/ver_sesiones.html', sesiones=sesiones)


@app.route('/get_observacion', methods=['POST'])
def get_observacion():
    idObservacion = request.form.get('idObservacion')
    resultado = db['sesion'].find_one({'_id': idObservacion})
    if resultado:
        return jsonify({'text_observacion': resultado['observacion']})
    else:
        return jsonify({ 'error': 'Error grave' })
    
@app.route('/editar_observacion', methods=['POST'])
def editar_observacion():
    idObservacion = request.form.get('idObservacion')
    observacion = request.form.get('nameObsTextArea')
    resultado = db['sesion'].update_one({'_id': idObservacion}, {'$set': {'observacion': observacion}})
    if observacion:
        return jsonify({'success': 'Se guardo correctamente'})
    else:
        return jsonify({ 'error': 'Error grave' })

@app.route('/ver_estadistica')
def ver_estadistica():
    return render_template('admin/estadistica.html')

@app.route('/generar_estaditica', methods=['POST'])
def generar_estaditica():
    id_pymongo = request.form.get('id_pymongo')
    resultado = db['sesion'].find_one({'_id': id_pymongo})
    if generar_grafico_estadisticas(resultado['estadisticas']):
        return jsonify({'ruta_imagen': '../static/images/estadistica/grafico.png'})
    else:
        return jsonify({ 'error': 'Error grave' })

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('error/500.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('error/500.html'), 500
