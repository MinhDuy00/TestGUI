import typing
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton
from PyQt5.QtGui import QPixmap, QBrush, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import QPoint, QRect, QTimer, pyqtSignal, pyqtSlot, Qt, QThread
import time
import sys
import cv2
import numpy as np

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    state_flag = 0

    def run(self):
        camera = cv2.VideoCapture(0)
        # camera.set(cv2.CAP_PROP_FPS,60)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
        while True:
            ret, cv_img = camera.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
                if self.state_flag == 1:
                    time.sleep(1)
    def change_state(self,state):
        self.state_flag = state

class TestRect(QLabel):
    change_frame = pyqtSignal(QPoint,int)
    def __init__(self):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self,event):
        super().paintEvent(event)
        qp = QPainter(self)
        br = QBrush(QColor(100,10,10,40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin,self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.change_frame.emit(self.begin,0)
        print(self.begin)
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self,event):
        self.begin = event.pos()
        self.end = event.pos()
        self.change_frame.emit(self.begin,1)
        self.update

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state_flag = 0

        self.setWindowTitle("Motor Detection")
        self.display_width = 640
        self.display_height = 480
        
        self.gap_x = 0
        self.gap_y = 0
        self.gap_w = 70
        self.gap_h = 305
        
        self.screw_x = 0
        self.screw_y = 0
        self.screw_w = 70
        self.screw_h = 305
        
        self.springs_x = 0
        self.springs_y = 0
        self.springs_w = 70
        self.springs_h = 305
        
        self.terminal_x = 0
        self.terminal_y = 0
        self.terminal_w = 70
        self.terminal_h = 305

        self.pagelayout = QHBoxLayout()
        self.imagelayout = QVBoxLayout()
        self.buttonlayout = QVBoxLayout()
        self.sublayout = QHBoxLayout()

        self.pagelayout.addLayout(self.imagelayout,20)
        self.pagelayout.addLayout(self.buttonlayout,5)

        self.image_frame = TestRect()
        self.image_frame.setFixedSize(self.display_width,self.display_height)
        self.resize(self.display_width,self.display_height)

        self.imagelayout.addWidget(self.image_frame,alignment=QtCore.Qt.AlignCenter)
        self.imagelayout.addLayout(self.sublayout)

        self.cropimg1 = QLabel()
        self.label1 = QLabel()
        self.cropimg2 = QLabel()
        self.label2 = QLabel()
        self.cropimg3 = QLabel()
        self.label3 = QLabel()
        self.cropimg4 = QLabel()
        self.label4 = QLabel()
        self.sublayout.addWidget(self.label1,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.cropimg1,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.label2,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.cropimg2,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.label3,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.cropimg3,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.label4,alignment=QtCore.Qt.AlignCenter)
        self.sublayout.addWidget(self.cropimg4,alignment=QtCore.Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(self.pagelayout)
        self.setCentralWidget(widget)

        btn = QPushButton("START")
        btn.pressed.connect(self.set_state_predict)
        self.buttonlayout.addWidget(btn)
        btn = QPushButton("STOP")
        btn.pressed.connect(self.set_state_getdata)
        self.buttonlayout.addWidget(btn)
        btn = QPushButton("SET DATA FRAME")
        self.buttonlayout.addWidget(btn)
        btn.pressed.connect(self.update_data_frame)


        gaplabel = QLabel("GAP DETECT")
        self.buttonlayout.addWidget(gaplabel,alignment=QtCore.Qt.AlignCenter)
        screwlabel = QLabel("SCREW DETECT")
        self.buttonlayout.addWidget(screwlabel,alignment=QtCore.Qt.AlignCenter)
        springslabel = QLabel("SPRINGS DETECT")
        self.buttonlayout.addWidget(springslabel,alignment=QtCore.Qt.AlignCenter)
        terminallabel = QLabel("TERMINAL DETECT")
        self.buttonlayout.addWidget(terminallabel,alignment=QtCore.Qt.AlignCenter)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.image_frame.change_frame.connect(self.update_frame)
        self.thread.start()
    def set_state_getdata(self):
        self.state_flag = 0
        self.thread.change_state(self.state_flag)
    def set_state_predict(self):
        self.state_flag = 1
        self.thread.change_state(self.state_flag)
    def update_data_frame(self):
        self.label1.setText("STEP 1:")

    @pyqtSlot(np.ndarray)
    def update_image(self,cv_img):
        self.image_frame.setPixmap(self.convert_cv_qt(cv_img).scaled(1280,720))
        gap_img = cv_img[self.gap_y:self.gap_y+self.gap_h,self.gap_x:self.gap_x+self.gap_w]
        screw_img = cv_img[self.screw_x:self.screw_y+self.screw_h,self.screw_x:self.screw_x+self.screw_w]
        springs_img = cv_img[self.springs_y:self.springs_y+self.springs_h,self.springs_x:self.springs_x+self.springs_w]
        terminal_img = cv_img[self.gap_y:self.gap_y+self.gap_h,self.gap_x:self.gap_x+self.gap_w]
        print(self.gap_x)
        self.cropimg1.setPixmap(self.convert_cv_qt(gap_img).scaled(100,100))
        self.cropimg2.setPixmap(self.convert_cv_qt(screw_img).scaled(100,100))
        self.cropimg3.setPixmap(self.convert_cv_qt(springs_img).scaled(100,100))
        self.cropimg4.setPixmap(self.convert_cv_qt(terminal_img).scaled(100,100))

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format
        return QPixmap.fromImage(p)
    @pyqtSlot(QPoint,int)
    def update_frame(self,position, flag):
        if flag == 0: 
            if self.label1.text() == "STEP 1:":
                self.gap_x = position.x()
                self.gap_y = position.y()
            elif self.label2.text() == "STEP 2:":
                self.screw_x = position.x()
                self.screw_y = position.y()
            elif self.label3.text() == "STEP 3:":
                self.springs_x = position.x()
                self.springs_y = position.y()
        elif flag == 1:
            if self.label1.text() == "STEP 1:":
                self.gap_h = position.x() - self.gap_x
                self.gap_w = position.y() - self.gap_y
                self.label1.setText("")
                self.label2.setText("STEP 2:")
            elif self.label2.text() == "STEP 2:":
                self.screw_h = position.x() - self.screw_x
                self.screw_w = position.y() - self.screw_y
                self.label2.setText("")
                self.label3.setText("STEP 3:")
            elif self.label3.text() == "STEP 3:":
                self.springs_h = position.x() - self.springs_x
                self.springs_w = position.y() - self.springs_y
                self.label3.setText("")
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = MainWindow()
    a.show()
    sys.exit(app.exec_())