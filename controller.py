# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
import sys
from tkinter.messagebox import showinfo

import serial

from model import Model
from usb_serial import Usb_serial
from view import View
import os
from sys import exit
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
        this.view.frame_select_com_off()
        this.view.frame_adjust_off()
        # send restart to ESP32
        this.usb_serial.write_comport(chr(3))
        this.view.text_com_delete()
        this.view.text_com_read_update("RESTART")
        this.m_old_comport_status = ""
        this.comport_status="READY"

        os.execv(__file__, sys.argv)

    def select_adjust(this):
        if (this.comport_status != "READY") & (this.comport_status!= "WAIT_FOR_IDLE"):
            showinfo(
                title='Information',
                message=f"STM not connected\nCOM port Status 'READY' needed\n Status is {this.comport_status}"
            )
            return

        this.usb_serial.write_comport('ADJUST')
        this.view.frame_adjust_on()
        this.comport_status="ADJUST"

    def handle_com_port(this):

        if this.m_old_comport_status!=this.comport_status:
            print(f"comport_status: {this.comport_status}")
        this.m_old_comport_status = this.comport_status

        akt_port = this.usb_serial.get_comport()
        this.view.text_com_port.set(f'{akt_port}: {this.comport_status}' )


        if this.comport_status == "INIT":
            result = this.usb_serial.open_comport(akt_port)
            this.view.text_status.set(result)
            # Cannot find COM PORT

            if result!='OPEN':
                this.view.text_com_port.set(f'ERROR Cannot open {akt_port}')
                this.view.frame_select_com_on()
                # Display available COM ports
                #this.view.frame_select_com.grid(row=0, column=1, sticky='nesw')

                #this.view.listbox_comports.pack(padx=10, pady=10)
                available_ports=this.usb_serial.get_ports()
                this.view.display_comports(available_ports)
                if this.view.com_selected!="":
                    this.usb_serial.put_comport(this.view.com_selected)
                    this.view.listbox_comports.pack_forget()

                #this.comport_status="INIT"
            else:

                this.comport_status="WAIT_FOR_IDLE"
                this.usb_serial.start_comport_read_thread()

        elif this.comport_status=="WAIT_FOR_IDLE":
            if this.usb_serial.read_line=='IDLE':
                this.comport_status="READY"

        elif this.comport_status=="ADJUST":
            this.view.text_adjust["text"]="lghlug"

        this.view.trigger_comloop(200)

if __name__ == '__main__':

    test=""
    rtm = Controller()
    rtm.main()
