def wait(ur, x_goal, y_goal):

    #Convert to shorter number that can be compared
    x_goal = int(x_goal*1000)
    y_goal = int(y_goal*1000)

    while True:

        #Get actual pose TCP-base
        x_ur,y_ur,z_ur,rx_ur,ry_ur,rz_ur = ur.get_pose()

        #Convert to shorter number that can be compared
        x_ur = int(x_ur*1000)
        y_ur = int(y_ur*1000)

        #print(x_goal, x_ur, y_goal, y_ur)

        if x_ur==x_goal and y_ur==y_goal:
            print('Arrived to goal position', x_goal, y_goal)
            break