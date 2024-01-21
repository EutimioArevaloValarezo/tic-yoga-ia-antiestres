from flask import jsonify, request, session
from db import db
from passlib.hash import pbkdf2_sha256
from decouple import config


def insert_usuario(data):
    data['contrasenia'] = pbkdf2_sha256.encrypt(data['contrasenia'])
    db['administrador'].insert_one(data)

def get_usuario(usuario):
    usuario = db['administrador'].find_one({"usuario":usuario})
    return usuario