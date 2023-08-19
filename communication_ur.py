import socket
import struct
import threading
import sys
import time


class communication_thread():
    def __init__(self, ip='192.38.66.226', port='30003'):
        # Whether the program is run in python 2 or not
        self.python_2 = (sys.version_info.major == 2)

        # Creating the socket
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        time_start = time.time()
        self.socket.connect((ip, port))

        # The thread keeps going as long as this variable is true
        self.running = True

        # The data which the thread optains from the ur
        self.data = 0

        # Read the message size
        self.message_size = float('inf')
        self.message_size = self.get_message_size()

        # The thread which keeps receiving data
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)

        # Starting the Thread
        print('UR: Starting communication thread...')
        self.receive_thread.start()

    def receive(self):
        while self.running:
            data = (self.socket.recv(2048))
            data = self.transform_data(data)
            # If no error occurred then update data
            if not data == -4444:
                self.data = data

    def shutdown(self):
        self.running = False
        self.receive_thread.join()
        self.socket.close()

    def get_message_size(self):
        data = (self.socket.recv(2048))
        message_size = int(self.transform_data_point(data, 'message_size'))
        self.data = self.transform_data(data)
        
        return message_size

    def transform_data_point(self, data, data_name):
        DATA_MAP = {'message_size': 0, 'time': 1,
            'q_b': 2,'q_s': 3, 'q_e': 4, 'q_w1': 5, 'q_w2': 6, 'q_w3': 7,
            'b': 32, 's': 33, 'e': 34, 'w1': 35, 'w2': 36, 'w3': 37,
            'v_b': 38, 'v_s': 39, 'v_e': 40, 'v_w1': 41, 'v_w2': 42, 'v_w3': 43,
            'x_actual': 56, 'y_actual': 57, 'z_actual': 58, 'rx_actual': 59, 'ry_actual': 60, 'rz_actual': 61,
            'v_x': 62, 'v_y': 63, 'v_z': 64, 'v_rx': 65, 'v_ry': 66, 'v_rz': 67,
            'f_x': 68, 'f_y': 69, 'f_z': 70, 'f_rx': 71, 'f_ry': 72, 'f_rz': 73,
            'x': 74, 'y': 75, 'z': 76, 'rx': 77, 'ry': 78, 'rz': 79,
            'robot_mode': 95, 'status': 132}

        # There is an exception for message size
        if data_name == 'message_size':
            byte_position = DATA_MAP[data_name]
            data_type = '!i'
            # Message size is only 4 long
            data_size = 4 
        else:
            byte_position = (DATA_MAP[data_name] - 1) * 8 + 4
            data_type = '!d'
            # Message size is an integer
            data_size = 8
        
        # Check that there is data to be read in the position
        if self.message_size < byte_position + data_size:
            return -4444


        data = data[byte_position:byte_position + data_size]

        # Convert the data from \x hex notation to plain hex
        if self.python_2:
            data = data.encode('hex')
        else:
            data = data.hex()

        if len(data) == data_size * 2:
            if self.python_2:
                data = struct.unpack(data_type, data.decode('hex'))[0]
            else:
                data = struct.unpack(data_type, bytes.fromhex(data))[0]
            return data
        else:
            return -4444

    def transform_data(self, data):
        DATA_MAP = {'message_size': 0, 'time': 1,
            'q_b': 2,'q_s': 3, 'q_e': 4, 'q_w1': 5, 'q_w2': 6, 'q_w3': 7,
            'b': 32, 's': 33, 'e': 34, 'w1': 35, 'w2': 36, 'w3': 37,
            'v_b': 38, 'v_s': 39, 'v_e': 40, 'v_w1': 41, 'v_w2': 42, 'v_w3': 43,
            'x_actual': 56, 'y_actual': 57, 'z_actual': 58, 'rx_actual': 59, 'ry_actual': 60, 'rz_actual': 61,
            'v_x': 62, 'v_y': 63, 'v_z': 64, 'v_rx': 65, 'v_ry': 66, 'v_rz': 67,
            'f_x': 68, 'f_y': 69, 'f_z': 70, 'f_rx': 71, 'f_ry': 72, 'f_rz': 73,
            'x': 74, 'y': 75, 'z': 76, 'rx': 77, 'ry': 78, 'rz': 79,
            'robot_mode': 95, 'status': 132}

        data_string = ''
        for data_type in DATA_MAP:
            data_point = self.transform_data_point(data, data_type)
            # Check if an error occurred
            if data_point == -4444:
                continue
            data_string += data_type + ':' + str(data_point) + ';'
        return data_string

    