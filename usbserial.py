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

from queue import Queue


class UsbSerial():
    # Class variables
    view_static = None
    _statemachine_state = "INIT"
    _serialInst = serial.Serial()
    _comport_is_open = ""
    _read_line = ""
    _com_port_read_is_started = False
    _actport = None
    queue = Queue()
    _com_selected = ""

    #############################################
    # Statemachine connect to ESP32
    @classmethod
    def reset_com_esp32(cls):
        cls._statemachine_state = 'INIT'

    @classmethod
    def start_init_com_esp32(cls):
        """
        Start thread with _init_com_statemachine_loop to connect to ESP32. Status is monitored in view
        :return:
        """
        if cls.view_static == None:
            print("ERRROR run cls.view_static=view")
            return False
        init_com_thread = Thread(target=cls._init_com_statemachine_loop, daemon=True)
        init_com_thread.start()
        return True

    @classmethod
    def _init_com_statemachine_loop(cls):
        '''
        Statemachine to open comunication wit ESP32. -Open COM -Send CRTL-C Reset to ESP32 -Wait for ESP32 response 'IDLE'
        - Request parameters from ESP32 and render in Frame parameters
        '''
        last_state = 'LAST'
        while True:

            if cls._statemachine_state != last_state:
                last_state = cls._statemachine_state
                cls.view_static.text_status.set(cls._statemachine_state)

            if cls._statemachine_state == 'INIT':
                cls._is_default_port_existing()
                time.sleep(0.050)
                continue
            elif cls._statemachine_state == 'EXISTING':
                cls._open()
                time.sleep(0.050)
                continue
            elif cls._statemachine_state == 'OPEN':
                cls._send_reset()
                time.sleep(1)
                continue
            elif cls._statemachine_state == 'WAIT_FOR_IDLE':

                cls._wait_for_idle()
                time.sleep(0.050)
                continue
            elif cls._statemachine_state == 'COM_READY':
                cls._com_ready()
            elif cls._statemachine_state == 'PASSIVE':
                time.sleep(1)
                continue
            elif cls._statemachine_state == "ERROR_COM":
                cls._error()
                time.sleep(0.200)

            else:
                raise Exception(f'Invalid state in state_machine: {cls._statemachine_state}')

    ####################################################################
    # COM READ THREAD
    @classmethod
    def _start_read_loop(cls):
        if cls._com_port_read_is_started:
            return
        else:
            cls._com_port_read_is_started = True
            com_thread = Thread(target=cls._read_loop, daemon=True)
            com_thread.start()

    @classmethod
    def _read_loop(cls):
        """Read ESP32 com port and put to queue
        Read ESP32 com port in a thread loop. Output: Put read lines to queue. And put last input to _read_line.
        """
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port

        while True:
            if cls._serialInst.inWaiting:
                try:
                    ln = cls._serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln) > 0:
                        cls._read_line = ln
                        cls.queue.put(ln)

                except Exception:
                    messagebox.showerror('error', 'Connection lost\nClose the programm')
                    cls.view_static.close()

    @classmethod
    def write(cls, cmd):
        cls._serialInst.write_timeout = 1.0

        try:
            cls._serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False

    @classmethod
    def request_parameter_from_esp(cls):
        """
        Trigger reading NUMBER_OF_PARAMETERS parameters in m_read_loop to m_parameter_list
        """
        cls.view_static.lbox_parameter.delete(0, tk.END)

        cls.write('PARAMETER,?')

    @staticmethod
    def _get_default_comport():
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
    def _put_default_comport(comport):
        '''Write default COM Port to file comport.pkl'''
        myvar = comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    @classmethod
    def _get_ports(cls):
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
    def _open_comport(cls, comport):
        if cls._comport_is_open != 'OPEN':
            try:
                cls._serialInst.baudrate = 115200
                cls._serialInst.port = comport
                if cls._serialInst.isOpen():
                    try:
                        print("isopen")
                        cls._serialInst.close()
                    except Exception:
                        pass
                cls._serialInst.open()
                cls._comport_is_open = "OPEN"
            except Exception:
                cls._comport_is_open = 'ERROR'
        return cls._comport_is_open

    @classmethod
    def _is_default_port_existing(cls):
        # Check if default COM port is existing on Computer
        cls._actport = cls._get_default_comport()
        cls.view_static.text_com_state.set(f'Connecting {cls._actport} ...')
        cls.available_ports = cls._get_ports()
        port_exists = False
        for port in cls.available_ports:
            r = cls._actport in port
            if r:
                port_exists = True
        if not port_exists:
            cls.view_static.text_com_state.set(f'ERROR_COM {cls._actport} not available on Computer')
            cls._statemachine_state = 'ERROR_COM'
            return
        else:
            cls._statemachine_state = 'EXISTING'
            return

    @classmethod
    def _open(cls):
        # try to open COM port on computer
        result = cls._open_comport(cls._actport)
        if result == 'OPEN':
            cls._statemachine_state = 'OPEN'
        else:
            cls._statemachine_state = 'ERROR_COM'
        return

    @classmethod
    def _send_reset(cls):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if cls.write(chr(3)):
            cls._start_read_loop()  # enable receiver
            cls._statemachine_state = 'WAIT_FOR_IDLE'
            return True
        else:
            cls._statemachine_state = 'ERROR_COM'
            return False

    @classmethod
    def _wait_for_idle(cls):
        # Wait for 'IDLE' from ESP32

        if cls._read_line == 'IDLE':
            cls._statemachine_state = 'COM_READY'
            return

        cls._statemachine_state = "ERROR_COM"
        return

    @classmethod
    def _com_ready(cls):
        # Get parameter and display in parameter_frame
        cls.request_parameter_from_esp()
        cls._statemachine_state = 'PASSIVE'

    @classmethod
    def _error(cls):
        cls.view_static.frame_select_com_on()
        available_ports = cls._get_ports()
        cls.view_static.display_comports(available_ports)

        cls._com_port_read_is_started = False
        if cls._com_selected != "":
            cls._put_default_comport(cls._com_selected)
            cls.view_static.frame_select_com_off()
            cls._statemachine_state = 'INIT'
            cls._com_selected = ""
            cls._com_port_read_is_started = False
