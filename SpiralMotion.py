import numpy as np
import math
from class_ur import UR
from class_sfe import SFE
from math import pi
import time
from threading import Thread
import queue
from gripper.class_gripper import Gripper

#Open SFE
sfe = SFE()

#Make sure SFE is locked before moving the robot arm
cmd = "SET;MOT_LOCK_STATE;LOCK\n"  
sfe.write(cmd)
sfe.read()

time.sleep(0.5)

# Open UR
ur = UR('192.38.66.226', 30003)

# Create queue
#q = queue.Queue()

#Go to start search position
ur.move(x=0.498, y=0.003, z=0.130, rx=-3.1294, ry=0.06, rz=-0.041)

time.sleep(10)
print('Initial position')

#Close gripper for locating connector
# gripperfunc = Gripper('/dev/ttyUSB0') 
# gripperfunc.close(wait=True)

#Unlock SFE
cmd = "SET;MOT_LOCK_STATE;UNLOCK\n"  
sfe.write(cmd)
sfe.read()

time.sleep(0.5)
print('SFE unlocked')

# sfe_data = Thread(target=sfe_position, args=(q,sfe), daemon=True)
# sfe_data.start()

#Variation in rx and ry will tell us if we are touching the connector and in which direction
rx_sfe = 0
ry_sfe = 0

print('Starting spiral connector search')


R = 1 # Initial radius
PI = np.pi 
max_cycles = 7

a = 0 #distance from the center
b = 0.003 # distance between turns

R = max_cycles * b * PI

theta = np.linspace(0, max_cycles * 2 * PI, 300)[::-1]

#print((b*max_cycles*2*PI)*10e-3) #Radius of the spiral

x = 0.362 + (a + b * theta) * np.cos(theta) #Add offset by summing to r = (a + b * theta)
y = 0.003 + (a + b * theta) * np.sin(theta)

for i in range(len(x)):

    #Check if it collides with connector
    if rx_sfe < -1.0 or rx_sfe > 1.0 or ry_sfe < -1.0 or ry_sfe > 1.0:
        print('Connector found')
        print(rx_sfe, ry_sfe)
        break

    #Get actual pose TCP-base
    #print(x[i])
    x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
    time.sleep(0.3)
    ur.move(x=x[i], y=y[i], z=0.130, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
    
    #Get info from SFE
    cmd = "GET;POSE\n"  
    sfe.write(cmd)

    #read sfe pose
    _, _, _, rx_sfe, ry_sfe, _ = sfe.readposition()

    time.sleep(0.5)

    print(rx_sfe, ry_sfe)