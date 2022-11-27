from threading import Thread
import time
from tkinter import messagebox

from model import Model
import view
from usbserial import UsbSerial

from configurations import *


class Measure:

    def __init__(self, view, model) -> object:
        self.__old_data_sets_received = 0
        self.__measure_loop_is_started = None
        self.__status_measure_loop = None
        self.__start_time: float
        self.view = view
        self.model = model


    def stop_measure_loop(self):
        self.__status_measure_loop = "DONE"
        time.sleep(0.1)

    @property
    def start_measure_loop(self):
        Model.clear_data_frame()

        self.__status_measure_loop = "INIT"
        self.__measure_loop_is_started = True
        com_thread = Thread(target=self.__measure_loop, daemon=True)
        com_thread.start()
        # if not self.__measure_loop_is_started:
        #     self.__measure_loop_is_started = True
        #     com_thread = Thread(target=self.__measure_loop, daemon=True)
        #     com_thread.start()

    def __measure_loop(self) -> None:

        while self.__status_measure_loop != "DONE":
            if self.__status_measure_loop == "INIT":
                self.__ml_init()
                continue
            elif self.__status_measure_loop == "REQUEST_MEASURE":
                self.__ml_request_measuring_from_ESP32()
                time.sleep(1)
                continue
            elif self.__status_measure_loop == 'WAIT':
                self.__ml_wait()
                time.sleep(1)
                continue

            elif self.__status_measure_loop == 'MEASURING':
                self.__ml_wait_for_done()
                time.sleep(1)
                continue

            elif self.__status_measure_loop == 'DONE':
                continue


            elif self.__status_measure_loop == "ERROR":
                messagebox.showerror('Timeout Error. No response from ESP', f'No response from ESP.\n')
                self.__status_measure_loop = "DONE"

        self.view.text_status.set('Measureloop DONE')







    def __ml_request_measuring_from_ESP32(self):
        # In sumulation ESP sends IDLE
        if not SIMULATION:
            UsbSerial.write('MEASURE')
            self.view.text_status.set('Measureloop REQUEST_MEASURE')
        self.view.lbox_com_read_delete()
        time.sleep(1)
        self.__status_measure_loop = "WAIT"

    def __ml_init(self):
        self.__start_time = time.time()
        self.view.text_status.set('Measureloop INIT')
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
        self.view.text_status.set('Measureloop WAIT')



        if Model.data_sets_received > 0:
            self.__status_measure_loop = 'MEASURING'
            self.view.text_status.set('Measuring')
            return


        if int(time.time() - self.__start_time) > TIMEOUT_MEASURING:
            self.__status_measure_loop = 'ERROR'

    def __ml_wait_for_done(self):

        if Model.data_sets_received == -1:
            self.__status_measure_loop = 'DONE'
            return

        if Model.data_sets_received != self.__old_data_sets_received:
            self.__old_data_sets_received=Model.data_sets_received
            self.view.text_label_measure.set(f"Datasets {Model.data_sets_received}")


