# Serial Communication with RTM
# Python Tutorial - How to Read Data from Arduino via Serial Port
# https://youtu.be/AHr94RtMj1A
# pip install pyserial
import pickle
import tkinter
from tkinter import messagebox

import serial.tools.list_ports
import serial
from threading import Thread


class UsbSerial:
    def __init__(self, view):
        self.portList = []
        self.comport = ""
        self.serialInst = serial.Serial()
        self.status = ""
        self.read_line = ""
        self.view = view
        self.com_port_read_is_started = False
        self.line_to_consume = ""
        self.parameters_needed = 0
        self.parameter_list = []
        self.sm_state="INIT"


    @staticmethod
    def m_get_comport_saved():
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except OSError:
            return ""

    @staticmethod
    def m_put_comport(comport):
        myvar = comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)

    def m_get_ports(self):
        """
        get a list of serial ports available on laptop
        :return: portList
        """
        self.portList = []
        ports = serial.tools.list_ports.comports(0)
        for onePort in ports:
            self.portList.append(str(onePort))
        return self.portList

    def m_open_comport(self, comport):
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

    def m_start_comport_read_thread(self):
        if self.com_port_read_is_started:
            return
        else:
            self.com_port_read_is_started = True
            print('start com_tread')
            com_thread = Thread(target=self.m_read_comport, daemon=True)
            com_thread.start()

    def m_read_comport(self):
        # https://youtu.be/AHr94RtMj1A
        # Python Tutorial - How to Read Data from Arduino via Serial Port
        print('read_comport starting')

        while True:
            if self.serialInst.inWaiting:
                try:
                    ln = self.serialInst.readline().decode('utf').rstrip('\n')
                    if len(ln) > 0:
                        self.read_line = ln
                        self.view.text_com_read_update(self.read_line)
                        self.view.text_adjust_update(self.read_line)
                        if self.parameters_needed > 0:
                            self.parameter_list.append(self.read_line)
                            self.parameters_needed -= 1



                except Exception:
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

    ##########################################################
    # State machine
    def m_is_default_port_existing(self):
        # Check if default COM port is existing on Computer
        self.act_port = self.m_get_comport_saved()
        self.view.text_com_state.set(f'Connecting {self.act_port} ...')
        available_ports = self.m_get_ports()
        port_exists = False
        for port in available_ports:
            r = self.act_port in port
            if r:
                port_exists = True
        if not port_exists:
            self.view.text_com_state.set(f'ERROR_COM {self.act_port} not available on Computer')
            self.sm_state = 'ERROR_COM'
            return
        else:
            self.sm_state = 'EXISTING'
            return

    def m_open(self):
        # try to open COM port on computer
        result = self.m_open_comport(self.act_port)
        if result == 'OPEN':
            self.sm_state = 'OPEN'
        else:
            self.sm_state = 'ERROR_COM'
        return

    def m_send_reset(self):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if self.write_comport(chr(3)):
            self.m_start_comport_read_thread()  # enable receiver
            self.sm_state = 'WAIT_FOR_IDLE'
        else:
            self.sm_state = 'ERROR_COM'

    def m_wait_for_idle(self):
        # Wait for 'IDLE' from ESP32

        if self.read_line == 'IDLE':
            self.sm_state = 'COM_READY'
            return

        self.sm_state = "ERROR_COM"
        return

    def m_com_ready(self):
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL
        self.view.text_com_state.set(f'Connected {self.act_port}')

    def m_error(self):
        self.view.frame_select_com_on()
        available_ports = self.m_get_ports()
        self.view.display_comports(available_ports)

        self.com_port_read_is_started = False
        if self.view.com_selected != "":
            self.m_put_comport(self.view.com_selected)
            # self.view.text_com_read_update(f'{self.view.com_selected} selected')
            self.view.frame_select_com_off()
            self.sm_state = 'INIT'
            self.view.com_selected = ""
            self.com_port_read_is_started = False

    def init_com(self):
        """
        Read default portnumber from flash. Open port, start receive loop. Send CTRL-C and wait for ESP32 response='IDLE'.
        On Error, open dialog to select other portnumber
        """
        self.view.text_status.set(self.sm_state)
        if self.sm_state == 'INIT':
            self.m_is_default_port_existing()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'EXISTING':
            self.m_open()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'OPEN':
            self.m_send_reset()
            self.view.trigger_state_machine_after(1000)
            return
        elif self.sm_state == 'WAIT_FOR_IDLE':
            self.m_wait_for_idle()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'COM_READY':
            self.m_com_ready()
        elif self.sm_state == "ERROR_COM":
            self.m_error()
            self.view.trigger_state_machine_after(200)

        else:
            raise Exception(f'Invalid state in state_machine: {self.sm_state}')
