import tkinter as tk
from tkinter import ttk

import model_parameter as pm


# from model_parameter import Model_parameter
#   Example
#   PARAMETER,10,1000,10.0,0.01,0,0,0,199,199,10

class View_parameter:
    reset_string = "PARAMETER,10,1000,10.0,0.01,0,0,0,199,199,10"

    def __init__(self, frame: tk.Frame, listbox: tk.Listbox) -> None:

        self.actual_values = None
        self.actual_values_list = None
        self.index = None
        self.entry = None
        self.lb1 = None
        self.listbox = listbox
        self.lb_actual_value = ttk.Label
        self.top = None
        self.frame = frame
        self.init_parameter()
        self.model = pm.Model_parameter
        self.text_actual_value = tk.StringVar()
        self.parameter_new_string=None

    def check_input(self, event=None):
        h = 1.0
        s = (self.entry.get())
        try:
            h = float(s)

            self.actual_values_list[self.index]=s
            self.make_parameterstring_from_listbox_values()

        except:
            print("must be a number")
            return



    def create_window(self, index):
        self.index = index

        self.top = tk.Toplevel(self.frame)
        self.top.geometry("400x300")

        self.lb_actual_value = ttk.Label(self.top,
                                         textvariable=self.text_actual_value,
                                         padding=5)

        self.lb_actual_value.grid(row=0, sticky='EW')
        self.lb1 = ttk.Label(self.top,
                             text='enter new value',
                             padding=5)
        self.lb1.grid(row=1,
                      sticky='EW')

        self.entry = tk.Entry(self.top)
        self.entry.grid(row=1, column=1)
        self.entry.bind('<Return>', self.check_input)

        self.run_edit(index)

    def run_edit(self, index):

        self.make_list_from_listbox_values()
        self.make_parameterstring_from_listbox_values()

        item = self.listbox.get(index)

        self.text_actual_value.set(item)

        print(item)

    def make_list_from_listbox_values(self):
        actual= self.listbox.get(0, tk.END)
        self.actual_values_list=[]

        for entry in actual:
            i = entry.split(',')[1]
            i=i.replace(" ","")
            self.actual_values_list.append(i)

    def make_parameterstring_from_listbox_values(self):
        self.parameter_new_string="PARAMETER"
        for v in self.actual_values_list:
            self.parameter_new_string += ',' + v

    def init_parameter(self):
        pass

    def send_parameterstring_to_esp(self):
        pass

    @property
    def get_parameter_string(self):
        return self.parameter_new_string

    def close_window(self):
        self.top.destroy()
        self.top.update()
        return

