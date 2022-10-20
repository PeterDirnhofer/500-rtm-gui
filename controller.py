# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
from tkinter.messagebox import showinfo

from model import Model
from view import View


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View

    def main(self):
        self.view.label_text_com_port.set(self.model.get_comport()) # read default COMPORT
        self.view.main()



    def select_measure(this):
        showinfo(
            title='Information',
            message='Measure clicked!'
        )


    def select_comport(this):
        this.view.labeltext_com_read.set("COMPORT selected")
        #this.model.put_comport("COM7")
        this.view.label_text_com_port.set(this.model.get_comport())



    def select_adjust(this):
        showinfo(
            title='Information',
            message='Adjust clicked!'
        )



if __name__ == '__main__':
    rtm = Controller()
    rtm.main()
