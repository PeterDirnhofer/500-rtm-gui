# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
from tkinter.messagebox import showinfo

import serial

from model import Model
from usb_serial import Usb_serial
from view import View
import os
import sys
import time
from threading import Timer

# Timer Class https://youtu.be/5NJ9cc0dnCM


class Controller:
    def __init__(self):
        self.model = Model()

        self.view = View(self)  # self (instance of controller) is passed to View
        self.usb_serial = Usb_serial(self,self.view)
        self.m_old_comport_status=""
        self.comport_status="INIT"

    def main(self):
        # self.view.label_text_com_port.set(self.usb_serial.get_comport()) # read default COMPORT
        self.view.main()

    def select_measure(this):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def select_restart(this):

        this.usb_serial.write_comport(chr(3))
        this.view.text_com_delete()
        os.execv(sys.argv[0],sys.argv)

    def select_adjust(this):
        if this.comport_status != "READY":
            showinfo(
                title='Information',
                message="STM not connected\nCOM port Status 'READY' needed"
            )
            return

        this.usb_serial.write_comport('ADJUST')
        this.view.text_com_delete()


    def handle_com_port(this):

        if this.m_old_comport_status!=this.comport_status:
            print(f"comport_status: {this.comport_status}")
        this.m_old_comport_status = this.comport_status

        akt_port = this.usb_serial.get_comport()
        this.view.text_com_port.set(f'{akt_port}: {this.comport_status}' )

        if this.comport_status == "INIT":
            result = this.usb_serial.open_comport(akt_port)
            this.view.text_status.set(result)
            if result!='OPEN':
                # Display available COM ports
                available_ports=this.usb_serial.get_ports()
                this.view.display_comports(available_ports)
                if this.view.com_selected!="":
                    this.usb_serial.put_comport(this.view.com_selected)
                #this.comport_status="INIT"
            elif result=="ERROR":
                this.view.text_com_port.set(f'ERROR Cannot open {akt_port}')

            else:
                this.comport_status="WAIT_FOR_IDLE"
                this.usb_serial.start_comport_read_thread()

        elif this.comport_status=="WAIT_FOR_IDLE":
            if this.usb_serial.read_line=='IDLE':
                this.comport_status="READY"

        this.view.trigger_comloop(200)

if __name__ == '__main__':


    test=""
    rtm = Controller()
    rtm.main()
