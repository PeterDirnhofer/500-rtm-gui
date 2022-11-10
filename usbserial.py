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


class UsbSerial:
    # Class variables
    available_ports = None
    view_reference = None
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
    def set_com_selected(cls, com):
        cls._com_selected = com

    @classmethod
    def get_com_selected(cls):
        return cls._com_selected

    @classmethod
    def start_com_esp32_loop(cls):
        """
        Start thread with _init_com_statemachine_loop to connect to ESP32. Status is monitored in view
        :return:
        """
        if cls.view_reference is not None:
            init_com_thread = Thread(target=cls._com_esp32_loop, daemon=True)
            init_com_thread.start()
            return True
        print("ERRROR run cls.view_reference,view")
        return False

    @classmethod
    def _com_esp32_loop(cls):
        """
        Statemachine to open communication wit ESP32.
        - Open COM for sending and receiving
        - Send CRTL-C to ESP32 -Wait for ESP32 response 'IDLE'
        - Request parameters from ESP32 and render in Frame parameters
        """
        last_state = 'LAST'
        while True:

            if cls._statemachine_state != last_state:
                last_state = cls._statemachine_state
                cls.view_reference.text_status.set(cls._statemachine_state)

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
                cls._request_parametes()
                continue

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
        """ Read ESP32 in a thread loop and write readings to queue.

        :raises Errormessage and stop program if connection to ESP32 is lost.
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
                        cls.view_reference.queue_available.set(len)

                except Exception as e:
                    messagebox.showerror('Error. Connection lost to ESP32', f'Close the programm\nError detail: \n{e}')
                    cls.view_reference.close()

    @classmethod
    def write(cls, cmd: str):
        """ Send command to ESP32.

        :param cmd: Command to send
        :return: False if send not ok
        """
        cls._serialInst.write_timeout = 1.0

        try:
            cls._serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception as e:
            messagebox.showerror(f"Error send to ESP32\n{str(e)}")
            return False

    @classmethod
    def request_parameter_from_esp(cls):
        """ Send request for parameter reading to ESP

        """
        cls.view_reference.lbox_parameter.delete(0, tk.END)  # Clear lbox with old parameters
        cls.write('PARAMETER,?')  # Send reqest or ESP

    @staticmethod
    def _get_default_comport() -> str:
        """ Read last used comport from pickle file.

        :return: 'COMx'
        """
        try:
            with open('data/comport.pkl', 'rb') as file:
                port = pickle.load(file)
                return port
        except OSError:
            return ""

    @staticmethod
    def _put_default_comport(port: str):
        """Write default COM Port to pickle file comport.pkl"""
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(port, file)

    @classmethod
    def _get_ports(cls) -> list[str]:
        """
        Get a list of serial ports actually available on computer.
        
        :return: port_list
        """
        port_list = []
        ports = serial.tools.list_ports.comports(0)
        for onePort in ports:
            port_list.append(str(onePort))
        return port_list

    @classmethod
    def _is_default_port_existing(cls):
        """ Check if requested port is available on computer.
        Set statemachine_state to 'EXISTING' or 'ERROR_COM'
        """
        # Check if default COM port is existing on Computer
        cls._actport = cls._get_default_comport()
        cls.view_reference.text_com_state.set(f'Connecting {cls._actport} ...')
        cls.available_ports = cls._get_ports()
        port_exists = False
        for port in cls.available_ports:
            r = cls._actport in port
            if r:
                port_exists = True
        if not port_exists:
            cls.view_reference.text_com_state.set(f'ERROR_COM {cls._actport} not available on Computer')
            cls._statemachine_state = 'ERROR_COM'
            return
        else:
            cls._statemachine_state = 'EXISTING'
            return

    @classmethod
    def _open(cls):
        """ Open COM  _actport.

        :return: Set _statemachine_state = 'OPEN' or 'ERROR_COM'
        """

        # if comport already open (after RESET)  skip open and set _statemachine_state = 'OPEN'
        if cls._comport_is_open:
            cls._statemachine_state = 'OPEN'
            return

        # If not open, try to open _actport
        try:
            cls._serialInst.baudrate = 115200
            cls._serialInst.port = cls._actport
            if cls._serialInst.isOpen():
                try:
                    print("isopen")
                    cls._serialInst.close()
                except Exception:
                    pass
            cls._serialInst.open()
            cls._comport_is_open = "OPEN"
        except Exception:
            cls._comport_is_open = 'ERROR_COM'

        cls._statemachine_state = cls._comport_is_open

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
            cls.view_reference.text_com_state.set(f'Connected to {cls._actport}')

            return

        cls._statemachine_state = "ERROR_COM"
        return

    @classmethod
    def _request_parametes(cls):
        """Request parameters from ESP32 by sending 'PARAMETER,? to ESP32.
        Set statemachine to 'PASSIVE'"""
        # Get parameter and display in parameter_frame
        cls.request_parameter_from_esp()
        cls._statemachine_state = 'PASSIVE'

    @classmethod
    def _error(cls):
        cls.view_reference.frame_select_com_on()
        available_ports = cls._get_ports()
        cls.view_reference.display_comports(available_ports)

        cls._com_port_read_is_started = False
        if cls._com_selected != "":
            cls._put_default_comport(cls._com_selected)
            cls.view_reference.frame_select_com_off()
            cls._statemachine_state = 'INIT'
            cls._com_selected = ""
            cls._com_port_read_is_started = False
