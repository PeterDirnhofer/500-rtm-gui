import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from typing import List, Optional

import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from usbserial import UsbSerial
from view_parameter import View_parameter


class View(tk.Tk):

    def __init__(self, controller):
        super().__init__()  # call __init__ Tk

        self.queue_is_available = tk.IntVar()  # Callback variable set by UsbSerial

        self.com_selected = None
        self.controller = controller  # controller can be used as attribute in class View

        self._make_main_frame()
        self._make_frame_menu()
        self._make_frame_comread()
        self._make_frame_comstate()
        self._make_frame_parameter()
        self._make_frame_state()
        self._make_frame_selectcom()
        self._make_frame_adjust()
        self._make_frame_measure()

        self.parameter_class = View_parameter(self.frame_main, self.lbox_parameter)

        self._style()

    def main(self):

        self._enable_receive_from_usbserial()  # Start read ESP read loop in background before entering mainloop
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call on_closing when app is canceled

        self.mainloop()  # Tk mainloop

    def _enable_receive_from_usbserial(self):
        """
        Calls '_do_queue_available' when 'queue_available' was set by 'UsbSerial._read_loop'.
        When 'UsbSerial._read_loop' has received data from ESP32 it saves it to the 'queue'.
        Then 'UsbSerial._read_loop' signalizes that data are available in queue by setting 'queue_available'.

        'queue_available' is a tk:IntVar: That means: Every change of 'queue_available' by UsbSerial
        forces the call of '_do_queue_available' with the '.trace_add' functionality below.
        """

        # call _do_queue_available, when data is written to queue_is_available
        self.queue_is_available.trace_add("write", self._do_queue_available)

    def _make_main_frame(self):
        # https://stackoverflow.com/questions/44548176/how-to-fix-the-low-quality-of-tkinter-render
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

        self.title("500 EUR Raster Tunnel Mikroskop")

        self.iconbitmap('data/LOGO-rsl.ico')

        self.geometry("1000x700")
        self.resizable(False, False)

        self.frame_main = ttk.Frame(self)
        self.frame_main.grid(row=0, column=0, sticky=NSEW)

        # define main frames
        # self.frame_main.grid_columnconfigure(0, weight=8)
        # self.frame_main.grid_columnconfigure(1, weight=8)
        #
        # self.frame_main.grid_rowconfigure(0, weight=5)
        # self.frame_main.grid_rowconfigure(1, weight=10)
        # self.frame_main.grid_rowconfigure(2, weight=10)
        # self.frame_main.grid_rowconfigure(3, weight=10)
        # self.frame_main.grid_rowconfigure(4, weight=5)

    def _make_frame_menu(self):
        self.frame_menu = ttk.Frame(self.frame_main)
        self.frame_menu.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        self.button_select_reset = ttk.Button(self.frame_menu, text="RESET",
                                              command=self.controller.select_restart)

        self.button_select_reset.pack(side=LEFT, padx=10, pady=2)

        self.button_select_measure = ttk.Button(self.frame_menu, text="Measure",
                                                command=self.controller.select_measure)

        self.button_select_measure.pack(side=LEFT, padx=10, pady=2)

        self.button_select_adjust = ttk.Button(self.frame_menu, text="Adjust",
                                               command=self.controller.select_adjust)

        self.button_select_adjust.pack(side=LEFT, padx=10, pady=2)

    def _make_frame_measure(self) -> None:
        self.frame_measure = ttk.LabelFrame(self.frame_main, text='Measure')
        self.text_label_measure = tk.StringVar()
        self.label_measure = ttk.Label(self.frame_measure,
                                       textvariable=self.text_label_measure,
                                       width=40)

    def _make_frame_comread(self) -> None:
        self.frame_com_read = ttk.LabelFrame(self.frame_main, text='COM read')
        self.frame_com_read.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)

        # add a scrollbar https://youtu.be/BckVJoE94Lk
        self.scrollbar = ttk.Scrollbar(self.frame_com_read, orient='vertical')
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.lbox_com_read = tk.Listbox(self.frame_com_read, width=60, height=10,
                                        yscrollcommand=self.scrollbar.set, relief='sunken')
        self.lbox_com_read.pack(side=LEFT, fill=X, padx=10)

        self.scrollbar.config(command=self.lbox_com_read.yview)

    def _make_frame_comstate(self) -> None:
        self.frame_com_state = ttk.LabelFrame(self.frame_main, text='COM State')
        self.frame_com_state.grid(row=2, column=0, padx=10, sticky=NSEW)

        self.text_com_state = tk.StringVar()
        label_com_state = ttk.Label(self.frame_com_state,
                                    textvariable=self.text_com_state,
                                    width=40)
        label_com_state.grid(row=0, column=0, padx=10)

    def _make_frame_parameter(self) -> None:
        self.frame_parameter = ttk.LabelFrame(self.frame_main, text="Parameter")
        self.frame_parameter.grid(row=3, column=0, padx=10, pady=10, sticky=NSEW)

        self.lbox_parameter = tk.Listbox(self.frame_parameter, width=60)

        self.lbox_parameter.bind('<<ListboxSelect>>', self.parameter_select)
        self.lbox_parameter.grid(row=0, column=0, padx=10, pady=5, sticky=NSEW)

        # Define refresh Image using pillow  https://youtu.be/kjc53i4xUmw
        self.pillow_image = Image.open(r"data/refresh_icon-icons.png")
        self.pillow_image = self.pillow_image.resize((25, 25), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.pillow_image)

        self.btn_get_parameter = ttk.Button(self.frame_parameter,
                                            image=self.image,
                                            command=UsbSerial.send_request_parameter_to_esp)

        # self.btn_get_parameter.pack(side = LEFT)
        self.btn_get_parameter.grid(row=1, column=0, sticky=W, padx=10, pady=5)

    def _make_frame_state(self) -> None:
        self.frame_status = ttk.LabelFrame(self.frame_main, text="State")
        self.frame_status.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
        self.text_status = tk.StringVar()

        self.label_status = tk.Label(self.frame_status, padx=10, pady=5,
                                     textvariable=self.text_status)
        self.label_status.pack(side=LEFT)

    def _make_frame_selectcom(self) -> None:
        self.frame_select_com = ttk.LabelFrame(self.frame_main, text="Select COM")
        self.frame_select_com.grid(row=3, column=1, padx=10, pady=5)

        self.lbox_comports = tk.Listbox(self.frame_select_com,
                                        width=70)

        self.lbox_comports.bind('<<ListboxSelect>>', self.lbox_comports_select)

    def _make_frame_adjust(self) -> None:
        self.frame_adjust = ttk.LabelFrame(self.frame_main, text="Adjust")
        self.frame_adjust.grid(row=3, column=1)
        self.frame_adjust.grid_forget()

        self.text_label_adjust = tk.StringVar()
        self.label_adjust = ttk.Label(self.frame_adjust, textvariable=self.text_label_adjust, font=("Arial", 50))

        self.label_adjust.grid(row=0, column=0, sticky=E + W)

    def frame_select_com_on(self) -> None:
        self.frame_select_com.grid(row=1, column=1)
        self.lbox_comports.pack(padx=10, pady=10)

    def frame_select_com_off(self) -> None:
        self.lbox_comports.grid_forget()
        self.frame_select_com.grid_forget()

    def frame_measure_on(self) -> None:
        self.frame_measure.grid(row=1, column=1, rowspan=3, sticky=NSEW)

    def frame_measure_off(self) -> None:
        self.frame_measure.grid_forget()

    def frame_adjust_on(self) -> None:
        self.frame_adjust.grid(row=1, column=1, sticky=E + W)
        self.label_adjust.grid(row=0, column=0, sticky=NSEW)

    def frame_adjust_off(self) -> None:
        self.label_adjust.grid_forget()
        self.frame_adjust.grid_forget()

    def _style(self):
        self.style = ttk.Style(self)
        self.style.configure('TLabel', relief='sunken')
        self.style.configure('TButton', relief='sunken')

    # noinspection PyUnusedLocal
    def _do_queue_available(self, *args):
        """ '_do_queue_available' is triggered, when tk.IntVar 'queue_available' was modified by 'UsbSerial._read_loop'.
        After 'UsbSerial._read_loop' has stored received data from ESP32 in 'queue' it signals
        that data are available by setting 'queue_available'
        """

        while not UsbSerial.queue.empty():
            res = UsbSerial.queue.get()
            x = res.split(",")
            if x[0] == 'ADJUST':
                self.label_adjust_update(x[1])
            elif x[0] == 'PARAMETER':
                self.lbox_parameter.insert(tk.END, f'{x[1]} , {x[2]}')
            else:
                self.lbox_com_read_update(res)

    def display_comports(self, ports: list[str]) -> None:
        """Render available ports in listbox_comports
        :param ports: List of available ports
        """
        # ports = self.sf.get_ports()
        self.lbox_comports.delete(0, 'end')
        ports_len = len(ports)
        self.lbox_comports.config(height=ports_len)
        for port in ports:
            self.lbox_comports.insert(END, str(port))

    def lbox_com_read_update(self, string_to_add):
        """
        Enable Listbox write access. Add string to Listbox.
        Set Cursor to end of Listbox, Disable write access,
        :param string_to_add:
        """
        self.lbox_com_read['state'] = NORMAL
        self.lbox_com_read.insert(END, string_to_add)

        # Autoscroll to end of Listbox
        # https://stackoverflow.com/questions/3699104/how-to-add-autoscroll-on-insert-in-tkinter-listbox
        self.lbox_com_read.select_clear(self.lbox_com_read.size() - 2)  # Clear the current selected item
        self.lbox_com_read.select_set(END)  # Select the new item
        self.lbox_com_read.yview(END)  # Set the scrollbar to the end of the listbox

        self.lbox_com_read['state'] = DISABLED

    def label_adjust_update(self, value):
        self.text_label_adjust.set(value)

    def lbox_com_read_delete(self):
        self.lbox_com_read['state'] = NORMAL
        self.lbox_com_read.delete(0, END)
        self.lbox_com_read['state'] = DISABLED

    def lbox_parameter_delete(self):
        self.lbox_parameter.delete(0, END)

    # noinspection PyUnusedLocal
    def lbox_comports_select(self, event):
        line = self.lbox_comports.get(ANCHOR)
        temp = line.split(" ")[0]

        self.com_selected = temp
        UsbSerial.set_com_selected(temp)
        print(temp)

    # noinspection PyUnusedLocal
    def parameter_select(self, event):
        selected_indices = self.lbox_parameter.curselection()

        # newWindow= tk.Toplevel(self.frame_main)
        # newWindow.title("Edit Parameter")
        # newWindow.geometry("200*200")

        for anchor in selected_indices:
            self.parameter_class.create_window(anchor)

        st = self.parameter_class.get_parameter_string

        print(st)
        #self.parameter_class.close_window()


    @staticmethod
    def __plot_3d(fig, data: List, intp: Optional[bool] = True) -> None:
        """Plots the x, y, z from data contained within a dict

        Parameters
        ----------
        data: List
            The data with the x, y, z as 2D-numpy arrays
        intp: bool, optional
            If 'True' then the contour is interpolated for a more smooth look
        """
        ax = fig.add_subplot(2, 1, 1, projection="3d")

        ax.plot_surface(*data, rstride=1, cstride=1,
                        antialiased=True, cmap=cm.coolwarm)

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title("3D Height profile (antialised)")

    def plotter(self, data: List) -> None:
        """Makes a two-page plot of the (.csv)-file's RTM scan input
        Based on Marten Scheuck. See model.py

        Parameters
        ----------
        data: List
            The restructured data from the (.csv)-file
        """

        fig = plt.figure(figsize=(6, 6))
        fig.suptitle("RTM Scan")
        self.__plot_3d(fig, data)
        # plot_single_scan(fig, data)

        __canvas = FigureCanvasTkAgg(fig, master=self.frame_measure)
        # __canvas = FigureCanvasTkAgg(fig, master=self.frame_main)
        __canvas.draw()
        self.label_measure.grid_forget()
        __canvas.get_tk_widget().pack()

        # plt.show()

    # https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
    # How to embed Matplotlib charts in Tkinter GUI?

    def on_closing(self):
        """
        Close app and stop Python
        :return:
        """
        self.controller.select_restart()
        self.destroy()
        exit()
