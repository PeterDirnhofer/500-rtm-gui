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
    _serialInst = serial.Serial()
    statemachine_state = "INIT"
    _parameters_needed = 0
    _parameter_list = []
    _status= ""
    _read_line= ""
    _com_port_read_is_started = False
    _act_port=None

    @classmethod
    def write(cls,cmd):
        UsbSerial._serialInst.write_timeout = 1.0

        try:
            UsbSerial._serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False

    @classmethod
    def request_parameter_from_esp(cls):
        """
        Trigger reading NUMBER_OF_PARAMETERS parameters in m_read_loop to m_parameter_list
        """
        UsbSerial.view_static.lbox_parameter.delete(0, tk.END)
        UsbSerial._parameter_list.clear()
        UsbSerial._parameters_needed = NUMBER_OF_PARAMETERS
        UsbSerial.write('PARAMETER,?')

    ####################################################################
    # COM READ THREAD
    @classmethod
    def m_start_read_loop(cls):
        if UsbSerial._com_port_read_is_started:
            print("m_read_loop already started")
            return
        else:
            UsbSerial._com_port_read_is_started = True
            com_thread = Thread(target=UsbSerial.m_read_loop, daemon=True)
            com_thread.start()

    @classmethod
    def m_read_loop(cls):
        """
        Loop that reads comport. Monitor reads in
        :return:
        """
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port

        while True:
            if UsbSerial._serialInst.inWaiting:
                try:
                    ln = UsbSerial._serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln) > 0:
                        UsbSerial._read_line = ln
                        if View.view_mode=='ADJUST':
                            UsbSerial.view_static.label_adjust_update(UsbSerial._read_line)
                            continue

                        if UsbSerial._parameters_needed > 0:
                            UsbSerial._parameter_list.append(UsbSerial._read_line)
                            UsbSerial.view_static.lbox_parameter.insert(tk.END, UsbSerial._read_line)
                            UsbSerial._parameters_needed -= 1
                        else:
                            UsbSerial.view_static.lbox_com_read_update(UsbSerial._read_line)
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

    @classmethod
    def m_get_ports(cls):
        """
        get a list of serial ports available on computer
        :return: portList
        """
        port_list = []
        ports = serial.tools.list_ports.comports(0)
        for onePort in ports:
            port_list.append(str(onePort))
        return port_list

    @classmethod
    def m_open_comport(cls, comport):
        if UsbSerial._status != 'OPEN':
            try:
                UsbSerial._serialInst.baudrate = 115200
                UsbSerial._serialInst.port = comport
                if UsbSerial._serialInst.isOpen():
                    try:
                        print("isopen")
                        UsbSerial._serialInst.close()
                    except Exception:
                        pass
                UsbSerial._serialInst.open()
                UsbSerial._status = "OPEN"
            except Exception:
                UsbSerial._status = 'ERROR'
        return UsbSerial._status


    ##########################################################
    @classmethod
    def start_init_com_statemachine(cls):

        init_com_thread = Thread(target=cls.init_com_statemachine_loop, daemon=True)

        init_com_thread.start()

    @classmethod
    def init_com_statemachine_loop(cls):
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
                UsbSerial.m_is_default_port_existing()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'EXISTING':
                UsbSerial.m_open()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'OPEN':
                UsbSerial.m_send_reset()
                time.sleep(1)
                continue
            elif UsbSerial.statemachine_state == 'WAIT_FOR_IDLE':
                UsbSerial._parameters_needed = 0
                UsbSerial.m_wait_for_idle()
                time.sleep(0.050)
                continue
            elif UsbSerial.statemachine_state == 'COM_READY':
                UsbSerial.m_com_ready()
            elif UsbSerial.statemachine_state == 'PASSIVE':
                time.sleep(1)
                continue
            elif UsbSerial.statemachine_state == "ERROR_COM":
                UsbSerial.m_error()
                time.sleep(0.200)

            else:
                raise Exception(f'Invalid state in state_machine: {UsbSerial.statemachine_state}')

    @classmethod
    def m_is_default_port_existing(cls):
        # Check if default COM port is existing on Computer
        UsbSerial.m_actport = UsbSerial.m_get_default_comport()
        UsbSerial.view_static.text_com_state.set(f'Connecting {UsbSerial.m_actport} ...')
        UsbSerial.available_ports = UsbSerial.m_get_ports()
        port_exists = False
        for port in UsbSerial.available_ports:
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

    @classmethod
    def m_open(cls):
        # try to open COM port on computer
        result = UsbSerial.m_open_comport(UsbSerial.m_actport)
        if result == 'OPEN':
            UsbSerial.statemachine_state = 'OPEN'
        else:
            UsbSerial.statemachine_state = 'ERROR_COM'
        return

    @classmethod
    def m_send_reset(cls):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if UsbSerial.write(chr(3)):
            UsbSerial.m_start_read_loop()  # enable receiver
            UsbSerial.statemachine_state = 'WAIT_FOR_IDLE'
            return True
        else:
            UsbSerial.statemachine_state = 'ERROR_COM'
            return False

    @classmethod
    def m_wait_for_idle(cls):
        # Wait for 'IDLE' from ESP32

        if UsbSerial._read_line == 'IDLE':
            UsbSerial.statemachine_state = 'COM_READY'
            return

        UsbSerial.statemachine_state = "ERROR_COM"
        return
    @classmethod
    def m_com_ready(cls):
        UsbSerial.view_static.button_select_adjust['state'] = tk.NORMAL
        UsbSerial.view_static.button_select_measure['state'] = tk.NORMAL
        UsbSerial.view_static.button_select_reset['state'] = tk.NORMAL
        UsbSerial.view_static.text_com_state.set(f'Connected {UsbSerial.m_actport}')

        # Get parameter and display in parameter_frame
        UsbSerial.view_static.controller.usb_serial_get_parameter_handle()
        UsbSerial.statemachine_state = 'PASSIVE'

    @classmethod
    def m_error(cls):
        UsbSerial.view_static.frame_select_com_on()
        available_ports = UsbSerial.m_get_ports()
        UsbSerial.view_static.display_comports(available_ports)

        UsbSerial._com_port_read_is_started = False
        if UsbSerial.view_static.com_selected != "":
            UsbSerial.m_put_default_comport(UsbSerial.view_static.com_selected)
            # UsbSerial.view_static.text_com_read_update(f'{UsbSerial.view_static.com_selected} selected')
            UsbSerial.view_static.frame_select_com_off()
            UsbSerial.statemachine_state = 'INIT'
            UsbSerial.view_static.com_selected = ""
            UsbSerial._com_port_read_is_started = False
