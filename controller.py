# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk

import tkinter
from tkinter.messagebox import showinfo


from usbserial import UsbSerial
from view import View
from model import Model


# Timer Class https://youtu.be/5NJ9cc0dnCM
class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View

        UsbSerial.view_reference = self.view  # pass view to UsbSerial
        UsbSerial.reset_com_esp32()

    def main(self):
        # Start statemachine in background to connect with ESP32 over USB interface
        UsbSerial.start_com_esp32_loop()

        self.view.main()


    def select_measure(self):

        file_name = "plot_data/newScan.csv"
        data = self.model.get_data_from_scan(file_name)
        self.view.plotter(data)

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL

        UsbSerial.write(chr(3))

        self.view.lb_com_read_delete()
        self.view.lbox_com_read_update('RESET')

        self.view.lbox_parameter_delete()

        UsbSerial.reset_com_esp32()

    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED
        self.view.button_select_measure['state'] = tkinter.DISABLED

        UsbSerial.write('ADJUST')
        self.view.frame_adjust_on()

        self.view.text_status.set('ADJUST')


if __name__ == '__main__':
    app = Controller()
    app.main()
