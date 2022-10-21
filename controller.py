# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
from tkinter.messagebox import showinfo

from model import Model
from usb_serial import Usb_serial
from view import View
import time
from threading import Timer

# Timer Class https://youtu.be/5NJ9cc0dnCM


class Controller:
    def __init__(self):
        self.model = Model()
        self.usb_serial=Usb_serial()
        self.view = View(self)  # self (instance of controller) is passed to View

        self.comport_status="INIT"

    def main(self):
        # self.view.label_text_com_port.set(self.usb_serial.get_comport()) # read default COMPORT
        self.view.main()



    def select_measure(this):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )


    def select_comport(this):
        this.view.text_com_read.set("COMPORT selected")
        #this.model.put_comport("COM7")
        this.view.label_text_com_port.set(this.model.get_comport())



    def select_adjust(this):
        showinfo(
            title='Information',
            message='Adjust clicked!'
        )

    def handle_com_port(this):

        print(f"comport_status: {this.comport_status}")
        akt_port = this.usb_serial.get_comport()
        this.view.text_com_port.set(f'{akt_port}: {this.comport_status}' )
        if this.comport_status == "INIT":
            result = this.usb_serial.open_comport(akt_port)
            this.view.text_status.set(this.usb_serial.open_comport(akt_port))
            if result!='CONNECTED':
                # Display available COM ports
                available_ports=this.usb_serial.get_ports()
                this.view.display_comports(available_ports)
                if this.view.com_selected!="":
                    print(f"{this.view.com_selected} selected")
                    this.usb_serial.put_comport(this.view.com_selected)
                    print(f"in controller com selected", this.view.com_selected)
                #this.view.text_parameter.set("Fehler Connecting to COM port")
            else:

                this.comport_status="WAIT_FOR_REQUEST"

            this.view.trigger_comloop(200)







if __name__ == '__main__':
    test=""
    rtm = Controller()
    rtm.main()
