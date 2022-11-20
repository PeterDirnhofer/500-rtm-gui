from threading import Thread
import time
from tkinter import messagebox
from usbserial import UsbSerial

from configurations import *


class Measure:

    def __init__(self, view, model):
        self.__measure_loop_is_started = None
        self.__status_measure_loop = None
        self.__start_time: float
        self.view = view
        self.model = model

    @property
    def start_measure_cycle(self):

        if not self.__measure_loop_is_started:
            self.__measure_loop_is_started = True
            self.__status_measure_loop = "INIT"
            com_thread = Thread(target=self.__measure_loop, daemon=True)
            com_thread.start()
            return True
        else:
            return False

    def __measure_loop(self) -> None:

        while self.__status_measure_loop != "DONE":
            if self.__status_measure_loop == "INIT":
                self.__ml_init()
                continue
            elif self.__status_measure_loop == "REQUEST_MEASURE":
                self.__ml_request_measure()
                time.sleep(1)
                continue
            elif self.__status_measure_loop == 'WAIT':
                self.__ml_wait()
                time.sleep(1)
                continue
            elif self.__status_measure_loop == "ERROR":
                messagebox.showerror('Timeout Error. No response from ESP', f'No response from ESP.\n')
                self.__status_measure_loop = "DONE"

    def __ml_request_measure(self):
        # In sumulation ESP sends IDLE
        if not SIMULATION:
            UsbSerial.write('MEASURE')
        self.view.lbox_com_read_delete()
        time.sleep(1)
        self.__status_measure_loop = "WAIT"

    def __ml_init(self):
        self.__start_time = time.time()

        self.view.text_status.set('Measuring ')
        self.view.frame_adjust_off()
        self.view.frame_measure_on()
        self.view.label_measure.grid(row=0, column=0, padx=10)
        self.view.text_label_measure.set("Measuring ")
        self.__status_measure_loop = "REQUEST_MEASURE"

    def __ml_wait(self):
        """
        Wait for measuring data from ESP. Write data to file.
        If all data received. set status 'DATA_COMPLETE'
        On timeout set status 'ERROR'
        :return:
        """

        self.view.text_label_measure.set(self.view.text_label_measure.get() + '.')


        if int(time.time() - self.__start_time) > TIMEOUT_MEASURING:
            if SIMULATION:
                self.__status_measure_loop = ""
            else:
                self.__status_measure_loop = 'ERROR'
