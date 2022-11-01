# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
import time
import tkinter

from tkinter.messagebox import showinfo

from model import Model
from usbserial import UsbSerial
from view import View


# Timer Class https://youtu.be/5NJ9cc0dnCM
class Controller:
    def __init__(self):
        self.port_is_available = False
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View
        self.usb_serial = UsbSerial(self.view)  # instance of view is passed to UsbSerial
        self.act_port = ""
        self.usb_serial.m_sm_state = 'INIT'

    def main(self):
        self.view.main()

    def usb_serial_get_parameter_handle(self):
        self.usb_serial.get_parameter()

    @staticmethod
    def select_measure():
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def usb_serial_trigger_new_statemachine_handle(self):
        self.usb_serial.start_init_com_statemachine()

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL

        self.usb_serial.write(chr(3))
        self.view.lb_com_read_delete()
        self.view.lbox_com_read_update('RESET')
        self.view.lbox_parameter_delete()

        self.usb_serial.m_sm_state = 'INIT'

    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED
        self.view.button_select_measure['state'] = tkinter.DISABLED

        self.usb_serial.write('ADJUST')
        self.view.frame_adjust_on()

        self.view.text_status.set('ADJUST')


if __name__ == '__main__':
    app = Controller()
    app.main()
