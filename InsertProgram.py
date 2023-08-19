from class_ur import UR
from class_sfe import SFE
from math import pi
import time
from threading import Thread
import queue
from functions import wait

def insertion(ur, sfe, c_x, c_y):

    # def sfe_position(queue, sfe):

    #     while True:

    #         #Get info from SFE
    #         cmd = "GET;POSE\n"  
    #         sfe.write(cmd)

    #         time.sleep(0.5)

    #         #read sfe pose
    #         #x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.read()
    #         position = sfe.read()

    #         queue.put(position)

    # Open SFE
    # sfe = SFE()

    #Make sure SFE is locked before moving the robot arm
    cmd = "SET;MOT_LOCK_STATE;LOCK\n"  
    sfe.write(cmd)
    sfe.read()

    time.sleep(0.5)

    # # Open UR
    # ur = UR('192.38.66.226', 30003)

    # # Create queue
    # q = queue.Queue()

    #Read current UR position
    x_ur,y_ur,_,rx_ur,ry_ur,rz_ur = ur.get_pose()

    #Go to approach position
    ur.move(x=c_x, y=c_y, z=0.210, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    wait(ur, c_x, c_y)
    time.sleep(5)

    print('Approach position')

    #Move on top the connector
    ur.move(x=c_x, y=c_y, z=0.165, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    time.sleep(1)

    #Unlock SFE
    cmd = "SET;MOT_LOCK_STATE;UNLOCK\n"  
    sfe.write(cmd)
    sfe.read()

    time.sleep(0.5)
    print('SFE unlocked')

    # sfe_data = Thread(target=sfe_position, args=(q,sfe), daemon=True)
    # sfe_data.start()

    z_sfe = 0

    print('Starting inserting motion')

    f = open('sfedata.txt', 'w')
    f2 = open('urdata.txt', 'w')

    #First insertion move --> Place the connector in position

    while z_sfe > -1.00:

        # _,_,z_sfe,_,_,_ = q.get()
        #Get info from SFE
        cmd = "GET;POSE\n"  
        sfe.write(cmd)

        time.sleep(0.5)

        #read sfe pose
        x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
        #Log data
        f.write(str(x_sfe)+';')
        f.write(str(y_sfe)+';')
        f.write(str(z_sfe)+';')
        f.write(str(rx_sfe)+';')
        f.write(str(ry_sfe)+';')
        f.write(str(rz_sfe))
        f.write('\n')
        #position = sfe.read()
        print(z_sfe)

        #Get actual pose TCP-base
        x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()

        #Log data
        f2.write(str(x_ur)+';')
        f2.write(str(y_ur)+';')
        f2.write(str(z_ur)+';')
        f2.write(str(rx_ur)+';')
        f2.write(str(ry_ur)+';')
        f2.write(str(rz_ur))
        f2.write('\n')

        #print(z_ur)
        ur.move(x=x_ur, y=y_ur, z=z_ur-0.001, rx=rx_ur, ry=ry_ur, rz=rz_ur)

    #Second insertion move --> turn until correct position found

    time.sleep(0.5)

    print('Start turning')

    while z_sfe < -0.75:

        # _,_,z_sfe,_,_,_ = q.get()
        #Get info from SFE
        cmd = "GET;POSE\n"  
        sfe.write(cmd)

        time.sleep(0.5)

        #read sfe pose
        x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
        #Log data
        f.write(str(x_sfe)+';')
        f.write(str(y_sfe)+';')
        f.write(str(z_sfe)+';')
        f.write(str(rx_sfe)+';')
        f.write(str(ry_sfe)+';')
        f.write(str(rz_sfe))
        f.write('\n')
        #position = sfe.read()
        print(z_sfe)

        #Get actual pose TCP-base
        b, s, e, w1, w2, w3 = ur.get_joints()
        print(w3)
        ur.move_joints(b=b, s=s, e=e, w1=w1, w2=w2, w3=w3+0.05)

        #read sfe pose
        #x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()