import ctypes
import tkinter as tk
from tkinter import ttk,Text
from tkinter.constants import *


dumyMsg = "kI,10\nkP,1000\ndestinationTunnelCurrent,10,0\nremainingTunnelCurrentDifferencenA,0.01\nstarX,0\nstartY," \
          "0\ndirection,0\n "
dumyMsg += "maxX,0\nmaxY,0\nmultiplicator,10"



class View(tk.Tk):
    def __init__(self, controller):
        super().__init__()  # Initializes methods of Tk. Tk can be used in View
        self.controller = controller  # controller can be used as attribute in class View
        self.com_selected=""
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
        frame_left.grid(row=1, column=0, rowspan=1, sticky='nesw')
        frame_top.grid(row=0, column=0, columnspan=2, sticky='nesw')
        frame_middle.grid(row=1, column=1, sticky='nesw')
        frame_bottom.grid(row=2, column=0, columnspan=2, sticky='nesw')

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

        # COM read ###############################################
        frame_com_read=ttk.LabelFrame(frame_com,text='COM read')
        frame_com_read.grid(row=0, column=0, padx=10, pady=10, sticky=E + W)
        # add a scrollbar https://youtu.be/BckVJoE94Lk

        self.scrollbar=ttk.Scrollbar(frame_com_read,orient='vertical')
        self.scrollbar.pack(side=RIGHT,fill=Y)

        self.text_com_read = tk.Text(frame_com_read,width=30,height=10,
                                     yscrollcommand=self.scrollbar.set,relief='sunken')
        self.text_com_read.pack(side=TOP,fill=X)

        self.scrollbar.config(command=self.text_com_read.yview)


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

        self.text_com_port = tk.IntVar()
        label_com_port = ttk.Label(frame_com_port,
                                   textvariable=self.text_com_port,
                                   width=40)
        label_com_port.grid(row=0, column=0, padx=10, pady=10)

        ###################################################################################
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
        frame_status.grid(row=0,column=0,padx=10, pady=10,sticky='nesw')
        self.text_status = tk.StringVar()
        self.label_status=ttk.Label(frame_status,
                                    textvariable=self.text_status)
        #self.label_status.after(2000,self.controller.handle_com_port)

        self.label_status.grid(row=0, column=0,padx=10,pady=10,sticky = 'nswe')


        ####################################################################################
        # frame_middle add listbox
        frame_select_com = ttk.LabelFrame(frame_middle,text="Select COM")
        frame_select_com.grid(row=0,column=1,sticky='nesw')

        self.listbox = tk.Listbox(frame_select_com,
                             width=70)
        self.listbox.grid(row=0,column=0,padx=10,pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.listboxSelect)

        # configure style
        self.style = ttk.Style(self)
        self.style.configure('TLabel', relief='sunken')
        self.style.configure('TButton', relief='sunken')

    def display_comports(self,ports):
        '''
        Gets list of actual available COM ports from laptop\
        Displays COM List in listbox_comports
        '''
        #ports = self.sf.get_ports()
        self.listbox.delete(0, 'end')
        portsLen = len(ports)
        self.listbox.config(height=portsLen)
        for port in ports:
            self.listbox.insert(END, str(port))

    def text_com_read_update(self, string_to_add):
        self.text_com_read['state']=NORMAL
        self.text_com_read.insert(END,string_to_add)
        self.text_com_read.insert(END, '\n')
        self.text_com_read['state'] = DISABLED

    def listboxSelect(self,event):
        line = self.listbox.get(ANCHOR)
        temp = line.split(" ")[0]
        self.com_selected=temp
        print(temp)

    def trigger_comloop(self,intervall_ms):
        self.after(intervall_ms,self.controller.handle_com_port)
    def main(self):

        #self.after(5000,self.controller.handle_com_port)
        self.trigger_comloop(1000)
        self.mainloop()  # Tk mainloop
