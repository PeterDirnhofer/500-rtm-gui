import tkinter as tk
from  tkinter import ttk

class View(tk.Tk):
    def __init__(self, controller):

        super().__init__() # Initializes methods of Tk. Tk can be used in View

        self.controller = controller # controller can be used as attribute in class View

    def main(self):
        self.mainloop()  # Tk mainloop


