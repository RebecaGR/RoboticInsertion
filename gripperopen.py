import socket
import time
import sys
sys.path.append('../gripper')
#import robotconfig
from gripper.class_gripper import Gripper
gripperfunc = Gripper('/dev/ttyUSB1') 
gripperfunc.open(wait=True)

gripperfunc.shutdown()



