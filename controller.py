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
        self.comport_status = "INIT"
        self.is_connected=False
        self.act_port=""
        self.port_is_availabe=False

    def main(self):

        self.view.main()

    def com_select_dialog(this):
        this.is_connected = False
        this.view.frame_select_com_on()
        available_ports = this.usb_serial.get_ports()
        this.view.display_comports(available_ports)

        if this.view.com_selected != "":
            this.usb_serial.put_comport(this.view.com_selected)
            this.view.text_com_read_update(f'{this.view.com_selected} selected')
        return

    def connect_com(this):

        if this.m_old_comport_status != this.comport_status:
            print(f"do_connection comport_status: {this.comport_status}")
        this.m_old_comport_status = this.comport_status
        this.view.text_com_port.set(f'{this.act_port}: {this.comport_status}')

        # check if default-comport is available on computer
        this.act_port = this.usb_serial.get_comport_saved()
        available_ports = this.usb_serial.get_ports()

        for port in available_ports:
            r = this.act_port in port
            if r==True:
                this.port_is_availabe=True

        if this.port_is_availabe==False:
            this.com_select_dialog()
            this.view.trigger_state_machine(500)
            return

        # try to open COM port on computer
        result = this.usb_serial.open_comport(this.act_port)


        if result != "OPEN":
            this.port_is_availabe=False
            this.usb_serial.put_comport('')
            this.com_select_dialog()
            this.view.trigger_state_machine(500)
            return


        print("wait for IDLE from ESP32")

        # Wait fir 'IDLE' from ESP32
        this.is_connected=True

        this.view.frame_select_com_off()

        this.comport_status = "WAIT_FOR_IDLE"
        this.view.text_com_read_update('RESET')
        this.usb_serial.write_comport(chr(3))
        this.usb_serial.start_comport_read_thread()

    def state_machine(this):

        print(f"Status: {this.comport_status}")
        if this.is_connected==False:
            this.connect_com()
            return

        # if this.comport_status == "INIT":
        #     result = this.usb_serial.open_comport(this.act_port)
        #     this.view.text_status.set(result)
        #     # Cannot find COM PORT
        #     return


        if this.comport_status == "WAIT_FOR_IDLE":

            if this.usb_serial.read_line == 'IDLE':
                this.comport_status = "IDLE"
                this.view.button_select_adjust['state'] = tkinter.NORMAL


        elif this.comport_status == "ADJUST":
            this.view.text_adjust["text"] = "lghlug"

        this.view.trigger_state_machine(1000)

    def select_measure(this):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def select_restart(this):
        this.view.frame_select_com_off()
        this.view.frame_adjust_off()
        # send restart to ESP32

        this.usb_serial.write_comport(chr(3))
        this.view.lb_com_read_delete()
        this.view.text_com_read_update('RESET')
        this.m_old_comport_status = ""
        this.comport_status = "WAIT_FOR_IDLE"

        os.execv(__file__, sys.argv)

    def select_adjust(this):
        this.view.button_select_adjust['state'] = tkinter.DISABLED
        if (this.comport_status != "IDLE"):
            showinfo(
                title='Information',
                message=f"STM not connected\nCOM port Status 'READY' needed\n Status is {this.comport_status}"
            )
            return

        this.usb_serial.write_comport('ADJUST')
        this.view.frame_adjust_on()
        this.comport_status = "ADJUST"


if __name__ == '__main__':
    test = ""
    rtm = Controller()
    rtm.main()
