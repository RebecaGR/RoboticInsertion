import serial
import serial.tools.list_ports as p

class SFE:
    def __init__(self):
        # #set this the com port you need SFE
        # com_port="/dev/ttyUSB1"
        # baudrate=38400
        # timeout=0.03

        # #set up connection SFE
        # self.ser=serial.Serial(port=com_port, baudrate=baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=timeout)
        
        print('SFE: SFE is ready.')

    def write(self, cmd):
        com_port="/dev/ttyUSB0"
        baudrate=38400
        timeout=0.03
        #set up connection SFE
        self.ser=serial.Serial(port=com_port, baudrate=baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=timeout)

        #print(cmd)
        self.ser.write(bytearray((cmd).encode()))

    def read(self):
        sb = self.ser.readline()
        message = sb.decode()

        #print(message)

        self.ser.close()

        return message

    def readposition(self):
        sb = self.ser.readline()
        message = sb.decode()

        #print(message)

         #Find position variables
        beginpos = message.find(";",4);
        posx = message.find("|");
        x = message[ beginpos + 1 : posx]
        x = float(x)

        posy = message.find("|",posx+1);
        y = message[posx+1 : posy]
        y= float(y)

        posz = message.find("|",posy+1);
        z = message[posy+1 : posz]
        z = float(z)

        posrx = message.find("|",posz+1);
        rx = message[posz+1 : posrx]
        rx = float(rx)

        posry = message.find("|",posrx+1);
        ry = message[posrx+1 : posry]
        ry = float(ry)

        posrz = message.find(";",posry+1);
        rz = message[posry+1 : posrz]
        rz = float(rz)

        return x,y,z,rx,ry,rz