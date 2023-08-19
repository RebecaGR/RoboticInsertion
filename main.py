import argparse
import numpy as np
import sys

from class_ur import UR
from class_sfe import SFE
from InsertProgram import insertion
from FindConnector import find_connector
from PickUpConnector import pickupConnector

def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--choice',
                    type=int,
                    help='File to run',
                    choices=[1, 2, 3])

    return args.parse_args()


def main(args):
    func = args

    # Open UR
    ur = UR('192.38.66.226', 30003)

    # Open SFE
    sfe = SFE()

    if func == 1:
        # Find connector
        c_x, c_y = find_connector()
        np.save('tmp_point.npy', np.array([c_x, c_y]))

    elif func == 2:
        # Pickup connector
        pickupConnector(ur, sfe)

    else:
        # Insection
        data = np.load('tmp_point.npy')
        c_x, c_y = data[0], data[1]
        insertion(ur, sfe, c_x, c_y)
    




args = int(input('Choice: '))
print(args)

main(args)
