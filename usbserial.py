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

import view
from view import View

NUMBER_OF_PARAMETERS = 10


class UsbSerial:

    # Class variables
    view_static = None
    serialInst = serial.Serial()
    statemachine_state = "INIT"
    parameters_needed = 0
    m_parameter_list = []
    m_status=""
    m_read_line=""
    m_com_port_read_is_started = False
    act_port=None


    def __init__(self):
        pass
        #if UsbSerial.view_static == None:
        #    UsbSerial.view_static = view


    @classmethod
    def write(cls,cmd):
        UsbSerial.serialInst.write_timeout = 1.0

        try:
            UsbSerial.serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False

    @classmethod
    def request_parameter_from_esp(cls):
        """
        Trigger reading NUMBER_OF_PARAMETERS parameters in m_read_loop to m_parameter_list
        """
        UsbSerial.view_static.lbox_parameter.delete(0, tk.END)
        UsbSerial.m_parameter_list.clear()
        UsbSerial.parameters_needed = NUMBER_OF_PARAMETERS
        UsbSerial.write('PARAMETER,?')

    ####################################################################
    # COM READ THREAD
    def m_start_read_loop(self):
        if UsbSerial.m_com_port_read_is_started:
            print("m_read_loop already started")
            return
        else:
            UsbSerial.m_com_port_read_is_started = True
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
                        UsbSerial.m_read_line = ln
                        if View.view_mode=='ADJUST':
                            UsbSerial.view_static.label_adjust_update(UsbSerial.m_read_line)
                            continue

                        if UsbSerial.parameters_needed > 0:
                            UsbSerial.m_parameter_list.append(UsbSerial.m_read_line)
                            UsbSerial.view_static.lbox_parameter.insert(tk.END, UsbSerial.m_read_line)
                            UsbSerial.parameters_needed -= 1
                        else:
                            UsbSerial.view_static.lbox_com_read_update(UsbSerial.m_read_line)
                            #UsbSerial.view_static.label_adjust_update(UsbSerial.m_read_line)


                except Exception:
                    messagebox.showerror('error', 'Connection lost\nClose the programm')
                    UsbSerial.view_static.close()

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
        if UsbSerial.m_status != 'OPEN':
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
                UsbSerial.m_status = "OPEN"
            except Exception:
                UsbSerial.m_status = 'ERROR'
        return UsbSerial.m_status

    ##########################################################
    def start_init_com_statemachine(self):

        init_com_thread = Thread(target=self.init_com_statemachine_loop, daemon=True)

        init_com_thread.start()

    def init_com_statemachine_loop(self):
        '''
        Statemachine to open comunication wit ESP32. -Open COM -Send CRTL-C Reset to ESP32 -Wait for ESP32 response 'IDLE'
        - Request parameters from ESP32 and render in Frame parameters
        '''
        last_state='LAST'
        while True:

            if UsbSerial.statemachine_state != last_state:
                last_state = UsbSerial.statemachine_state
                UsbSerial.view_static.text_status.set(UsbSerial.statemachine_state)

            if UsbSerial.statemachine_state == 'INIT':
                self.m_is_default_port_existing()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'EXISTING':
                self.m_open()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'OPEN':
                self.m_send_reset()
                time.sleep(1)
                continue
            elif UsbSerial.statemachine_state == 'WAIT_FOR_IDLE':
                UsbSerial.parameters_needed = 0
                self.m_wait_for_idle()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'COM_READY':
                self.m_com_ready()
            elif UsbSerial.statemachine_state == 'PASSIVE':
                time.sleep(1)
                continue
            elif UsbSerial.statemachine_state == "ERROR_COM":
                self.m_error()
                time.sleep(0.200)

            else:
                raise Exception(f'Invalid state in state_machine: {UsbSerial.statemachine_state}')

    def m_is_default_port_existing(self):
        # Check if default COM port is existing on Computer
        UsbSerial.m_actport = self.m_get_default_comport()
        UsbSerial.view_static.text_com_state.set(f'Connecting {UsbSerial.m_actport} ...')
        available_ports = self.m_get_ports()
        port_exists = False
        for port in available_ports:
            r = UsbSerial.m_actport in port
            if r:
                port_exists = True
        if not port_exists:
            UsbSerial.view_static.text_com_state.set(f'ERROR_COM {UsbSerial.m_actport} not available on Computer')
            UsbSerial.statemachine_state = 'ERROR_COM'
            return
        else:
            UsbSerial.statemachine_state = 'EXISTING'
            return

    def m_open(self):
        # try to open COM port on computer
        result = self.m_open_comport(UsbSerial.m_actport)
        if result == 'OPEN':
            UsbSerial.statemachine_state = 'OPEN'
        else:
            UsbSerial.statemachine_state = 'ERROR_COM'
        return

    def m_send_reset(self):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if UsbSerial.write(chr(3)):
            self.m_start_read_loop()  # enable receiver
            UsbSerial.statemachine_state = 'WAIT_FOR_IDLE'
        else:
            UsbSerial.statemachine_state = 'ERROR_COM'

    def m_wait_for_idle(self):
        # Wait for 'IDLE' from ESP32

        if UsbSerial.m_read_line == 'IDLE':
            UsbSerial.statemachine_state = 'COM_READY'
            return

        UsbSerial.statemachine_state = "ERROR_COM"
        return

    def m_com_ready(self):
        UsbSerial.view_static.button_select_adjust['state'] = tk.NORMAL
        UsbSerial.view_static.button_select_measure['state'] = tk.NORMAL
        UsbSerial.view_static.button_select_reset['state'] = tk.NORMAL
        UsbSerial.view_static.text_com_state.set(f'Connected {UsbSerial.m_actport}')

        # Get parameter and display in parameter_frame
        UsbSerial.view_static.controller.usb_serial_get_parameter_handle()
        UsbSerial.statemachine_state = 'PASSIVE'

    def m_error(self):
        UsbSerial.view_static.frame_select_com_on()
        available_ports = self.m_get_ports()
        UsbSerial.view_static.display_comports(available_ports)

        UsbSerial.m_com_port_read_is_started = False
        if UsbSerial.view_static.com_selected != "":
            self.m_put_default_comport(UsbSerial.view_static.com_selected)
            # UsbSerial.view_static.text_com_read_update(f'{UsbSerial.view_static.com_selected} selected')
            UsbSerial.view_static.frame_select_com_off()
            UsbSerial.statemachine_state = 'INIT'
            UsbSerial.view_static.com_selected = ""
            UsbSerial.m_com_port_read_is_started = False
