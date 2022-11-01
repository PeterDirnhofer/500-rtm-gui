# Serial Communication with RTM
# Python Tutorial - How to Read Data from Arduino via Serial Port
# https://youtu.be/AHr94RtMj1A
# pip install pyserial
import pickle
import tkinter as tk
from tkinter import messagebox

import serial.tools.list_ports
import serial
from threading import Thread

NUMBER_OF_PARAMETERS = 10


class UsbSerial:
    def __init__(self, view):
        self.serialInst = serial.Serial()
        self.m_status = ""
        self.m_read_line = ""
        self.view = view
        self.m_com_port_read_is_started = False
        self.m_line_to_consume = ""
        self.parameters_needed = 0
        self.m_parameter_list = []
        self.m_sm_state = "INIT"
        self.m_actport = ""

    def init_com_statemachine(self):

        """
        Initialize PC COM Port to ESP32.
        Read default portnumber from flash. Open port, start receive loop.
        Send CTRL-C and wait for ESP32 response='IDLE'.
        On Error, open dialog to select other portnumber
        """
        self.view.text_status.set(self.m_sm_state)
        if self.m_sm_state == 'INIT':
            self.m_is_default_port_existing()
            self.view.trigger_state_machine_after(50)
            return
        elif self.m_sm_state == 'EXISTING':
            self.m_open()
            self.view.trigger_state_machine_after(50)
            return
        elif self.m_sm_state == 'OPEN':
            self.m_send_reset()
            self.view.trigger_state_machine_after(1000)
            return
        elif self.m_sm_state == 'WAIT_FOR_IDLE':
            self.parameters_needed = 0
            self.m_wait_for_idle()
            self.view.trigger_state_machine_after(50)
            return
        elif self.m_sm_state == 'COM_READY':
            self.m_com_ready()
        elif self.m_sm_state == "ERROR_COM":
            self.m_error()
            self.view.trigger_state_machine_after(200)

        else:
            raise Exception(f'Invalid state in state_machine: {self.m_sm_state}')

    def write(self, cmd):
        self.serialInst.write_timeout = 1.0

        try:
            self.serialInst.write(f'{cmd}\n'.encode('utf'))
            return True
        except Exception:
            return False

    def get_parameter(self):
        """
        Trigger reading NUMBER_OF_PARAMETERS parameters in m_read_loop to m_parameter_list
        """
        self.view.tbox_parameter.delete(0, tk.END)
        self.m_parameter_list.clear()
        self.parameters_needed = NUMBER_OF_PARAMETERS
        self.write('PARAMETER,?')

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
            if self.serialInst.inWaiting:
                try:
                    ln = self.serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln) > 0:
                        self.m_read_line = ln
                        if self.parameters_needed > 0:
                            self.m_parameter_list.append(self.m_read_line)
                            self.view.tbox_parameter.insert(tk.END, self.m_read_line)
                            self.parameters_needed -= 1
                        else:
                            self.view.lbox_com_read_update(self.m_read_line)
                            self.view.label_adjust_update(self.m_read_line)


                except Exception:
                    messagebox.showerror('error', 'Connection lost\nClose the programm')
                    self.view.close()

    @staticmethod
    def m_get_default_comport():
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except OSError:
            return ""

    @staticmethod
    def m_put_default_comport(comport):
        myvar = comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    def m_get_ports(self):
        """
        get a list of serial ports available on laptop
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
                self.serialInst.baudrate = 115200
                self.serialInst.port = comport
                if self.serialInst.isOpen():
                    try:
                        print("isopen")
                        self.serialInst.close()
                    except Exception:
                        pass
                self.serialInst.open()
                self.m_status = "OPEN"
            except Exception:
                self.m_status = 'ERROR'
        return self.m_status

    ##########################################################
    # State machine
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
            self.m_sm_state = 'ERROR_COM'
            return
        else:
            self.m_sm_state = 'EXISTING'
            return

    def m_open(self):
        # try to open COM port on computer
        result = self.m_open_comport(self.m_actport)
        if result == 'OPEN':
            self.m_sm_state = 'OPEN'
        else:
            self.m_sm_state = 'ERROR_COM'
        return

    def m_send_reset(self):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if self.write(chr(3)):
            self.m_start_read_loop()  # enable receiver
            self.m_sm_state = 'WAIT_FOR_IDLE'
        else:
            self.m_sm_state = 'ERROR_COM'

    def m_wait_for_idle(self):
        # Wait for 'IDLE' from ESP32

        if self.m_read_line == 'IDLE':
            self.m_sm_state = 'COM_READY'
            return

        self.m_sm_state = "ERROR_COM"
        return

    def m_com_ready(self):
        self.view.button_select_adjust['state'] = tk.NORMAL
        self.view.button_select_measure['state'] = tk.NORMAL
        self.view.button_select_reset['state'] = tk.NORMAL
        self.view.text_com_state.set(f'Connected {self.m_actport}')

        # Get parameter and display in parameter_frame
        self.view.controller.usb_serial_get_parameter_handle()

    def m_error(self):
        self.view.frame_select_com_on()
        available_ports = self.m_get_ports()
        self.view.display_comports(available_ports)

        self.m_com_port_read_is_started = False
        if self.view.com_selected != "":
            self.m_put_default_comport(self.view.com_selected)
            # self.view.text_com_read_update(f'{self.view.com_selected} selected')
            self.view.frame_select_com_off()
            self.m_sm_state = 'INIT'
            self.view.com_selected = ""
            self.m_com_port_read_is_started = False
