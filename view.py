import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

import PIL
from PIL import Image, ImageTk

class View(tk.Tk):
    def __init__(self, controller):
        super().__init__()  # call __init__ Tk
        self.controller = controller  # controller can be used as attribute in class View
        self.com_selected = ""

        self._make_main_frame()

        self._make_frame_menu()
        self._make_frame_comread()
        self._make_frame_comstate()
        self._make_frame_parameter()
        self._make_frame_state()

        self._make_frame_middle()
        self._style()

    def main(self):
        self.trigger_state_machine_after(1000)
        self.mainloop()  # Tk mainloop


    def _make_main_frame(self):
        # https://stackoverflow.com/questions/44548176/how-to-fix-the-low-quality-of-tkinter-render
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

        self.title("500 EUR Raster Tunnel Mikroskop")

        self.iconbitmap('data/LOGO-rsl.ico')

        self.geometry("900x700")
        self.resizable(False, False)

        # define main frames
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)

        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=40)
        self.rowconfigure(2, weight=10)
        self.rowconfigure(3, weight=60)
        self.rowconfigure(4, weight=5)



        self.frame_middle = ttk.Frame(self)  # Measure
        self.frame_bottom = ttk.Frame(self)  # Status



        self.frame_middle.grid(row=1, column=1, sticky='nesw')
        self.frame_bottom.grid(row=3, column=0, columnspan=2, sticky='nesw')

    def _make_frame_menu(self):
        self.frame_menu = ttk.Frame(self)
        self.frame_menu.grid(row=0,column=0,sticky='nesw')
        self.button_select_reset = ttk.Button(self.frame_menu, text="RESET",
                                              command=self.controller.select_restart,
                                              state=DISABLED)
        self.button_select_reset.pack(side=LEFT, padx=10, pady=2)

        self.button_select_measure = ttk.Button(self.frame_menu, text="Measure",
                                                command=self.controller.select_measure,
                                                state=DISABLED)
        self.button_select_measure.pack(side=LEFT, padx=10, pady=2)

        self.button_select_adjust = ttk.Button(self.frame_menu, text="Adjust",
                                               command=self.controller.select_adjust,
                                               state=DISABLED)
        self.button_select_adjust.pack(side=LEFT, padx=10, pady=2)

    def _make_frame_comread(self):
        self.frame_com_read = ttk.LabelFrame(self, text='COM read1')
        self.frame_com_read.grid(row=1, column=0, padx=10, pady=10,  sticky=N + S)

        # add a scrollbar https://youtu.be/BckVJoE94Lk
        self.scrollbar = ttk.Scrollbar(self.frame_com_read, orient='vertical')
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.lbox_com_read = tk.Listbox(self.frame_com_read, width=30, height=10,
                                        yscrollcommand=self.scrollbar.set, relief='sunken')
        self.lbox_com_read.pack(side=LEFT, fill=X)

        self.scrollbar.config(command=self.lbox_com_read.yview)

    def _make_frame_comstate(self):
        self.frame_com_state = ttk.LabelFrame(self, text='COM-State')
        self.frame_com_state.grid(row=2, column=0, padx=10)

        self.text_com_state = tk.IntVar()
        label_com_state = ttk.Label(self.frame_com_state,
                                    textvariable=self.text_com_state,
                                    width=40)
        label_com_state.grid(row=0, column=0, padx=10)

    def _make_frame_parameter(self):
        self.frame_parameter = ttk.LabelFrame(self, text="Parameter")
        self.frame_parameter.grid(row=3, column=0, padx=10, pady=10)
        self.tbox_parameter = tk.Listbox(self.frame_parameter,
                                         width=70)

        self.tbox_parameter.bind('<<ListboxSelect>>', self.parameter_select)

        self.tbox_parameter.pack()

        # Define refresh Image using pillow  https://youtu.be/kjc53i4xUmw
        self.pillow_image = Image.open(r"data/refresh_icon-icons.png")
        self.pillow_image = self.pillow_image.resize((25, 25), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.pillow_image)

        self.btn_get_parameter = ttk.Button(self.frame_parameter,
                                            image=self.image,
                                            command=self.controller.usb_serial_get_parameter_handle)

        self.btn_get_parameter.pack(side=LEFT)

    def _make_frame_state(self):
        self.frame_status = ttk.LabelFrame(self, text="State")
        self.frame_status.grid(row=4, column=0, columnspan=2,padx=10, pady=10, sticky='nesw')
        self.text_status = tk.StringVar()
        self.label_status = ttk.Label(self.frame_status,
                                      textvariable=self.text_status)
        self.label_status.pack(side=LEFT)

    def _make_frame_middle(self):
        self.frame_select_com = ttk.LabelFrame(self.frame_middle, text="Select COM")

        self.listbox_comports = tk.Listbox(self.frame_select_com,
                                           width=70)

        self.listbox_comports.bind('<<ListboxSelect>>', self.listbox_select)
        self.frame_adjust = ttk.LabelFrame(self.frame_middle, text="Adjust")

        self.text_label_adjust = tk.StringVar()
        self.label_adjust = ttk.Label(self.frame_adjust, textvariable=self.text_label_adjust, font=("Arial", 50))

    def _style(self):
        self.style = ttk.Style(self)
        self.style.configure('TLabel', relief='sunken')
        self.style.configure('TButton', relief='sunken')

    def trigger_state_machine_after(self, intervall_ms):
        self.after(intervall_ms, self.controller.usb_serial_init_com_handle)

    def frame_select_com_on(self):
        # self.frame_adjust_off()
        self.frame_select_com.grid(row=0, column=1, sticky='nesw')
        self.listbox_comports.pack(padx=10, pady=10)

    def frame_select_com_off(self):
        self.listbox_comports.pack_forget()
        self.frame_select_com.grid_forget()

    def frame_adjust_on(self):
        # self.frame_select_com_off()
        self.frame_adjust.pack(padx=10, pady=10)
        self.label_adjust.pack(padx=10, pady=10)

    def frame_adjust_off(self):
        self.label_adjust.pack_forget()
        self.frame_adjust.pack_forget()

    def display_comports(self, ports):
        """
        Gets list of actual available COM ports from laptop\
        Displays COM List in listbox_comports
        """
        # ports = self.sf.get_ports()
        self.listbox_comports.delete(0, 'end')
        ports_len = len(ports)
        self.listbox_comports.config(height=ports_len)
        for port in ports:
            self.listbox_comports.insert(END, str(port))

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

    def lb_com_read_delete(self):
        self.lbox_com_read['state'] = NORMAL
        self.lbox_com_read.delete(0, END)
        self.lbox_com_read['state'] = DISABLED

    def listbox_select(self, event):
        line = self.listbox_comports.get(ANCHOR)
        temp = line.split(" ")[0]
        self.com_selected = temp
        print(temp)

    def parameter_select(self, event):
        pass

    def close(self):
        self.destroy()
