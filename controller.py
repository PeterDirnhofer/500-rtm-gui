# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk

import tkinter

from usbserial import UsbSerial
from view import View
from model import Model

from configurations import *
from measure import *


# Timer Class https://youtu.be/5NJ9cc0dnCM
class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View
        self.measure= Measure(self.view, self.model)

        UsbSerial.view_ptr = self.view  # pass view to UsbSerial
        UsbSerial.reset_com_esp32()

    def main(self):
        # Start statemachine in background to connect with ESP32 over USB interface
        UsbSerial.start_com_esp32_loop()

        self.view.main()

    def select_measure(self):
        #self.view.plotter(data)
        if self.measure.start_measure_cycle != False:
            return

        # data = self.model.get_data_from_scan(SCAN_FILE_NAME)

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        self.view.frame_measure_off()
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL

        UsbSerial.write(chr(3))

        self.view.lbox_com_read_delete()
        self.view.lbox_com_read_update('RESET')

        self.view.lbox_parameter_delete()

        UsbSerial.reset_com_esp32()

    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED
        self.view.button_select_measure['state'] = tkinter.DISABLED

        UsbSerial.write('ADJUST')
        self.view.frame_measure_off()
        self.view.frame_adjust_on()

        self.view.text_status.set('ADJUST')




if __name__ == '__main__':
    app = Controller()
    app.main()
