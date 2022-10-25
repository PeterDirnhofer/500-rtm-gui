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
        self.m_old_comport_status = ""
        self.comport_status = ""
        self.is_connected=False
        self.act_port=""
        self.port_is_availabe=False

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

    def connect_com(self):
        if self.m_old_comport_status != self.comport_status:
            print(f"do_connection comport_status: {self.comport_status}")
        self.m_old_comport_status = self.comport_status
        self.view.text_com_port.set(f'{self.act_port}: {self.comport_status}')

        # check if default-comport is available on computer
        self.act_port = self.usb_serial.get_comport_saved()
        available_ports = self.usb_serial.get_ports()

        for port in available_ports:
            r = self.act_port in port
            if r==True:
                self.port_is_availabe=True

        if self.port_is_availabe==False:
            self.com_select_dialog()
            self.view.trigger_state_machine(500)
            return

        # try to open COM port on computer
        result = self.usb_serial.open_comport(self.act_port)


        if result != "OPEN":
            self.port_is_availabe=False
            self.usb_serial.put_comport('')
            self.com_select_dialog()
            self.view.trigger_state_machine(500)
            return


        print("wait for IDLE from ESP32")

        # Wait fir 'IDLE' from ESP32
        self.is_connected=True

        self.view.frame_select_com_off()

        #self.comport_status = "WAIT_FOR_IDLE"
        self.view.text_com_read_update('RESET')
        self.usb_serial.write_comport(chr(3))
        self.usb_serial.start_comport_read_thread()
        self.comport_status == "WAIT_FOR_IDLE"
        self.view.trigger_state_machine(500)

    def state_machine(self):

        print(f"Status: {self.comport_status}")
        if self.is_connected==False:
            self.connect_com()
            return

        #self.view.text_com_read_update(f'status: {self.comport_status}')
        #self.view.text_com_read_update('WAIT_FOR_IDLE')
        if self.comport_status == "WAIT_FOR_IDLE":
            if self.usb_serial.read_line == 'IDLE':
                self.comport_status = "IDLE"
                self.view.button_select_adjust['state'] = tkinter.NORMAL


        elif self.comport_status == "ADJUST":
            self.view.text_adjust["text"] = "lghlug"

        self.view.trigger_state_machine(1000)

    def select_measure(self):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        # send restart to ESP32

        self.usb_serial.write_comport(chr(3))
        self.view.lb_com_read_delete()
        self.view.text_com_read_update('RESET')
        self.m_old_comport_status = ""
        self.comport_status = "WAIT_FOR_IDLE"

        os.execv(__file__, sys.argv)

    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED
        if (self.comport_status != "IDLE"):
            showinfo(
                title='Information',
                message=f"STM not connected\nCOM port Status 'READY' needed\n Status is {self.comport_status}"
            )
            return

        self.usb_serial.write_comport('ADJUST')
        self.view.frame_adjust_on()
        self.comport_status = "ADJUST"


if __name__ == '__main__':
    test = ""
    rtm = Controller()
    rtm.main()
