# -*- coding: utf-8 -*-
import sys
import cv2
import time
import numpy as np
import threading
import socket
import json
from PIL import ImageGrab

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class Client(QMainWindow):
    def __init__(self):
        super(Client, self).__init__()
        self.FPS = 30
        self.send_FPS = 100
        # get screen resolution
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        width = self.screenRect.width()
        height = self.screenRect.height()

        self.ip = '127.0.0.1'
        self.keybord_port = 23333
        self.mouse_port = 23332
        self.vision_port = 23331
        self.keybord_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vision_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vision_socket.bind((self.ip, self.vision_port))

        self.mouse_dict = {
            'move':[],
            'press':[],
            'release':[],
            'wheel':[],
        }
        self.keyboard_dict = {
            'press': [],
            'release': [],
        }
        self.cmd_dict = {
            'width':0,
            'height':0,
        }
        
        self.setMouseTracking(True)
        # create GUI
        self.init_ui(width, height)
        # start to get screen image
        self.img_thread = threading.Thread(target=self.get_img, args=())
        self.img_thread.start()
        self.send_thread = threading.Thread(target=self.send, args=())
        self.send_thread.start()
        
    def encode_message(self, dict):
        data = json.dumps(dict).encode()
        return data

    def send(self):
        while True:
            if len(self.keyboard_dict['press']) > 0 or len(self.keyboard_dict['release']) > 0:
                message = self.encode_message(self.keyboard_dict)
                self.keybord_socket.sendto(message, (self.ip, self.keybord_port))

            if len(self.mouse_dict['press']) > 0 or len(self.mouse_dict['release']) > 0 or len(self.mouse_dict['wheel']) > 0:
                message = self.encode_message(self.mouse_dict)
                self.mouse_socket.sendto(message, (self.ip, self.mouse_port))

            self.mouse_dict = {
                'move':[],
                'press':[],
                'release':[],
                'wheel':[],
            }

            self.keyboard_dict = {
                'press': [],
                'release': [],
            }

            if self.cmd_dict['width'] > 0 and self.cmd_dict['height'] > 0:
                print(self.cmd_dict)

            self.cmd_dict = {
                'width':0,
                'height':0,
            }
            time.sleep(1./self.send_FPS)

    def get_img(self):
        while True:
            """
            self.raw_img = ImageGrab.grab()
            self.resize_img = self.raw_img.resize((self.width(),self.height()))
            self.img = np.array(self.resize_img)
            """
            
            data, addr = self.vision_socket.recvfrom(65535)
            data = np.frombuffer(data, dtype=np.uint8)
            self.img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.pm = self.cvimg_to_pixmap(self.img)
            try:
                self.label.setPixmap(self.pm)
            except:
                pass
            time.sleep(1/self.FPS)
            
    def init_ui(self, width, height):
        self.resize(width//2, height//2)
        self.setWindowTitle('Clairvoyance')
        self.label=QLabel(self)
        self.label.setScaledContents(True)
        self.label.setMouseTracking(True)
        
    def resizeEvent(self, event):
        self.label.resize(self.width(),self.height())
        self.cmd_dict['width'] = self.width()
        self.cmd_dict['height'] = self.height()
    
    def wheelEvent(self, event):
        data = event.angleDelta().y()/120.
        self.mouse_dict['wheel'].append(data)

    def mouseMoveEvent(self, event):
        s = event.windowPos()
        self.mouse_dict['move'].append([s.x(), s.y()])

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            cmd = 'l'
        elif e.button() == Qt.RightButton:
            cmd = 'r'
        elif e.button() == Qt.MiddleButton:
            cmd = 'm'
        elif e.button() == Qt.ForwardButton:
            cmd = 'f'
        elif e.button() == Qt.BackButton:
            cmd = 'b'
        else:
            print('Unknow press')
            cmd = 'u'
        self.mouse_dict['press'].append([cmd, e.pos().x(), e.pos().y()])
        
 
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            cmd = 'l'
        elif e.button() == Qt.RightButton:
            cmd = 'r'
        elif e.button() == Qt.MiddleButton:
            cmd = 'm'
        elif e.button() == Qt.ForwardButton:
            cmd = 'f'
        elif e.button() == Qt.BackButton:
            cmd = 'b'
        else:
            print('Unknow release')
            cmd = 'u'
        self.mouse_dict['release'].append([cmd, e.pos().x(), e.pos().y()])
        
    def keyPressEvent(self, event):
        key = event.key()
        self.keyboard_dict['press'].append(key)
        
    #https://docs.godotengine.org/en/stable/classes/class_@globalscope.html
    def keyReleaseEvent(self, event):
        key = event.key()
        self.keyboard_dict['release'].append(key)

    def cvimg_to_pixmap(self, cvimg):
        height, width, depth = cvimg.shape
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        qimg = QImage(cvimg.data, cvimg.shape[1], cvimg.shape[0], cvimg.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        return pixmap

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Client()
    w.show()
    sys.exit(app.exec_())