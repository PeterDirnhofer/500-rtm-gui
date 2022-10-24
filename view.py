import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

dumyMsg = "kI,10\nkP,1000\ndestinationTunnelCurrent,10,0\nremainingTunnelCurrentDifferencenA,0.01\nstarX,0\nstartY," \
          "0\ndirection,0\n "
dumyMsg += "maxX,0\nmaxY,0\nmultiplicator,10"


class View(tk.Tk):
    def __init__(self, controller):
        super().__init__()  # Initializes methods of Tk. Tk can be used in View
        self.controller = controller  # controller can be used as attribute in class View
        self.com_selected = ""
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
        self.rowconfigure(1, weight=100)
        self.rowconfigure(2, weight=5)

        frame_top = ttk.Frame(self)  # e Menu
        frame_left = ttk.Frame(self)  # comport and parameter
        frame_middle = ttk.Frame(self)  # Measure
        frame_bottom = ttk.Frame(self)  # Status

        # grid placement main frames
        frame_left.grid(row=1, column=0, rowspan=1, sticky='nesw')
        frame_top.grid(row=0, column=0, columnspan=2, sticky='nesw')
        frame_middle.grid(row=1, column=1, sticky='nesw')
        frame_bottom.grid(row=2, column=0, columnspan=2, sticky='nesw')

        ###################################################################################
        # frame_top: Menu add Buttons Measure + Adjust
        button_select_restart = ttk.Button(frame_top, text="RESET", command=controller.select_restart)
        button_select_restart.grid(row=0, column=0, padx=10, pady=2)

        button_select_measure = ttk.Button(frame_top, text="Measure", command=controller.select_measure)
        button_select_measure.grid(row=0, column=1, padx=10, pady=2)

        self.button_select_adjust = ttk.Button(frame_top, text="Adjust",
                                          command=controller.select_adjust,
                                          state=DISABLED)
        self.button_select_adjust.grid(row=0, column=2, padx=10, pady=2)


        ###################################################################################
        # frame_left  Add frame_com COM READ   COM WRITE  COM SELECT
        frame_com = ttk.LabelFrame(frame_left, text="COM Port")
        frame_com.grid(row=0, column=0, padx=10, pady=10)

        frame_com.rowconfigure(0, weight=14)
        frame_com.rowconfigure(1, weight=2)
        frame_com.rowconfigure(2, weight=2)

        # COM read ###############################################
        frame_com_read = ttk.LabelFrame(frame_com, text='COM read')
        frame_com_read.grid(row=0, column=0, padx=10, pady=10, sticky=E + W)
        # add a scrollbar https://youtu.be/BckVJoE94Lk

        self.scrollbar = ttk.Scrollbar(frame_com_read, orient='vertical')
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.lb_com_read = tk.Listbox(frame_com_read, width=30, height=10,
                                      yscrollcommand=self.scrollbar.set, relief='sunken')
        self.lb_com_read.pack(side=TOP, fill=X)

        self.scrollbar.config(command=self.lb_com_read.yview)

        # COM write
        frame_com_write = ttk.LabelFrame(frame_com, text='COM write')
        frame_com_write.grid(row=1, column=0, padx=10, pady=5)

        label_com_write = ttk.Label(frame_com_write,
                                    text="PARAMETER,?",
                                    width=40)
        label_com_write.grid(row=0, column=0, padx=10)

        # COM port

        frame_com_port = ttk.LabelFrame(frame_com, text='COM Port')
        frame_com_port.grid(row=2, column=0, padx=10)

        self.text_com_port = tk.IntVar()
        label_com_port = ttk.Label(frame_com_port,
                                   textvariable=self.text_com_port,
                                   width=40)
        label_com_port.grid(row=0, column=0, padx=10)

        # frame_left

        # #################################################
        # frame_left/Parameter Frame
        # frame_left add frame_parameter
        frame_parameter = ttk.LabelFrame(frame_left, text="Parameter")
        frame_parameter.grid(row=1, column=0, padx=10, pady=10)

        self.text_parameter = tk.StringVar()
        self.text_parameter.set(dumyMsg)

        label_parameter = ttk.Label(frame_parameter,
                                    textvariable=self.text_parameter,
                                    width=40)
        label_parameter.grid(row=0, column=0, padx=10, pady=10)

        ####################################################################################
        # frame_bottom add frame_status

        frame_status = ttk.LabelFrame(frame_bottom, text="Status")
        frame_status.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')
        self.text_status = tk.StringVar()
        self.label_status = ttk.Label(frame_status,
                                      textvariable=self.text_status)
        self.label_status.grid(row=0, column=0, padx=10, pady=10, sticky='nswe')

        ####################################################################################
        # frame_middle Option1 : add frame_select_com add listbox_comports

        self.frame_select_com = ttk.LabelFrame(frame_middle, text="Select COM")
        self.listbox_comports = tk.Listbox(self.frame_select_com,
                                           width=70)
        self.listbox_comports.bind('<<ListboxSelect>>', self.listbox_select)

        ####################################################################################
        # frame_middle Option 2: add Adjust

        self.frame_adjust = ttk.LabelFrame(frame_middle, text="Adjust")
        #self.frame_adjust.pack(padx=10, pady=10)

        self.textvar_adjust = tk.StringVar()
        self.text_adjust = ttk.Label(self.frame_adjust,textvariable=self.textvar_adjust,font=("Arial",50))



        #self.text_adjust.pack_forget()
        #self.frame_adjust.pack_forget()

        ################################################################
        # configure style
        self.style = ttk.Style(self)
        self.style.configure('TLabel', relief='sunken')
        self.style.configure('TButton', relief='sunken')

    def main(self):
        # self.after(5000,self.controller.handle_com_port)


        self.trigger_comloop(1000)
        self.mainloop()  # Tk mainloop

    def trigger_comloop(self, intervall_ms):
        self.after(intervall_ms, self.controller.state_machine)

    def frame_select_com_on(self):
        #self.frame_adjust_off()
        self.frame_select_com.grid(row=0, column=1, sticky='nesw')
        self.listbox_comports.pack(padx=10, pady=10)

    def frame_select_com_off(self):
        self.listbox_comports.pack_forget()
        self.frame_select_com.grid_forget()

    def frame_adjust_on(self):
        #self.frame_select_com_off()
        self.frame_adjust.pack(padx=10, pady=10)
        self.text_adjust.pack(padx=10, pady=10)

    def frame_adjust_off(self):
        self.text_adjust.pack_forget()
        self.frame_adjust.pack_forget()

    def display_comports(self, ports):
        '''
        Gets list of actual available COM ports from laptop\
        Displays COM List in listbox_comports
        '''
        # ports = self.sf.get_ports()
        self.listbox_comports.delete(0, 'end')
        ports_len = len(ports)
        self.listbox_comports.config(height=ports_len)
        for port in ports:
            self.listbox_comports.insert(END, str(port))

    def text_com_read_update(self, string_to_add):
        self.lb_com_read['state'] = NORMAL
        self.lb_com_read.insert(END, string_to_add)

        # Autoscroll to end of Listbox
        # https://stackoverflow.com/questions/3699104/how-to-add-autoscroll-on-insert-in-tkinter-listbox
        self.lb_com_read.select_clear(self.lb_com_read.size()-2) #Clear the current selected item
        self.lb_com_read.select_set(END)                         #Select the new item
        self.lb_com_read.yview(END)                              #Set the scrollbar to the end of the listbox

        self.lb_com_read['state'] = DISABLED

    def text_adjust_update(self, value):
        self.textvar_adjust.set(value)

    def lb_com_read_delete(self):
        self.lb_com_read['state'] = NORMAL
        self.lb_com_read.delete(0, END)
        self.lb_com_read['state'] = DISABLED

    def listbox_select(self, event):
        line = self.listbox_comports.get(ANCHOR)
        temp = line.split(" ")[0]
        self.com_selected = temp
        print(temp)
