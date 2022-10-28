# Serial Communication with RTM
# Python Tutorial - How to Read Data from Arduino via Serial Port
# https://youtu.be/AHr94RtMj1A
# pip install pyserial
import os
import pickle
import sys
from tkinter import messagebox

import serial.tools.list_ports
import serial
from threading import Thread


class UsbSerial:

    def __init__(self, text_comread, view):
        self.portList = []
        self.comport = ""
        self.serialInst = serial.Serial()
        self.status = ""
        self.read_line = ""
        self.text_comread = text_comread
        self.view = view
        self.com_port_read_is_started = False

    @staticmethod
    def get_comport_saved():
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except OSError:
            return ""

    @staticmethod
    def put_comport(comport):
        myvar = comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    def get_ports(self):
        """
        get a list of serial ports available on laptop
        :return: portList
        """
        self.portList = []
        ports = serial.tools.list_ports.comports(0)
        for onePort in ports:
            self.portList.append(str(onePort))
        return self.portList

    def open_comport(self, comport):
        if self.status != 'OPEN':
            try:
                print(f'Try to open {comport} ')
                self.serialInst.baudrate = 115200
                self.serialInst.port = comport
                if self.serialInst.isOpen():
                    try:
                        print("isopen")
                        self.serialInst.close()
                    except Exception:
                        pass
                self.serialInst.open()
                self.status = "OPEN"
            except Exception:
                self.status = 'ERROR'
        return self.status

    def start_comport_read_thread(self):
        if self.com_port_read_is_started:
            print('com_port read alredy started')
            return
        else:
            self.com_port_read_is_started=True
            print('start com_tread')
            com_thread = Thread(target=self.read_comport, daemon=True)
            com_thread.start()

    def read_comport(self):
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port
        print('read_comport starting')

        while True:
            if self.serialInst.inWaiting:
                try:
                    ln=self.serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln)>0:
                        self.read_line = ln
                        self.view.text_com_read_update(self.read_line)
                        self.view.text_adjust_update(self.read_line)
                except Exception as e:
                    messagebox.showerror('error', 'Connection lost\nClose the programm')
                    self.view.close()

    def write_comport(self, cmd):
        print(f'write_comport {cmd}')
        self.serialInst.write_timeout = 1.0

        try:
            self.serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False
