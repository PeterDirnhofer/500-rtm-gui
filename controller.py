# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
import os
import sys
import tkinter
from tkinter.messagebox import showinfo

from model import Model
from usb_serial import Usb_serial
from view import View



# Timer Class https://youtu.be/5NJ9cc0dnCM
class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View
        self.usb_serial = Usb_serial(self, self.view)

        self.comport_status = ""
        self.comport_state=""
        self.is_connected=False
        self.act_port=""
        self.sm_state= 'INIT'

    def main(self):
        self.view.main()

    def com_select_dialog(self):
        self.is_connected = False
        self.view.frame_select_com_on()
        available_ports = self.usb_serial.get_ports()
        self.view.display_comports(available_ports)

        if self.view.com_selected != "":
            self.usb_serial.put_comport(self.view.com_selected)
            self.view.text_com_read_update(f'{self.view.com_selected} selected')
        return

    def sm_is_default_port_existing(self):
        self.act_port = self.usb_serial.get_comport_saved()
        available_ports = self.usb_serial.get_ports()
        port_exists = False
        for port in available_ports:
            r = self.act_port in port
            if r == True:
                port_exists = True
        if port_exists == False:
            self.sm_state='ERROR'
            return
        else:
            self.sm_state='EXISTING'
            return


    def sm_open(self):
        # try to open COM port on computer
        result = self.usb_serial.open_comport(self.act_port)
        if result == 'OPEN':
            self.sm_state='OPEN'
        else:
            self.sm_state='ERROR'
        return

    def sm_send_reset(self):
        if self.usb_serial.write_comport(chr(3))==True:
            self.usb_serial.start_comport_read_thread()  # enable receiver
            self.sm_state = 'WAIT_FOR_IDLE'
        else:
            self.sm_state = 'ERROR'

    def sm_wait_for_idle(self):
        if self.usb_serial.read_line=='IDLE':
            self.sm_state='COM_READY'
        else:
            self.sm_state = 'ERROR'



    def state_machine(self):

        if self.sm_state== 'INIT':
            self.sm_is_default_port_existing()
            self.view.trigger_state_machine(50)
            return
        elif self.sm_state== 'EXISTING':
            self.sm_open()
            self.view.trigger_state_machine(50)
            return
        elif self.sm_state== 'OPEN':
            self.sm_send_reset()
            self.view.trigger_state_machine(1000)
            return
        elif self.sm_state== 'WAIT_FOR_IDLE':
            self.sm_wait_for_idle()
            self.view.trigger_state_machine(50)
            return
        elif self.sm_state== 'COM_READY':
            # state machin no longer needed. No retrigger
            pass
        elif self.sm_state== "ERROR":
            self.view.text_status.set("ERROR !!!!!!!!!!!!!!!!!")
            pass
        else:
            raise Exception(f'Invalid state: {self.sm_state}')

        #self.view.trigger_state_machine(50)

    def connect_com(self):

        # check if default-comport is available on computer
        self.act_port = self.usb_serial.get_comport_saved()
        available_ports = self.usb_serial.get_ports()

        port_exists=False
        for port in available_ports:
            r = self.act_port in port
            if r==True:
                port_exists=True


        if port_exists==False:
            self.view.text_com_state.set(f'{self.act_port} is not available on Computer')
            self.com_select_dialog()
            return 'NO_CONNECT'

        # try to open COM port on computer
        result = self.usb_serial.open_comport(self.act_port)

        if result != "OPEN":
            self.view.text_com_state.set(f"ERROR opening {self.act_port} ")
            self.port_is_availabe=False
            self.usb_serial.put_comport('')
            self.com_select_dialog()
            return 'NO_CONNECT'

        # Now COM port is open. Check if port can be accessed
        if self.usb_serial.write_comport(chr(3)) == False:
            self.view.text_com_state.set(f'Cannot send on port {self.act_port}')
            self.com_select_dialog()
            return 'NO_CONNECT'

        # Send COM was ok, Wait for IDLE
        self.view.frame_select_com_off()
        #self.view.text_com_read_update('RESET WAIT_FOR_IDLE')
        self.usb_serial.start_comport_read_thread()
        #self.comport_status == "WAIT_FOR_IDLE"
        self.view.text_com_state.set(f'{self.act_port} connected')
        self.is_connected=True


        return 'CONNECTED'

    def state_machine1(self):

        print(f"Status: {self.comport_status}")
        if self.is_connected==False:
            if self.connect_com()=='CONNECTED':
                self.comport_status == "WAIT_FOR_IDLE"
                self.view.button_select_adjust['state'] = tkinter.NORMAL
                self.view.button_select_measure['state'] = tkinter.NORMAL
                self.view.button_select_reset['state'] = tkinter.NORMAL


            else:
                self.view.trigger_state_machine(50)
            return

    def select_measure(self):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL

        # send restart to ESP32

        self.usb_serial.write_comport(chr(3))
        self.view.lb_com_read_delete()
        self.view.text_com_read_update('RESET')
        self.m_old_comport_status = ""
        self.comport_status = "WAIT_FOR_IDLE"
        self.is_connected=False

        os.execv(__file__, sys.argv)

    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED

        self.usb_serial.write_comport('ADJUST')
        self.view.frame_adjust_on()
        self.comport_status = "ADJUST"


if __name__ == '__main__':
    test = ""
    rtm = Controller()
    rtm.main()
