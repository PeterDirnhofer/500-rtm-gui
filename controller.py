# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
from tkinter.messagebox import showinfo

from model import Model
from usb_serial import Usb_serial
from view import View


class Controller:
    def __init__(self):
        self.model = Model()
        self.usb_serial=Usb_serial()
        self.view = View(self)  # self (instance of controller) is passed to View

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

        print("handle_com_port")
        akt_port=this.usb_serial.get_comport()
        result=this.usb_serial.open_comport(akt_port)

        if result!='CONNECTED':
            # Display avaiable ports and wai for selection
            this.view.text_status.set(this.usb_serial.open_comport(akt_port))
            available_ports=this.usb_serial.get_ports()
            this.view.display_comports(available_ports)
            # Wait until new port is selected


            print(f"in controller com selected",this.view.com_selected)




            #this.view.text_parameter.set("Fehler Connecting to COM port")
        else:
            this.view.label_status.after(2000, this.handle_com_port)






if __name__ == '__main__':
    test=""
    rtm = Controller()
    rtm.main()
