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

        # https://stackoverflow.com/questions/44548176/how-to-fix-the-low-quality-of-tkinter-render
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

        self.title("500 EUR Raster Tunnel Mikroskop")
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
        frame_left.grid(row=1, column=0, rowspan=1, sticky='WENS')
        frame_top.grid(row=0, column=0, columnspan=2, sticky='WENS')
        frame_middle.grid(row=1, column=1, sticky='WENS')
        frame_bottom.grid(row=2, column=0, columnspan=2, sticky='WENS')

        ###################################################################################
        # frame_top: Add Measure + Adjust
        button_select_measure = ttk.Button(frame_top, text="Measure", command=controller.select_measure)
        button_select_measure.grid(row=0, column=0, padx=10, pady=2)

        button_select_adjust = ttk.Button(frame_top, text="Adjust", command=controller.select_adjust)
        button_select_adjust.grid(row=0, column=1, pady=2)

        button_select_adjust = ttk.Button(frame_top, text="COM Port", command=controller.select_comport)
        button_select_adjust.grid(row=0, column=2, padx=10,pady=2)

        ###################################################################################
        # frame_left  Add frame_com COM READ   COM WRITE  COM SELECT
        frame_com = ttk.LabelFrame(frame_left, text="COM Port")
        frame_com.grid(row=0, column=0, padx=10, pady=10)

        frame_com.rowconfigure(0, weight=10)
        frame_com.rowconfigure(1, weight=2)
        frame_com.rowconfigure(2, weight=2)

        # COM read
        frame_com_read=ttk.LabelFrame(frame_com,text='COM read')
        frame_com_read.grid(row=0, column=0, padx=10, pady=10, sticky=E + W)

        self.labeltext_com_read = tk.IntVar()
        label_com_read = ttk.Label(frame_com_read,
                                   # text="label_com_read\nREQUEST\nREQUEST",
                                   textvariable=self.labeltext_com_read,
                                   width=40)
        label_com_read.grid(row=0, column=0, padx=10, pady=10, sticky=E + W)

        # COM write
        frame_com_write=ttk.LabelFrame(frame_com,text='COM write')
        frame_com_write.grid(row=1, column=0, padx=10, pady=10)

        label_com_write = ttk.Label(frame_com_write,
                                    text="PARAMETER,?",
                                    width=40)
        label_com_write.grid(row=0, column=0, padx=10, pady=10)

        # COM port


        frame_com_port=ttk.LabelFrame(frame_com,text='COM Port')
        frame_com_port.grid(row=2,column=0,padx=10,pady=10)
        self.label_text_com_port = tk.IntVar()
        label_com_port = ttk.Label(frame_com_port,
                                   textvariable=self.label_text_com_port,
                                   width=40)
        label_com_port.grid(row=0, column=0, padx=10, pady=10)
        ###################################################################################
        # Parameter Frame
        # frame_left add frame_parameter
        frame_parameter = ttk.LabelFrame(frame_left, text="Parameter")
        frame_parameter.grid(row=1, column=0, padx=10, pady=10)

        self.text_parameter = tk.StringVar()
        self.text_parameter.set(dumyMsg)

        label_parameter = ttk.Label(frame_parameter,
                                    textvariable=self.text_parameter,
                                    width=40)
        label_parameter.grid(row=0, column=0, padx=10, pady=10)

        # configure style
        self.style = ttk.Style(self)
        self.style.configure('TLabel', relief='sunken')
        self.style.configure('TButton', relief='sunken')

    def main(self):

        self.mainloop()  # Tk mainloop
