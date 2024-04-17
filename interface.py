from tkinter import *
from tkinter import ttk

class UI:
    def __init__(self):
        self.root = Tk()
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack()

    def new_tab(self):
        new_tab = Frame(self.tabs)
        new_tab.pack()

    def run(self):
        self.root.mainloop()


root = Tk()

frame = LabelFrame(root)
frame.pack()

root.mainloop()
