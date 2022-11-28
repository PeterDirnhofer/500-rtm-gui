import time
import tkinter
from threading import Thread
from tkinter import messagebox

from configurations import *
from model import Model
from usbserial import UsbSerial


class Measure:

    def __init__(self, view, model) -> None:
        self.__old_data_sets_received = 0
        self.__measure_loop_is_started = None
        self.__status_measure_loop = None
        self.__start_time: float
        self.view = view
        self.model = model

    def stop_measure_loop(self):
        self.__status_measure_loop = "DATA_COMPLETE"
        # time.sleep(0.1)

    @property
    def start_measure_loop(self):
        Model.clear_data_frame()

        self.__status_measure_loop = "INIT"
        self.__measure_loop_is_started = True
        measure_loop_thread = Thread(target=self.__measure_loop, daemon=True)
        measure_loop_thread.start()

    def __measure_loop(self) -> None:

        while self.__status_measure_loop != "DATA_COMPLETE":
            if self.__status_measure_loop == "INIT":
                self.__ml_init()
                continue
            elif self.__status_measure_loop == "REQUEST_MEASURE":
                self.__ml_request_measuring_from_ESP32()
                time.sleep(1)
                continue
            elif self.__status_measure_loop == 'WAIT':
                self.__ml_wait()
                continue

            elif self.__status_measure_loop == 'MEASURING':
                self.__ml_wait_for_data_complete()
                time.sleep(0.2)
                continue

            # elif self.__status_measure_loop == 'DATA_COMPLETE':
            #   time.sleep(1)

            #    continue

            elif self.__status_measure_loop == "ERROR":
                messagebox.showerror('Timeout Error. No response from ESP', f'No response from ESP.\n')
                self.__status_measure_loop = "DONE"

        self.view.text_status.set('Measureloop DONE')

    def __ml_request_measuring_from_ESP32(self):

        UsbSerial.write('MEASURE')
        self.view.text_status.set('Measureloop REQUEST_MEASURE')
        self.view.lbox_com_read_delete()
        self.__status_measure_loop = "WAIT"

    def __ml_init(self):
        self.__start_time = time.time()
        self.view.text_status.set('Measureloop INIT')
        self.view.text_status.set('Measuring ')
        self.view.frame_adjust_off()
        self.view.frame_measure_on()
        self.view.label_measure.grid(row=0, column=0, padx=10)
        self.view.text_label_measure.set("Measuring ")
        self.view.button_select_adjust['state'] = tkinter.DISABLED
        self.view.button_select_measure['state'] = tkinter.DISABLED

        self.__status_measure_loop = "REQUEST_MEASURE"

    def __ml_wait(self):
        """
        Wait for first measuring data from ESP. If any dataset is received set status to 'MEASURING'
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

    def __ml_wait_for_data_complete(self):
        """
        Wait until all data are received in Model.
        Set dtatus to 'DONE' when data complete
        :return:
        """

        if Model.data_sets_received == -1:  # Data complete when data_sets_received = -1
            self.__status_measure_loop = 'DATA_COMPLETE'
            return

        if Model.data_sets_received != self.__old_data_sets_received:
            self.__old_data_sets_received = Model.data_sets_received
            self.view.text_label_measure.set(f"Datasets {Model.data_sets_received}")
