# -*- coding: utf-8 -*-
import sys
import cv2
import time
import numpy as np
import threading
from PIL import ImageGrab

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    
class Client(QMainWindow):
    def __init__(self):
        super(Client, self).__init__()
        self.FPS = 30
        # get screen resolution
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        width = self.screenRect.width()
        height = self.screenRect.height()
        
        self.setMouseTracking(True)
        # create GUI
        self.init_ui(width, height)
        # start to get screen image
        self.img_thread = threading.Thread(target=self.get_img, args=())
        self.img_thread.start()
        
    def get_img(self):
        while True:
            self.raw_img = ImageGrab.grab()
            self.resize_img = self.raw_img.resize((self.width(),self.height()))
            self.img = np.array(self.resize_img)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.pm = self.cvimg_to_pixmap(self.img)
            self.label.setPixmap(self.pm)
            time.sleep(1/self.FPS)
            
    def init_ui(self, width, height):
        self.resize(width//2, height//2)
        self.setWindowTitle('Clairvoyance')
        self.label=QLabel(self)
        self.label.setScaledContents(True)
        self.label.setMouseTracking(True)
        
    def resizeEvent(self, event):
        self.label.resize(self.width(),self.height())
        
    def mouseMoveEvent(self, event):
        s = event.windowPos()
        print(s.x(), s.y())
        
    def keyPressEvent(self, event):
        key = event.key()
        print('Press', key)
        if key == Qt.Key_Left:
            print('Left Arrow Pressed')
        
    def keyReleaseEvent(self, event):
        key = event.key()
        print('Release', key)

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