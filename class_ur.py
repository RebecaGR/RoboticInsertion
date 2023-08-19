import time
from math import pi, cos, sin
import numpy as np
import socket
import sys

from communication_ur import communication_thread


class UR:
    def __init__(self, ip=None, port=None):
        # Whether the program is run in python 2 or not
        self.python_2 = (sys.version_info.major == 2)

        # Dictionary containing all the ur data which have been reading
        self.ur_data = {}

        # Connecting socket directly to robot
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # If no ip is provided, then use default
        if ip is None:
            self.ip = '192.38.66.226'
        else:
            self.ip = ip

        # If no port is provided, then use default
        if port is None:
            self.port = '30003'
        else:
            self.port = port

        # Connect to the UR arm
        self.socket.connect((self.ip, self.port))

        # Starting communication script
        self.communication_thread = communication_thread(self.ip, self.port)

        # Make sure that the communication thread have started receiving data
        while len(self.ur_data) == 0:
            self.read()
        
        print('UR: UR is ready.')

    def set_tcp(self, x=0, y=0, z=0, rx=0, ry=0, rz=0):
        self.socket.send((f'set_tcp(p[{x},{y},{z},{rx},{ry},{rz}])\n').encode())
        time.sleep(0.1)

    def get_pose(self):
        self.read()
        # The older version have the position values in a different place
        MESSAGE_SIZE_TO_VERSION = {'3.0': 1044, '3.2': 1060}

        if (self.communication_thread.message_size >=
                MESSAGE_SIZE_TO_VERSION['3.0']):
            x = self.ur_data['x_actual']
            y = self.ur_data['y_actual']
            z = self.ur_data['z_actual']
            rx = self.ur_data['rx_actual']
            ry = self.ur_data['ry_actual']
            rz = self.ur_data['rz_actual']
        else:
            x = self.ur_data['x']
            y = self.ur_data['y']
            z = self.ur_data['z']
            rx = self.ur_data['rx']
            ry = self.ur_data['ry']
            rz = self.ur_data['rz']
        return [x, y, z, rx, ry, rz]

    def get_joints(self):
        self.read()
        b = self.ur_data['b']
        s = self.ur_data['s']
        e = self.ur_data['e']
        w1 = self.ur_data['w1']
        w2 = self.ur_data['w2']
        w3 = self.ur_data['w3']
        return [b, s, e, w1, w2, w3]

    # def move(self, x=None, y=None, z=None, rx=None, ry=None, rz=None, 
    #                b=None, s=None, e=None, w1=None, w2=None, w3=None, 
    #                pose=None, mode='linear', transform=True, relative=False,
    #                acc=0.5, speed=0.1, wait=False):
    #     pose = self.generate_move(x, y, z, rx, ry, rz,
    #                               b, s, e, w1, w2, w3,
    #                               pose, mode, transform, relative)

    #     print(f'move{mode[0]}(p{pose},{acc},{speed})\n')
    #     if mode[0] == 'j':
    #         self.socket.send((f'move{mode[0]}({pose},{acc},{speed})\n').encode())
    #     else:
    #         self.socket.send((f'move{mode[0]}(p{pose},{acc},{speed})\n').encode())
    #     if wait:
    #         self.wait() 

    def move(self, x=None, y=None, z=None, rx=None, ry=None, rz=None, a=1.0, v=0.1):
        self.socket.send((f'movej(p[{x},{y},{z},{rx},{ry},{rz}], a={a}, v={v})' + '\n').encode("utf8"))

    def move_joints(self, b=None, s=None, e=None, w1=None, w2=None, w3=None):
        self.socket.send((f'movej([{b},{s},{e},{w1},{w2},{w3}], a=1.0, v=0.1)' + '\n').encode('utf8'))

    def read(self):
        data = self.communication_thread.data
        # Removing last entry: empty due to fenceposting in sending process
        data_split = data.split(';')[:-1]
        for item in data_split:
            data_point, data_value = item.split(':')
            self.ur_data[data_point] = float(data_value)