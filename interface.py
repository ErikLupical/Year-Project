from graph import *

from abc import ABC, abstractmethod

from tkinter import *
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np


class UI(Tk):
    def __init__(self):
        super().__init__()
        self.title("Hekate")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.create_new_tab()

        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        new_button = Button(button_frame, text="New Tab", command=self.create_new_tab)
        new_button.pack(side="right", fill="x", expand=True)

        close_button = Button(button_frame, text="Close Tab", bg='pink', command=self.close_current_tab)
        close_button.pack(side="left", fill="x", expand=True)

    def create_new_tab(self):
        tab = Tab(self.notebook)  # ttk.Frame(self.notebook)

        self.notebook.add(tab.get_frame(), text=f"Tab {self.notebook.index('end')+1}")

    def close_current_tab(self):
        current_tab_index = self.notebook.index(self.notebook.select())

        if self.notebook.index('end') > 0:
            self.notebook.forget(current_tab_index)
            if self.notebook.index('end') == 0:
                self.create_new_tab()

    def run(self):
        self.mainloop()


class Tab:
    def __init__(self, notebook):
        # New Frame
        self.frame = Frame(notebook)

        self.traffic = TrafficGraph()
        self.state = None

        # Dropdown Menu
        self.option = StringVar()
        self.option.set('Choose type of figure')
        self.drop_option = OptionMenu(self.frame, self.option,
                                      'Graph',
                                      'Pie',
                                      'Distribution',
                                      'TimeSeries',
                                      command=self.switch_state)

        # Canvas
        self.canvas_frame = Frame(self.frame)
        self.figure = self.traffic.figure

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="ew")

        toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame, pack_toolbar=False)
        toolbar.grid(row=1, column=0, sticky="nsew")

        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(1, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        # Description frame
        self.description_frame = LabelFrame(self.frame, text="Description")
        self.description = Text(self.description_frame, width=80, height=10)
        self.description.pack()

        # Combo boxes
        self.combo1_var = StringVar()
        self.combo2_var = StringVar()

        self.combo_frame = Frame(self.frame)
        self.combobox1 = ttk.Combobox(self.combo_frame, width=50, textvariable=self.combo1_var, values=[])
        self.combobox1.grid(row=0, column=0, padx=20, pady=10)

        arrow = Label(self.combo_frame, text='↹', anchor='center')
        arrow.grid(row=0, column=1)

        self.combobox2 = ttk.Combobox(self.combo_frame, width=50, textvariable=self.combo2_var, values=[])
        self.combobox2.grid(row=0, column=3, padx=20, pady=10)

        run_button = Button(self.combo_frame, text='Run', command=self.run_process, padx=10)
        run_button.grid(row=0, column=4, padx=20, pady=10)

        self.combo_frame.rowconfigure(0, weight=1)
        self.combo_frame.columnconfigure(0, weight=1)
        self.combo_frame.columnconfigure(1, weight=1)
        self.combo_frame.columnconfigure(2, weight=1)
        self.combo_frame.columnconfigure(3, weight=1)

        # Treeview
        self.tree = ttk.Treeview(self.frame, columns=('Attribute', 'Value'), show='headings')
        self.tree.heading('Attribute', text='Attribute')
        self.tree.heading('Value', text='Value')

        self.init_place_components()

    def init_place_components(self):
        self.drop_option.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")
        self.description_frame.grid(row=2, column=0, sticky="nsew")
        self.combo_frame.grid(row=0, column=1, sticky="nsew")
        self.tree.grid(row=1, column=1, rowspan=2, sticky="nsew")

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)

    def update_content(self):

        self.canvas.draw()

    def switch_state(self, option):
        states = {
            'Graph': GraphState,
            'Pie': PieState,
            'Distribution': DistributionState,
            'TimeSeries': TimeSeriesState
        }
        state_class = states[option]
        self.state = state_class(self)
        self.state.set_content()

    def run_process(self):
        if self.state:
            self.state.run_process()

    def get_frame(self):
        return self.frame


class TabState(ABC):
    def __init__(self, tab):
        self.tab = tab

    @abstractmethod
    def set_content(self):
        raise NotImplemented

    @abstractmethod
    def run_process(self):
        raise NotImplemented

    def set_treeview(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.tab.tree.insert('', 'end', values=(key, ''))
                self.set_treeview(value)
            elif isinstance(value, list):
                self.tab.tree.insert('', 'end', values=(key, f'{str(value)}'))
            else:
                self.tab.tree.insert('', 'end', values=(key, f'{value:.3f}'))


class GraphState(TabState):
    def set_content(self):
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)
        self.tab.canvas.get_tk_widget().grid_forget()

        self.tab.traffic.init_graph()
        self.tab.traffic.init_graph_figure(node_size=0.5, font_size=5, width=0.5, with_labels=True)

        self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
        self.tab.canvas.draw()
        self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Combo boxes
        crossroads_unique = self.tab.traffic.df['Crossroads'].unique()
        road_unique = self.tab.traffic.df['Road'].unique()
        self.tab.combobox1.config(values=list(np.sort(list(set(np.concatenate((crossroads_unique, road_unique)))))))
        self.tab.combobox2.config(values=list(np.sort(list(set(np.concatenate((crossroads_unique, road_unique)))))))

        self.tab.update_content()

    def run_process(self):
        # Display shortest_path graph
        self.tab.traffic.filter_shortest_path(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))

        self.tab.traffic.init_graph_figure(with_labels=True)
        self.tab.canvas.get_tk_widget().grid_forget()
        self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
        self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_percentages()

        intervals = ['7-9', '9-17', '17-19']
        percentages_intervals = {interval: {} for interval in intervals}

        # Separate the percentages based on the time interval
        for attr, value in self.tab.traffic.percentages.items():
            for interval in intervals:
                if interval in attr:
                    vehicle = attr.split('_')[0]
                    percentages_intervals[interval][vehicle] = value

        # for interval in intervals:
        #     self.tab.tree.insert('', 'end', values=(f"Interval {interval}", ""))
        #     for vehicle, value in percentages_intervals[interval].items():
        #         self.tab.tree.insert('', 'end', values=(vehicle, f"{value:.3f}%"))

        self.set_treeview(percentages_intervals)

        self.tab.update_content()


class PieState(TabState):
    def set_content(self):
        pass

    def run_process(self):
        raise NotImplemented


class DistributionState(TabState):
    def set_content(self):
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)
        self.tab.canvas.get_tk_widget().grid_forget()

        self.tab.traffic.init_distribution_figure()

        self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
        self.tab.canvas.draw()
        self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Combo boxes
        self.tab.combobox1.config(values=['Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                                          'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                                          'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19', 'Total_Vol'],)
        self.tab.combobox2.config(values=['Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                                          'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                                          'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19', 'Total_Vol'])

        self.tab.update_content()

    def run_process(self):
        if str(self.tab.combo1_var.get()) or str(self.tab.combo2_var.get()):
            self.tab.traffic.init_distribution_figure(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()), bins=50, alpha=0.5,)
            self.tab.canvas.get_tk_widget().grid_forget()
            self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
            self.tab.canvas.draw()
            self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_stats(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))
        self.set_treeview(self.tab.traffic.stats)

        self.tab.update_content()


class TimeSeriesState(TabState):
    def set_content(self):
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)
        self.tab.canvas.get_tk_widget().grid_forget()

        self.tab.traffic.init_time_series_figure()

        self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
        self.tab.canvas.draw()
        self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Combo boxes
        self.tab.combobox1.config(values=['Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                                          'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                                          'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19', 'Total_Vol'],)
        self.tab.combobox2.config(values=['Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                                          'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                                          'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19', 'Total_Vol'])

        self.tab.update_content()

    def run_process(self):
        if str(self.tab.combo1_var.get()) or str(self.tab.combo2_var.get()):
            self.tab.traffic.init_time_series_figure(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))
            self.tab.canvas.get_tk_widget().grid_forget()
            self.tab.canvas = FigureCanvasTkAgg(self.tab.traffic.figure, master=self.tab.canvas_frame)
            self.tab.canvas.draw()
            self.tab.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_stats(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))
        self.set_treeview(self.tab.traffic.stats)

        self.tab.update_content()


if __name__ == "__main__":
    UI = UI()
    UI.run()
