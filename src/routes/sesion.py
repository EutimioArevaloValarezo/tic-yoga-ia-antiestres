from db import db
import bson

def insert_sesion(datos):
    sesion = {
        "persona": {
            "nombre": datos['get_nombre'],
            "apellido": datos['get_apellido'],
            "cedula": datos['get_cedula'],
            "email": datos['get_email'],
            "telefono": datos['get_telefono'],
        },
        "carrera":datos['get_carrera'],
        "fecha":datos['get_fecha'],
        "hora_inicio":datos['get_tiempoInicio'],
        "hora_fin":datos['get_tiempoFin'],
        "duracion":datos['get_duracion'],
        "estadisticas": {
            "facilidad_uso": datos['get_FacilidadUso'],
            "utilidad": datos['get_Utilidad'],
            "aceptacion_tecnologica": datos['get_AceptacionTecnologica'],
            "motivacion": datos['get_Motivacion'],
            "efectividad":datos['get_Efectividad'],
            "satisfaccion":datos['get_Satisfaccion'],
            "comentarios":datos['get_comentarios']
        }
    }

    db['sesion'].insert_one(sesion)