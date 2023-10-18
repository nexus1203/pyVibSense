import os
import sys
import json
from datetime import datetime, timedelta
from time import perf_counter as pc
from datetime import datetime
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QEvent,
                          QMetaObject, QObject, QPoint, QPropertyAnimation,
                          QRect, QSize, Qt, QThread, QTime, QTimer, QUrl)
from PyQt5.QtWidgets import (QApplication, QFileDialog, QInputDialog, QLabel,
                             QLineEdit, QMainWindow, QMessageBox, QWidget)
from PyQt5.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import QPointF
import pyqtgraph as pg
from userinterface import Ui_MainWindow

from workers.wireless_worker import OmniVibSense
from scipy.signal import medfilt

SAMPLE_RATE = 3000


def safe_text_to_float(text):
    try:
        return float(text)
    except ValueError:
        return 1.001


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        label_style_w = {'color': '	#FFFFFF', 'font-size': '12pt'}
        # close event
        self.ui.closeEvent = self.closeEvent
        '''status bar setup'''
        self.status_bar_init()
        self.start_clock()
        """checked items"""
        self.checked_list = ['a0', 'a1', 'a2']
        self.ui.checkBox_a0.stateChanged.connect(self.check_box1)
        self.ui.checkBox_a1.stateChanged.connect(self.check_box2)
        self.ui.checkBox_a2.stateChanged.connect(self.check_box3)
        """max buffer default value"""
        self.ui.lineEdit_maxbuffer.setText('3.0')

        # start button
        self.start_acquisition = False
        self.display_buffer = None
        self.calibrate_buffer = None
        self.calibrate = False
        self.cal_x = 0
        self.cal_y = 0
        self.cal_z = 0
        self.load_calibration()

        self.ui.but_calibrate.clicked.connect(self.calibration)
        self.ui.but_calibrate_reset.clicked.connect(
            lambda: (setattr(self, 'cal_x', 0), setattr(self, 'cal_y', 0),
                     setattr(self, 'cal_z', 0), self.save_calibration())[
                         -1]  # Return the result of the last expression
        )
        self.ui.but_start.clicked.connect(self.start_graph)
        self.ui.but_stop.clicked.connect(self.stop_graph)
        self.ui.but_reset.clicked.connect(self.reset_graph)
        self.ui.but_load.clicked.connect(self.load_graph)
        self.ui.but_saveas.clicked.connect(self.save_data)
        """start worker"""
        self.start_worker()
        self.reset_graph()

    def load_calibration(self, ):
        try:
            with open("settings/calibration.json") as f:
                data = json.load(f)
                self.cal_x = data['x']
                self.cal_y = data['y']
                self.cal_z = data['z']
        except Exception as e:
            print(e)
            print(
                "No calibration file found. Using default calibration values.")

    def save_calibration(self, ):
        try:
            with open("settings/calibration.json", 'w') as f:
                data = {'x': self.cal_x, 'y': self.cal_y, 'z': self.cal_z}
                json.dump(data, f)
                print("Calibration file saved with new values.")
                print(f"X: {self.cal_x}, Y: {self.cal_y}, Z: {self.cal_z}")
        except Exception as e:
            print(e)
            print("Error saving calibration file.")

    def start_worker(self, ):
        self.vibration_reader = OmniVibSense()
        self.vibration_reader.start()
        self.vibration_reader.signal.data.connect(self.update_data)

    def graph_set(self, ):
        self.display_length = safe_text_to_float(
            self.ui.lineEdit_maxbuffer.text())
        self.display_buffer = np.zeros(
            (3, int(self.display_length * SAMPLE_RATE)))
        self.x_axis = np.linspace(0, self.display_length,
                                  int(self.display_length * SAMPLE_RATE))

    def calibration(self, ):
        self.calibrate = True

    def start_graph(self, ):
        self.start_acquisition = True

    def stop_graph(self, ):
        self.start_acquisition = False

    def save_data(self, ):
        date_now = datetime.now().strftime("%Y%m%d___%H_%M_%S")
        filename = QFileDialog.getSaveFileName(
            self, 'Save File', '_data/' + date_now + '.csv',
            "CSV files (*.csv)")
        try:
            if filename[0] != '':
                np.savetxt(filename[0],
                           self.display_buffer.T,
                           delimiter=',',
                           header='a0, a1, a2')
        except Exception as e:
            print(e)

    def load_graph(self, ):
        # load file
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '',
                                                "CSV files (*.csv)")
        data = np.loadtxt(file_name[0], delimiter=',', skiprows=1)
        x_axis = np.linspace(0, len(data[:, 0]) / SAMPLE_RATE, len(data[:, 0]))
        self.a0_plot.setData(x_axis, data[:, 0])
        self.a1_plot.setData(x_axis, data[:, 1])
        self.a2_plot.setData(x_axis, data[:, 2])

    def reset_graph(self, ):
        self.start_acquisition = False
        self.ui.graphicsView_a0.clear()
        self.ui.graphicsView_a1.clear()
        self.ui.graphicsView_a2.clear()
        self.configure_graph()
        self.graph_set()

    def configure_graph(self, ):
        self.a0_plot = pg.PlotDataItem(pen=pg.mkPen(color=(255, 255, 255),
                                                    width=2),
                                       name='a0')
        self.a1_plot = pg.PlotDataItem(pen=pg.mkPen(color=(255, 255, 255),
                                                    width=2),
                                       name='a1')
        self.a2_plot = pg.PlotDataItem(pen=pg.mkPen(color=(255, 255, 255),
                                                    width=2),
                                       name='a2')
        self.ui.graphicsView_a0.addItem(self.a0_plot)
        self.ui.graphicsView_a1.addItem(self.a1_plot)
        self.ui.graphicsView_a2.addItem(self.a2_plot)

    def update_data(self, data):
        print(data.shape)  # data shape = (3, 3000)
        # apply median filter to each axis
        data[0, :] = medfilt(data[0, :], 5)
        data[1, :] = medfilt(data[1, :], 5)
        data[2, :] = medfilt(data[2, :], 5)
        # insert the new data into the buffer and remove the oldest data
        shape = data.shape
        if self.start_acquisition:
            data[0, :] = data[0, :] - self.cal_x
            data[1, :] = data[1, :] - self.cal_y
            data[2, :] = data[2, :] - self.cal_z
            self.display_buffer = np.roll(self.display_buffer,
                                          -shape[1],
                                          axis=1)
            self.display_buffer[:, -shape[1]:] = data
            self.update_graph()

        elif self.calibrate:
            self.cal_x = np.mean(data[0, :])
            self.cal_y = np.mean(data[1, :])
            self.cal_z = np.mean(data[2, :])
            self.save_calibration()
            print("Calibration complete.")
            print(f"X: {self.cal_x}, Y: {self.cal_y}, Z: {self.cal_z}")
            self.calibrate = False

    def update_graph(self, ):
        if 'a0' in self.checked_list:
            self.a0_plot.setData(self.x_axis, self.display_buffer[0, :])
        if 'a1' in self.checked_list:
            self.a1_plot.setData(self.x_axis, self.display_buffer[1, :])
        if 'a2' in self.checked_list:
            self.a2_plot.setData(self.x_axis, self.display_buffer[2, :])

        # auto range
        self.ui.graphicsView_a0.enableAutoRange(axis='y')
        self.ui.graphicsView_a1.enableAutoRange(axis='y')
        self.ui.graphicsView_a2.enableAutoRange(axis='y')

    def check_box1(self, state):
        if state == Qt.Checked:
            self.checked_list.append('a0')
        else:
            self.checked_list.remove('a0')

    def check_box2(self, state):
        if state == Qt.Checked:
            self.checked_list.append('a1')
        else:
            self.checked_list.remove('a1')

    def check_box3(self, state):
        if state == Qt.Checked:
            self.checked_list.append('a2')
        else:
            self.checked_list.remove('a2')

    def status_bar_init(self, ):
        # creating a label widget
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(100)

        #add time here
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_display = QLabel('Time: {}'.format(time_now))
        self.date_display.setFont(font)
        # setting up the border

        self.date_display.setStyleSheet(
            "border :1px solid rgb(120,120,120); color: rgb(220, 220, 220);")
        # adding label to status bar
        self.ui.statusbar.addWidget(self.date_display)

    def start_clock(self, ):
        # for date and time display
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_time)
        self.timer.start(1000)

    def show_time(self, ):
        time_now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.date_display.setText('Time: {}'.format(time_now))

    def closeEvent(self, event):
        print("Exiting the UI now")
        try:
            self.vibration_reader.stop_thread()
        except Exception as e:
            print(e)

        sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())