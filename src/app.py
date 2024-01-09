from flask import Flask
# from flask_socketio import SocketIO, emit

# import mediapipe as mp

# import torch
# import torch.nn as nn
# import torchvision.models as models
# import torchvision.transforms as transforms
# import time
# import cv2
# from PIL import Image

app = Flask(__name__)
# socketio = SocketIO(app)

from routes import rutas

if __name__ == '__main__':
    app.run(host='0.0.0.0', 
            port=5000, 
            debug=True)