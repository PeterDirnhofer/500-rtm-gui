# Serial Communication with RTM
# Python Tutorial - How to Read Data from Arduino via Serial Port
# https://youtu.be/AHr94RtMj1A
# pip install pyserial
import pickle
import time
import tkinter as tk
from queue import Queue
from threading import Thread
from tkinter import messagebox

import serial
import serial.tools.list_ports

from model import *


class UsbSerial:
    # Class variables
    available_ports: [str] = None
    view_ptr = None
    _statemachine_state: str = "INIT"
    _serialInst = serial.Serial()
    _comport_is_open: str = ""
    _read_line: str = ""
    _com_port_read_is_started: bool = False
    _act_port: str = None
    queue: Queue[str] = Queue()
    _com_selected: str = ""

    #############################################
    # Statemachine connect to ESP32
    @classmethod
    def reset_com_esp32(cls):
        cls._statemachine_state = 'INIT'

    @classmethod
    def set_com_selected(cls, com: str):
        cls._com_selected = com

    @classmethod
    def get_com_selected(cls):
        return cls._com_selected

    @classmethod
    def start_com_esp32_loop(cls) -> bool:
        """
        Start thread with _init_com_statemachine_loop to connect to ESP32. Status is monitored in view
        :return:
        """
        if cls.view_ptr is not None:
            init_com_thread = Thread(target=cls._start_com_esp32_loop, daemon=True)
            init_com_thread.start()
            return True
        print("ERROR run cls.view_reference,view")
        return False

    @classmethod
    def _start_com_esp32_loop(cls):
        """
        Statemachine to establish communication wit ESP32.
        - Open COM for sending and receiving
        - Send CTRL-C to ESP32 -Wait for ESP32 response 'IDLE'
        - Request parameters from ESP32 and render in Frame parameters
        - This method uses view to display status or get COM port in a dialog if needed
        """
        last_state = 'LAST'
        while True:
            # while cls._statemachine_state != 'PASSIVE':
            if cls._statemachine_state != last_state:
                last_state = cls._statemachine_state
                cls.view_ptr.text_status.set(cls._statemachine_state)

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
                time.sleep(1)  # Wait 1 Second until ESP has finished old protocol e.g. Parameters
                continue

            elif cls._statemachine_state == 'WAIT_FOR_IDLE':
                cls._wait_for_idle()
                time.sleep(0.050)
                continue

            elif cls._statemachine_state == 'COM_READY':
                cls._request_parameters()
                time.sleep(0.5)
                continue

            elif cls._statemachine_state == 'PASSIVE':
                time.sleep(0.3)
                continue

            elif cls._statemachine_state == "ERROR_COM":
                cls._error()
                time.sleep(0.200)

            else:
                raise Exception(f'Invalid state in state_machine: {cls._statemachine_state}')

    ####################################################################
    # start ESP32 COM READ THREAD
    @classmethod
    def _start_read_loop(cls):
        if cls._com_port_read_is_started:
            return
        else:
            cls._com_port_read_is_started = True
            com_thread = Thread(target=cls._read_loop, daemon=True)
            com_thread.start()

    @classmethod
    def _read_loop(cls) -> None:
        """ Polling ESP32 in a thread loop and put readings to 'queue'.
        Signaling to view that data are available by setting the tk.IntVar 'queue_available'
        """
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port

        while True:
            if cls._serialInst.inWaiting:
                try:
                    ln = cls._serialInst.readline().decode('utf').rstrip('\n')

                    # data from ESP32 available
                    if len(ln) > 0:
                        cls._read_line = ln

                        # If data from measure, save
                        ln_split = ln.split(",")

                        if ln_split[0] == "DATA":
                            if ln_split[1] == 'DONE':
                                Model.dataframe_to_csv()
                                cls.view_ptr.text_status.set("Data saved in " + SCAN_FILE_NAME)

                            Model.write_to_dataframe(ln)
                            continue

                        # put received data from ESP32 to queue
                        cls.queue.put(ln)

                        # signal that data are available to queue
                        cls.view_ptr.queue_available.set(len)


                except Exception as e:
                    messagebox.showerror('Error. Connection lost to ESP32', f'Close the program\nError detail: \n{e}')
                    cls.view_ptr.on_closing()

    @classmethod
    def write(cls, cmd: str) -> bool:
        """ Send command to ESP32.
        :param cmd: Command to send as string
        :return: False if not ok
        """
        cls._serialInst.write_timeout = 1.0

        try:
            cls._serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception as e:
            messagebox.showerror(f"Error send to ESP32\n{str(e)}")
            return False

    @classmethod
    def request_parameter_from_esp(cls) -> None:
        """ Send request for parameter reading to ESP
        """
        cls.view_ptr.lbox_parameter.delete(0, tk.END)  # Clear listbox with old parameters
        cls.write('PARAMETER,?')  # Send request or ESP

    @staticmethod
    def _get_default_comport_nvm() -> str:
        """ Read last used comport from pickle file.

        :return: 'COMx'
        """
        try:
            with open(COMPORT_PICKLE_FILE, 'rb') as file:
                port = pickle.load(file)
                return port
        except OSError:
            return ""

    @staticmethod
    def _put_default_comport_nvm(port: str):
        """Write default COM Port to pickle file comport.pkl"""
        with open(COMPORT_PICKLE_FILE, 'wb') as file:
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
        cls._act_port = cls._get_default_comport_nvm()
        cls.view_ptr.text_com_state.set(f'Connecting {cls._act_port} ...')
        cls.available_ports = cls._get_ports()
        port_exists = False
        for port in cls.available_ports:
            r = cls._act_port in port
            if r:
                port_exists = True
        if not port_exists:
            cls.view_ptr.text_com_state.set(f'ERROR_COM {cls._act_port} not available on Computer')
            cls._statemachine_state = 'ERROR_COM'
            return
        else:
            cls._statemachine_state = 'EXISTING'
            return

    @classmethod
    def _open(cls):
        """ Open COM  _act_port.

        :return: Set _statemachine_state = 'OPEN' or 'ERROR_COM'
        """

        # if comport already open (after RESET)  skip open and set _statemachine_state = 'OPEN'
        if cls._comport_is_open:
            cls._statemachine_state = 'OPEN'
            return

        # If not open, try to open _act_port
        # noinspection PyBroadException
        try:
            cls._serialInst.baudrate = 115200
            cls._serialInst.port = cls._act_port
            if cls._serialInst.isOpen():
                # noinspection PyBroadException
                try:
                    print("is open")
                    cls._serialInst.close()
                except Exception:
                    pass
            cls._serialInst.open()
            cls._comport_is_open = "OPEN"
        except Exception:
            cls._comport_is_open = 'ERROR_COM'

        cls._statemachine_state = cls._comport_is_open

    @classmethod
    def _send_reset(cls) -> bool:
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
            cls.view_ptr.text_com_state.set(f'Connected to {cls._act_port}')

            return

        cls._statemachine_state = "ERROR_COM"
        return

    @classmethod
    def _request_parameters(cls):
        """Request parameters from ESP32 by sending 'PARAMETER,?' to ESP32.
        Set statemachine to 'PASSIVE'"""
        # Get parameter and display in parameter_frame
        cls.request_parameter_from_esp()
        cls._statemachine_state = 'PASSIVE'

    @classmethod
    def _error(cls):
        cls.view_ptr.frame_select_com_on()
        available_ports = cls._get_ports()
        cls.view_ptr.display_comports(available_ports)

        cls._com_port_read_is_started = False
        if cls._com_selected != "":
            cls._put_default_comport_nvm(cls._com_selected)
            cls.view_ptr.frame_select_com_off()
            cls._statemachine_state = 'INIT'
            cls._com_selected = ""
            cls._com_port_read_is_started = False
