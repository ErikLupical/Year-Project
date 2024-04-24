from graph import *
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UI:
    def __init__(self):
        self.root = Tk()

        # Initializing Graph
        self.traffic_graph = TrafficGraph()
        self.traffic_graph.draw_graph()

        # Creating and showing Graph
        self.canvas = FigureCanvasTkAgg(self.traffic_graph.plot, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        self.description_frame = LabelFrame(text="Description")

        self.description = Text(self.description_frame, width=80, height=10)
        self.description.pack()

        self.description_frame.grid(row=1, column=0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    UI = UI()
    UI.run()

#     self.tabs = ttk.Notebook(self.root)
#     self.tabs.pack()
#
# def new_tab(self):
#     new_tab = Frame(self.tabs)
#     new_tab.pack()
