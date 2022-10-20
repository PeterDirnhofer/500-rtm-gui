# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk

from model import Model
from view import View


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self) # self (instance of controller) is passed to View

    def main(self):
        self.view.main()



if __name__ == '__main__':
    rtm = Controller()
    rtm.main()
