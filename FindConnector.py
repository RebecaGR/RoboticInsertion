from class_ur import UR
from class_sfe import SFE
from math import pi
import time
from threading import Thread
import queue
from gripper.class_gripper import Gripper
from ConnectorCentrePoint import findCircle
from PickUpConnector import pickupConnector
from functions import wait
from InsertProgram import insertion

def log_sensor_data(f,x,y,z,rx,ry,rz):
    f.write('SFE data: ')
    f.write(str(x)+';')
    f.write(str(y)+';')
    f.write(str(z)+';')
    f.write(str(rx)+';')
    f.write(str(ry)+';')
    f.write(str(rz)+';')
    f.write('\n')

def log_robot_pos(f,x,y,z,rx,ry,rz):
    f.write('UR pos: ')
    f.write(str(x)+';')
    f.write(str(y)+';')
    f.write(str(z)+';')
    f.write(str(rx)+';')
    f.write(str(ry)+';')
    f.write(str(rz)+';')
    f.write('\n')


def find_connector():
    #Log data
    f = open('circle_data.txt', 'w')
    f2 = open('circle_sfe_data.txt', 'w')

    # Open SFE
    sfe = SFE()

    #Make sure SFE is locked before moving the robot arm
    cmd = "SET;MOT_LOCK_STATE;LOCK\n"  
    sfe.write(cmd)
    sfe.read()

    time.sleep(0.5)

    # Open UR
    ur = UR('192.38.66.226', 30003)

    # # Create queue
    # q = queue.Queue()

    #start position without connector--> [x,y,z,rx,ry,rz]
    start_position = [0.45169, -0.12347, 0.130, -3.1294, 0.0565, 0.0085]

    #start position with connector gripped 
    #start_position = [0.45169, -0.12347, 0.144, -3.1294, 0.0565, 0.0085]

    #Go to start search position
    ur.move(x=start_position[0], y=start_position[1], z=start_position[2], rx=start_position[3], ry=start_position[4], rz=start_position[5])
    wait(ur, x_goal=start_position[0], y_goal=start_position[1])

    #time.sleep(10)
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

    #Search boundaries
    y_min = -0.12347
    y_max = 0.09683
    x_min = 0.276

    print('Starting connector search')

    found = False

    #First locate the connector

    #Zig-zag/spiral move in the defined working area

    #For the actual use case --> change z to 128-132 mm for the gripper to touch the connector

    #Get actual pose TCP-base
    x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
    print(y_ur)

    time.sleep(0.5)

    #Find first contact point

    while x_ur > x_min or rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:

        y=y_ur
        print(y)

        #Move in y
        while y < y_max:

            if rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:
                print('while condition break')
                found = True
                #ur.move(x=x_ur, y=y-0.05, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
                print(rx_sfe, ry_sfe)
                log_sensor_data(f, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)
                #Get actual pose TCP-base
                x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
                log_robot_pos(f, x_ur, y_ur, z_ur, rx_ur, ry_ur, rz_ur)
                #Save point for later calculation
                # print('deflection point 1')
                # print(y_ur, y_sfe*1e-3, y_ur+y_sfe*1e-3, y_ur-y_sfe*1e-3)
                point1 = [x_ur+x_sfe*1e-3, y_ur-y_sfe*1e-3]
                break
            else:
                y = y + 0.01
                #print(y)
                ur.move(x=x_ur, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
                wait(ur, x_ur, y)
                #time.sleep(0.5)
                #Get info from SFE
                cmd = "GET;POSE\n"  
                sfe.write(cmd)

                #time.sleep(0.5)

                #read sfe pose
                x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
                log_sensor_data(f2, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)

                #time.sleep(0.3)

        if found == True:
            break

        #Wait for it to get to y
        #wait(x_ur,y)

        #Move in x
        ur.move(x=x_ur-0.03, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        #time.sleep(0.5)
        wait(ur, x_ur-0.03,y)

        #Move in y
        while y > y_min:

            if rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:
                print('while condition break')
                found = True
                #ur.move(x=x_ur-0.03, y=y_max, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
                print(rx_sfe, ry_sfe)
                log_sensor_data(f, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)
                #Get actual pose TCP-base
                x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
                log_robot_pos(f, x_ur, y_ur, z_ur, rx_ur, ry_ur, rz_ur)
                #Save point for later calculation
                point1 = [x_ur, y_ur]
                break
            else:
                y = y - 0.01
                ur.move(x=x_ur-0.03, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
                wait(ur, x_ur-0.03, y)
                #time.sleep(0.5)
                #Get info from SFE
                cmd = "GET;POSE\n"  
                sfe.write(cmd)

                #time.sleep(0.5)

                #read sfe pose
                x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
                log_sensor_data(f2, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)

                #time.sleep(0.3)
        
        #wait(x_ur-0.01,y_min)

        if found == True:
            break

        #Wait for it to get to y
        #wait(x_ur-0.03,y)

        #Move in x
        ur.move(x=x_ur-0.06, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        #time.sleep(0.5)
        wait(ur, x_ur-0.06,y)

        #Get actual pose TCP-base
        x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()

    #Find second point

    #if rx is negative --> move -0.05 in y, up in z and to y_max then down again to previous z --> to find the second point
    #if rx is positive --> move +0.05 in y, up in z and to y_min then down again to previous z --> to find the second point
    #if ry is negatibe --> not probable --> implement later on
    #if ry is positive --> not probable --> implement later on

    if rx_sfe < 0:
        y_temp = y - 0.05
        z_temp = z_ur + 0.03
        ur.move(x=x_ur, y=y_temp, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        wait(ur, x_ur, y_temp)
        #time.sleep(0.3)
        #include movement in z --> z temp
        ur.move(x=x_ur, y=y_temp, z=z_temp, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        time.sleep(0.5)
        ur.move(x=x_ur, y=y_max, z=z_temp, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        wait(ur, x_ur, y_max)
        #time.sleep(0.3)
        ur.move(x=x_ur, y=y_max, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        time.sleep(0.5)

        #Get info from SFE
        cmd = "GET;POSE\n"  
        sfe.write(cmd)

        #read sfe pose
        x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()

        time.sleep(0.3)

        y = y_max

        #Move in y
        while y > y_min:

            if rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:
                print('while condition break')
                #Get actual pose TCP-base
                x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
                #Move away
                ur.move(x=x_ur, y=y+0.03, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
                wait(ur, x_ur, y+0.03)
                time.sleep(0.3)
                print(rx_sfe, ry_sfe)
                #Log data for analysis
                log_sensor_data(f, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)
                log_robot_pos(f, x_ur, y_ur, z_ur, rx_ur, ry_ur, rz_ur)
                #Save point for later calculation
                # print('deflection point 2')
                # print(y_ur, y_sfe*1e-3, y_ur+y_sfe*1e-3, y_ur-y_sfe*1e-3)
                point2 = [x_ur+x_sfe*1e-3, y_ur-y_sfe*1e-3]
                break
            else:
                y = y - 0.01
                ur.move(x=x_ur, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
                wait(ur, x_ur, y)
                
                #Get info from SFE
                cmd = "GET;POSE\n"  
                sfe.write(cmd)

                #read sfe pose
                x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
                log_sensor_data(f2, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)

                #time.sleep(0.3)

    elif rx_sfe > 0:
        y_temp = y + 0.05
        z_temp = z_ur + 0.03
        ur.move(x=x_ur, y=y_temp, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        wait(ur, x_ur, y_temp)
        #time.sleep(0.3)
        #include movement in z -> z temp
        ur.move(x=x_ur, y=y_temp, z=z_temp, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        time.sleep(0.5)
        ur.move(x=x_ur, y=y_min, z=z_temp, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        wait(ur, x_ur, y_min)
        #time.sleep(0.3)
        ur.move(x=x_ur, y=y_min, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        time.sleep(0.5)

        #Get info from SFE
        cmd = "GET;POSE\n"  
        sfe.write(cmd)

        #read sfe pose
        x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()

        time.sleep(0.3)

        y = y_min

        #Move in y
        while y < y_max:

            if rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:
                print('while condition break')
                #Get actual pose TCP-base
                x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
                #Move away
                ur.move(x=x_ur, y=y-0.05, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
                wait(ur, x_ur, y-0.05)
                time.sleep(0.3)
                print(rx_sfe, ry_sfe)
                #Log data for analysis
                log_sensor_data(f, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)
                log_robot_pos(f, x_ur, y_ur, z_ur, rx_ur, ry_ur, rz_ur)
                #Save point for later calculation
                point2 = [x_ur, y_ur]
                break
            else:
                y = y + 0.01
                ur.move(x=x_ur, y=y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
                wait(ur, x_ur, y)
                
                #Get info from SFE
                cmd = "GET;POSE\n"  
                sfe.write(cmd)

                #read sfe pose
                x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
                log_sensor_data(f2, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)

                #time.sleep(0.3)


    #Find third point 

    #if rx is negative --> move -0.05 in y, to x starting point and to the middle y between point 1 and point 2 --> to find the third point
    #if rx is positive --> move +0.05 in y, to x starting point and to the middle y between point 1 and point 2 --> to find the third point
    #if ry is negatibe --> not probable --> implement later on
    #if ry is positive --> not probable --> implement later on

    mid_y = (point1[1]+point2[1])/2
    print(mid_y)
    ur.move(x=start_position[0], y=mid_y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    wait(ur, start_position[0], mid_y)

    # if rx_sfe < 0:
        # y_temp = y - 0.05
        # ur.move(x=x_ur, y=y_temp, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        # wait(x_ur, y_temp)
        #Move to initial x value and middle y
        # mid_y = (point1[1]+point2[1])/2
        # print(mid_y)
        # ur.move(x=start_position[0], y=mid_y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        # wait(start_position[0], mid_y)
        # ur.move(x=x_ur, y=y_max, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
        # time.sleep(0.5)

    # elif rx_sfe > 0:
    #     y_temp = y + 0.05
    #     ur.move(x=x_ur, y=y_temp, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    #     wait(x_ur, y_temp)
    #     #Move to initial x value and middle y
    #     mid_y = (point1[1]+point2[1])/2
    #     print(mid_y)
    #     ur.move(x=start_position[0], y=mid_y, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    #     wait(start_position[0], mid_y)
    #     # ur.move(x=x_ur, y=y_min, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
    #     # time.sleep(0.5)

    #Get info from SFE
    cmd = "GET;POSE\n"  
    sfe.write(cmd)

    #read sfe pose
    x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()

    time.sleep(0.3)

    x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()

    x = start_position[0]

    #Move in x
    while x > x_min:

        if rx_sfe < -1.2 or rx_sfe > 1.2 or ry_sfe < -1.2 or ry_sfe > 1.2:
            print('while condition break')
            #Get actual pose TCP-base
            x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()
            #Move away
            ur.move(x=x+0.05, y=y_ur, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur)
            wait(ur, x+0.05, y_ur)
            print(rx_sfe, ry_sfe)
            #Log data for analysis
            log_sensor_data(f, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)
            log_robot_pos(f, x_ur, y_ur, z_ur, rx_ur, ry_ur, rz_ur)
            #Save point for later calculation
            #Save the UR position + sensor deflection -> for more accurate position
            point3 = [x_ur+x_sfe*1e-3, y_ur]
            break
        else:
            x = x - 0.01
            ur.move(x=x, y=y_ur, z=z_ur, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)
            wait(ur, x, y_ur)
                
            #Get info from SFE
            cmd = "GET;POSE\n"  
            sfe.write(cmd)

            #read sfe pose
            x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe = sfe.readposition()
            log_sensor_data(f2, x_sfe, y_sfe, z_sfe, rx_sfe, ry_sfe, rz_sfe)

            #time.sleep(0.3)


    #Calculate connector size and center position
    c_x, c_y = findCircle(point1[0], point1[1], point2[0], point2[1], point3[0], point3[1])
    #ur.move(x=c_x, y=c_y, z=0.165, rx=rx_ur, ry=ry_ur, rz=rz_ur, v=0.05)

    return c_x, c_y

#Get 3 point of the connector --> calculate circular connectors --> size and center position
#What happens with other shapes connectors??? --> out of th scope of the project ??

# #Pick up connector
# pickupConnector(ur, sfe)

# #Insertion task
# insertion(ur, sfe, c_x, c_y)
