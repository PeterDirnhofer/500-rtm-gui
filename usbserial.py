# Serial Communication with RTM
# Python Tutorial - How to Read Data from Arduino via Serial Port
# https://youtu.be/AHr94RtMj1A
# pip install pyserial
import pickle
import time
import tkinter as tk
from tkinter import messagebox

import serial.tools.list_ports
import serial
from threading import Thread

from view import View

NUMBER_OF_PARAMETERS = 10


class UsbSerial:

    serialInst = serial.Serial()
    sm_state_static = "INIT"

    def __init__(self, view):
        self.m_status = ""
        self.m_read_line = ""
        self.view = view
        self.m_com_port_read_is_started = False
        self.m_line_to_consume = ""
        self.parameters_needed = 0
        self.m_parameter_list = []
        self.m_sm_state = "INIT"
        self.m_sm_last_state = 'LAST'
        self.m_actport = ""

    def write(cmd):
        UsbSerial.serialInst.write_timeout = 1.0

        try:
            UsbSerial.serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False


    def get_parameter_from_esp(self):
        """
        Trigger reading NUMBER_OF_PARAMETERS parameters in m_read_loop to m_parameter_list
        """
        self.view.lbox_parameter.delete(0, tk.END)
        self.m_parameter_list.clear()
        self.parameters_needed = NUMBER_OF_PARAMETERS
        UsbSerial.write('PARAMETER,?')

    ####################################################################
    # COM READ THREAD
    def m_start_read_loop(self):
        if self.m_com_port_read_is_started:
            print("m_read_loop already started")
            return
        else:
            self.m_com_port_read_is_started = True
            com_thread = Thread(target=self.m_read_loop, daemon=True)
            com_thread.start()

    def m_read_loop(self):
        """
        Loop that reads comport. Monitor reads in
        :return:
        """
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port

        while True:
            if UsbSerial.serialInst.inWaiting:
                try:
                    ln = UsbSerial.serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln) > 0:
                        self.m_read_line = ln
                        if View.view_mode=='ADJUST':
                            self.view.label_adjust_update(self.m_read_line)
                            continue


                        if self.parameters_needed > 0:
                            self.m_parameter_list.append(self.m_read_line)
                            self.view.lbox_parameter.insert(tk.END, self.m_read_line)
                            self.parameters_needed -= 1
                        else:
                            self.view.lbox_com_read_update(self.m_read_line)
                            #self.view.label_adjust_update(self.m_read_line)


                except Exception:
                    messagebox.showerror('error', 'Connection lost\nClose the programm')
                    self.view.close()

    ####################################################################################
    @staticmethod
    def m_get_default_comport():
        '''
        Read default COM Port from File compport.pkl
        :return: Default COM Port
        '''
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except OSError:
            return ""

    @staticmethod
    def m_put_default_comport(comport):
        '''Write default COM Port to file comport.pkl'''
        myvar = comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    def m_get_ports(self):
        """
        get a list of serial ports available on computer
        :return: portList
        """
        port_list = []
        ports = serial.tools.list_ports.comports(0)
        for onePort in ports:
            port_list.append(str(onePort))
        return port_list

    def m_open_comport(self, comport):
        if self.m_status != 'OPEN':
            try:
                UsbSerial.serialInst.baudrate = 115200
                UsbSerial.serialInst.port = comport
                if UsbSerial.serialInst.isOpen():
                    try:
                        print("isopen")
                        UsbSerial.serialInst.close()
                    except Exception:
                        pass
                UsbSerial.serialInst.open()
                self.m_status = "OPEN"
            except Exception:
                self.m_status = 'ERROR'
        return self.m_status

    ##########################################################
    def start_init_com_statemachine(self):

        init_com_thread = Thread(target=self.init_com_statemachine_loop, daemon=True)

        init_com_thread.start()

    def init_com_statemachine_loop(self):
        '''
        Statemachine to open comunication wit ESP32. -Open COM -Send CRTL-C Reset to ESP32 -Wait for ESP32 response 'IDLE'
        - Request parameters from ESP32 and render in Frame parameters
        '''

        while True:

            if UsbSerial.sm_state_static != self.m_sm_last_state:
                self.m_sm_last_state = UsbSerial.sm_state_static
                self.view.text_status.set(UsbSerial.sm_state_static)

            if UsbSerial.sm_state_static == 'INIT':
                self.m_is_default_port_existing()
                time.sleep(0.050)
                continue
            elif UsbSerial.sm_state_static == 'EXISTING':
                self.m_open()
                time.sleep(0.050)
                continue
            elif UsbSerial.sm_state_static == 'OPEN':
                self.m_send_reset()
                time.sleep(1)
                continue
            elif UsbSerial.sm_state_static == 'WAIT_FOR_IDLE':
                self.parameters_needed = 0
                self.m_wait_for_idle()
                time.sleep(0.050)
                continue
            elif UsbSerial.sm_state_static == 'COM_READY':
                self.m_com_ready()
            elif UsbSerial.sm_state_static == 'PASSIVE':
                time.sleep(1)
                continue
            elif UsbSerial.sm_state_static == "ERROR_COM":
                self.m_error()
                time.sleep(0.200)

            else:
                raise Exception(f'Invalid state in state_machine: {UsbSerial.sm_state_static}')

    def m_is_default_port_existing(self):
        # Check if default COM port is existing on Computer
        self.m_actport = self.m_get_default_comport()
        self.view.text_com_state.set(f'Connecting {self.m_actport} ...')
        available_ports = self.m_get_ports()
        port_exists = False
        for port in available_ports:
            r = self.m_actport in port
            if r:
                port_exists = True
        if not port_exists:
            self.view.text_com_state.set(f'ERROR_COM {self.m_actport} not available on Computer')
            UsbSerial.sm_state_static = 'ERROR_COM'
            return
        else:
            UsbSerial.sm_state_static = 'EXISTING'
            return

    def m_open(self):
        # try to open COM port on computer
        result = self.m_open_comport(self.m_actport)
        if result == 'OPEN':
            UsbSerial.sm_state_static = 'OPEN'
        else:
            UsbSerial.sm_state_static = 'ERROR_COM'
        return

    def m_send_reset(self):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if UsbSerial.write(chr(3)):
            self.m_start_read_loop()  # enable receiver
            UsbSerial.sm_state_static = 'WAIT_FOR_IDLE'
        else:
            UsbSerial.sm_state_static = 'ERROR_COM'

    def m_wait_for_idle(self):
        # Wait for 'IDLE' from ESP32

        if self.m_read_line == 'IDLE':
            UsbSerial.sm_state_static = 'COM_READY'
            return

        UsbSerial.sm_state_static = "ERROR_COM"
        return

    def m_com_ready(self):
        self.view.button_select_adjust['state'] = tk.NORMAL
        self.view.button_select_measure['state'] = tk.NORMAL
        self.view.button_select_reset['state'] = tk.NORMAL
        self.view.text_com_state.set(f'Connected {self.m_actport}')

        # Get parameter and display in parameter_frame
        self.view.controller.usb_serial_get_parameter_handle()
        UsbSerial.sm_state_static = 'PASSIVE'

    def m_error(self):
        self.view.frame_select_com_on()
        available_ports = self.m_get_ports()
        self.view.display_comports(available_ports)

        self.m_com_port_read_is_started = False
        if self.view.com_selected != "":
            self.m_put_default_comport(self.view.com_selected)
            # self.view.text_com_read_update(f'{self.view.com_selected} selected')
            self.view.frame_select_com_off()
            UsbSerial.sm_state_static = 'INIT'
            self.view.com_selected = ""
            self.m_com_port_read_is_started = False
