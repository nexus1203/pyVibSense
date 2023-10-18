import socket
import struct
import numpy as np
from .signals import Signals
from PyQt5.QtCore import QThread, pyqtSignal

DATA_PORT = 5255
HEADER = b"DATA_START"
FOOTER = b"DATA_END"
SAMPLES_PER_PACKET = 375
EXPECTED_SIZE = SAMPLES_PER_PACKET * 3 * 4  # 3 floats for each SAMPLE, 4 bytes per float

SAMPLE_RATE = 3000


class OmniVibSense(QThread):
    signal = Signals()

    def __init__(self, parent=None):
        super(OmniVibSense, self).__init__(parent)

        self.buffer = bytearray()

        self.data = np.zeros((3, SAMPLE_RATE))  # 2D array
        self.current_sample_idx = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', DATA_PORT))

    def run(self):
        self.threadactive = True

        while self.threadactive:
            data, _ = self.socket.recvfrom(4096 //
                                           2)  # Adjust buffer size if needed
            # print(len(data))
            if data == HEADER:
                self.buffer = bytearray()
            elif data == FOOTER:
                self.process_data()
            else:
                self.buffer.extend(data)

    def process_data(self):

        if len(self.buffer) != EXPECTED_SIZE:
            print(
                f"Unexpected data size. Expected {EXPECTED_SIZE} bytes, but received {len(self.buffer)} bytes."
            )
            return

        format_string = f'{3*SAMPLES_PER_PACKET}f'
        acc_data_array = np.array(struct.unpack(format_string, self.buffer))

        # Reshape the data to get three rows where each row represents an axis (X, Y, Z)
        acc_data_reshaped = acc_data_array.reshape(SAMPLES_PER_PACKET, 3).T

        # Add data to our data array
        next_sample_idx = self.current_sample_idx + SAMPLES_PER_PACKET
        self.data[:,
                  self.current_sample_idx:next_sample_idx] = acc_data_reshaped

        # Update the current sample index
        self.current_sample_idx = next_sample_idx

        # Check if we reached the sample rate (3000 samples)
        if self.current_sample_idx >= SAMPLE_RATE:
            self.signal.data.emit(self.data)
            # Reset the sample index
            self.current_sample_idx = 0
            print("3000 samples received")

        # Clear the buffer
        self.buffer = bytearray()

    def stop_thread(self):
        self.threadactive = False
        self.socket.close()
        self.quit()
        self.terminate()
