# Serial Communication with RTM
# pip install pyserial
import pickle

import serial.tools.list_ports
import serial
from os.path import exists

#serialInst=serial.Serial()

class Usb_serial:
    def __init__(self):
        self.portList=[]
        self.comport=""
        self.serialInst=serial.Serial()
        self.status=""

    def get_comport(self):
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except:
            return""

    def put_comport(self,comport):
        myvar=comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    def get_ports(self):
        '''
        get a list of serial ports available on laptop
        :return: portList
        '''
        self.portList = []
        ports=serial.tools.list_ports.comports(0)
        for onePort in ports:
            self.portList.append(str(onePort))
        return self.portList

    def open_comport(self,comport):
        if self.status!='CONNECTED':
            try:
                self.serialInst=serial.Serial(port=comport,baudrate=11520)
                self.status="CONNECTED"
            except Exception as e:
                print(e)
                self.status=e
        return self.status

