from PyQt5.QtCore import QObject, pyqtSignal


class Signals(QObject):
    """Define custom signal types"""
    progress = pyqtSignal(int)
    success = pyqtSignal(bool)
    connectOk = pyqtSignal(object)
    data = pyqtSignal(object)
    safety_status = pyqtSignal(float)
