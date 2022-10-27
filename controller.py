# Python Tutorial: GUI Calculator with Model View Controller #1
# https://youtu.be/ek47NMFW_mk
import os
import sys
import tkinter
from tkinter.messagebox import showinfo

from model import Model
from usbserial import UsbSerial
from view import View


# Timer Class https://youtu.be/5NJ9cc0dnCM
class Controller:
    def __init__(self):
        self.m_old_comport_status = ""
        self.port_is_available = False
        self.model = Model()
        self.view = View(self)  # self (instance of controller) is passed to View
        self.usb_serial = UsbSerial(self, self.view)

        self.comport_status = ""
        self.comport_state = ""
        self.is_connected = False
        self.act_port = ""
        self.sm_state = 'INIT'

    def main(self):
        self.view.main()

    def sm_is_default_port_existing(self):
        # Check if default COM port is existing on Computer
        self.act_port = self.usb_serial.get_comport_saved()
        self.view.text_com_state.set(f'Connecting {self.act_port} ...')
        available_ports = self.usb_serial.get_ports()
        port_exists = False
        for port in available_ports:
            r = self.act_port in port
            if r:
                port_exists = True
        if not port_exists:
            self.view.text_com_state.set(f'ERROR {self.act_port} not available on Computer')
            self.sm_state = 'ERROR'
            return
        else:
            self.sm_state = 'EXISTING'
            return

    def sm_open(self):
        # try to open COM port on computer
        result = self.usb_serial.open_comport(self.act_port)
        if result == 'OPEN':
            self.sm_state = 'OPEN'
        else:
            self.sm_state = 'ERROR'
        return

    def sm_send_reset(self):
        # Check if it is possible to send CTRL-C to ESP32
        # Start COM read in background thread
        if self.usb_serial.write_comport(chr(3)):
            self.usb_serial.start_comport_read_thread()  # enable receiver
            self.sm_state = 'WAIT_FOR_IDLE'
        else:
            self.sm_state = 'ERROR'

    def sm_wait_for_idle(self):
        # Wait for 'IDLE' from ESP32
        if self.usb_serial.read_line == 'IDLE':
            self.sm_state = 'COM_READY'
            return


        hs = self.usb_serial.read_line[:20]
        self.view.text_com_state.set(f"ERROR read IDLE: {hs}")
        self.sm_state="ERROR"

    def sm_com_ready(self):
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL
        self.view.text_com_state.set(f'Connected {self.act_port}')

    def sm_error(self):
        self.view.frame_select_com_on()
        available_ports = self.usb_serial.get_ports()
        self.view.display_comports(available_ports)

        if self.view.com_selected != "":
            self.usb_serial.put_comport(self.view.com_selected)
            # self.view.text_com_read_update(f'{self.view.com_selected} selected')
            self.view.frame_select_com_off()
            self.sm_state = 'INIT'

    def state_machine(self):
        if self.sm_state == 'INIT':
            self.sm_is_default_port_existing()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'EXISTING':
            self.sm_open()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'OPEN':
            self.sm_send_reset()
            self.view.trigger_state_machine_after(1000)
            return
        elif self.sm_state == 'WAIT_FOR_IDLE':
            self.sm_wait_for_idle()
            self.view.trigger_state_machine_after(50)
            return
        elif self.sm_state == 'COM_READY':
            self.sm_com_ready()
            # state machine no longer needed. No retrigger

        elif self.sm_state == "ERROR":
            self.sm_error()

            # self.select_restart()
            self.view.trigger_state_machine_after(200)

        else:
            raise Exception(f'Invalid state in state_machine: {self.sm_state}')

    @staticmethod
    def select_measure():
        showinfo(
            title='Information',
            message='Measure clicked!'
        )

    def select_restart(self):
        self.view.frame_select_com_off()
        self.view.frame_adjust_off()
        self.view.button_select_adjust['state'] = tkinter.NORMAL
        self.view.button_select_measure['state'] = tkinter.NORMAL
        self.view.button_select_reset['state'] = tkinter.NORMAL

        # send restart to ESP32

        self.usb_serial.write_comport(chr(3))
        self.view.lb_com_read_delete()
        self.view.text_com_read_update('RESET')
        self.m_old_comport_status = ""
        self.comport_status = "WAIT_FOR_IDLE"
        self.is_connected = False
        print(f"__file__  {__file__}")
        os.execv(__file__, sys.argv)



    def select_adjust(self):
        self.view.button_select_adjust['state'] = tkinter.DISABLED

        self.usb_serial.write_comport('ADJUST')
        self.view.frame_adjust_on()
        self.comport_status = "ADJUST"


if __name__ == '__main__':
    test = ""
    rtm = Controller()
    rtm.main()
