from graph import *

from abc import ABC, abstractmethod

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np


class UI(Tk):
    def __init__(self):
        super().__init__()
        self.title("Hekate")
        # self.attributes('-fullscreen', True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.create_new_tab()

        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        close_button = Button(button_frame, text="Close Tab", bg='pink', command=self.close_current_tab)
        close_button.pack(side="left", fill="x", expand=True)

        exit_button = Button(button_frame, text="Quit", bg='pink', command=self.destroy)
        exit_button.pack(side="left", fill="x", expand=True)

        new_button = Button(button_frame, text="New Tab", command=self.create_new_tab)
        new_button.pack(side="left", fill="x", expand=True)

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
        self.traffic = TrafficGraph()
        self.state = NullState(self)

        # New Frame
        self.frame = Frame(notebook)

        # Dropdown Menu
        option = StringVar()
        option.set('Choose type of figure')
        self.drop_option = OptionMenu(self.frame, option,
                                      'Graph',
                                      'Distribution',
                                      'TimeSeries',
                                      command=self.switch_state)

        # Canvas
        self.figure = self.traffic.figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)

        # Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame, pack_toolbar=False)

        # Description frame
        description_frame = LabelFrame(self.frame, text="Description")
        self.description = Text(description_frame, width=80, height=10)
        self.description.pack()

        # Stats frame
        stats_frame = Frame(self.frame)

        # Combo boxes
        self.combo1_var = StringVar()
        self.combo2_var = StringVar()

        self.combobox1 = ttk.Combobox(stats_frame, width=50, textvariable=self.combo1_var, values=[])
        self.combobox1.grid(row=0, column=0, padx=20, pady=10)

        arrow = Label(stats_frame, text='↹', anchor='center', font=("Segoe UI", 12))
        arrow.grid(row=0, column=1)

        self.combobox2 = ttk.Combobox(stats_frame, width=50, textvariable=self.combo2_var, values=[])
        self.combobox2.grid(row=0, column=3, padx=20, pady=10)

        run_button = Button(stats_frame, text='Run', command=self.run_process, padx=10)
        run_button.grid(row=0, column=4, padx=20, pady=10)

        # Treeview
        # TODO add scrollbar
        self.tree = ttk.Treeview(stats_frame, columns=('Attribute', 'Value'), show='headings')
        self.tree.heading('Attribute', text='Attribute')
        self.tree.heading('Value', text='Value')
        self.tree.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=20)

        # Story buttons
        story_frame = Frame(stats_frame)

        reset_button = Button(story_frame, text='Reset Tab', command=self.reset_tab)
        reset_button.pack(side='left', fill='x', expand=True)

        story_button = Button(story_frame, text='Storytelling', command=self.tell_story)
        story_button.pack(side='left', fill='x', expand=True)

        story_frame.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=20, pady='10')

        stats_frame.rowconfigure(0, weight=1)

        # Configure stat frame components
        stats_frame.rowconfigure(0, weight=0)
        stats_frame.rowconfigure(1, weight=1)
        stats_frame.rowconfigure(2, weight=0)

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        # Place components
        self.drop_option.grid(row=0, column=0, sticky="nsew")
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        toolbar.grid(row=2, column=0, sticky="nsew")
        description_frame.grid(row=3, column=0, sticky="nsew")

        stats_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=1)

    def update_figure(self):
        self.canvas.get_tk_widget().grid_forget()
        self.canvas = FigureCanvasTkAgg(self.traffic.figure, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        toolbar = NavigationToolbar2Tk(self.canvas, self.frame, pack_toolbar=False)
        toolbar.grid(row=2, column=0, sticky="nsew")

    def update_description(self, text):
        self.description.delete('1.0', END)
        self.description.insert('1.0', text)

    def update_combobox(self, list1, list2):
        self.combobox1.config(values=list1)
        self.combobox2.config(values=list2)

    def update_treeview(self, dictionary, parent=''):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                node = self.tree.insert(parent, 'end', text=key, values=(key, ''))
                self.update_treeview(value, node)
            elif isinstance(value, list):  # List handling, converted to string for display.
                self.tree.insert(parent, 'end', values=(key, ', '.join(map(str, value))))
            else:  # Regular items with scalar values, formatting handled accordingly.
                formatted_value = f'{value:.3f}' if isinstance(value, float) else str(value)
                self.tree.insert(parent, 'end', values=(key, formatted_value))

    # TODO write reset handler
    def reset_tab(self):
        pass

    # TODO add loading screen
    def switch_state(self, option):
        states = {
            'Graph': GraphState,
            'Distribution': DistributionState,
            'TimeSeries': TimeSeriesState
        }
        state_class = states[option]
        self.state = state_class(self)
        self.state.set_content()
        self.drop_option.config(state='disabled')

    def run_process(self):
        self.state.run_process()

    def tell_story(self):
        self.state.tell_story()

    def get_frame(self):
        return self.frame


class TabState(ABC):
    def __init__(self, tab):
        self.tab = tab
        self.attributes = ['Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                           'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                           'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19',
                           'Total_Vol']

    @abstractmethod
    def set_content(self):
        raise NotImplemented

    @abstractmethod
    def run_process(self):
        raise NotImplemented

    @abstractmethod
    def tell_story(self):
        raise NotImplemented


class NullState(TabState):
    def set_content(self):
        pass

    def run_process(self):
        pass

    def tell_story(self):
        self.tab.update_description('Please choose a visualization type.')


class GraphState(TabState):
    def set_content(self):
        # Figure
        self.tab.traffic.init_graph()
        self.tab.traffic.init_graph_figure(node_size=0.5, font_size=10, width=0.5, with_labels=True)
        self.tab.update_figure()

        # Description
        self.tab.update_description('Use toolbar to navigate the graph')

        # Combo boxes
        unique_values = np.union1d(self.tab.traffic.df['Crossroads'].unique(), self.tab.traffic.df['Road'].unique())
        unique_list = unique_values.tolist()
        self.tab.update_combobox(unique_list, unique_list)

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

    def run_process(self):
        # Display shortest_path graph
        self.tab.traffic.filter_shortest_path(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))
        self.tab.traffic.init_graph_figure(with_labels=True)

        self.tab.update_figure()

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_percentages()

        intervals = ['7-9', '9-17', '17-19']
        percentages_intervals = {interval: {} for interval in intervals}
        # Separate the percentages based on the time interval
        for attr, value in self.tab.traffic.stats.items():
            for interval in intervals:
                if interval in attr:
                    vehicle = attr.split('_')[0]
                    percentages_intervals[interval][vehicle] = value

        self.tab.update_treeview(percentages_intervals)

    def tell_story(self):
        self.tab.combo1_var.set('LatPhrao')
        self.tab.combo2_var.set('PhongPhet')
        self.run_process()
        self.tab.update_description('The graph shows a path from the crossroad with the largest volume to the crossroad'
                                    ' with the 3rd largest volume. The treeview shows the percentage of different types'
                                    ' of vehicles seperated into different time periods. The majority of traffic'
                                    ' consists of cars, followed by a significantly smaller percentage of vans and'
                                    ' buses. The volume of minibuses, trucks, and bicycles is minimal.'
                                    ' This distribution remains relatively consistent during different times of the day'
                                    ' (7-9 am, 9-17 pm, 17-19 pm). This suggests that cars are the primary mode of'
                                    ' transportation in this area, regardless of the time of day.')


class DistributionState(TabState):
    def set_content(self):
        # Figure
        self.tab.traffic.init_distribution_figure()
        self.tab.update_figure()

        # Description
        self.tab.update_description('')

        # Combo boxes
        self.tab.update_combobox(self.attributes, self.attributes)

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

    def run_process(self):
        # Figure
        if str(self.tab.combo1_var.get()) or str(self.tab.combo2_var.get()):
            self.tab.traffic.init_distribution_figure(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()),
                                                      bins=50, alpha=0.5,)

            self.tab.update_figure()

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_stats(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))
        self.tab.update_treeview(self.tab.traffic.stats)

    def tell_story(self):
        self.tab.combo1_var.set('Car_9-17')
        self.tab.combo2_var.set('Total_Vol')
        self.run_process()
        self.tab.update_description('Both the distribution of cars between 9-17 and the total volume are positively '
                                    'skewed, with most data points concentrated towards the lower end of volume. This '
                                    'suggests that there are a few times when the volume is very high, but most of the '
                                    'time, the volume is relatively low. A high standard deviation or IQR indicates a '
                                    'wide spread of data around the mean. In this case, both distributions '
                                    'have a relatively high standard deviation, indicating a high variability in the '
                                    'volume of cars. The mean, median, and mode are measures of centrality. In this '
                                    'case, the mean and median are relatively close for both distributions, suggesting '
                                    'that distributions are not heavily skewed.')


class TimeSeriesState(TabState):
    def set_content(self):
        # Figure
        self.tab.traffic.init_time_series_figure()
        self.tab.update_figure()

        # Description
        self.tab.update_description('')

        # Combo boxes
        self.tab.update_combobox(self.attributes, self.attributes)

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

    def run_process(self):
        if str(self.tab.combo1_var.get()) or str(self.tab.combo2_var.get()):
            self.tab.traffic.init_time_series_figure(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()))

            self.tab.update_figure()

        # Treeview
        for i in self.tab.tree.get_children():
            self.tab.tree.delete(i)

        self.tab.traffic.find_stats(str(self.tab.combo1_var.get()), str(self.tab.combo2_var.get()), time_series=True)
        self.tab.update_treeview(self.tab.traffic.stats)
        print(self.tab.traffic.stats)

    def tell_story(self):
        self.tab.combo1_var.set('Car_9-17')
        self.tab.combo2_var.set('Total_Vol')
        self.run_process()
        self.tab.update_description('The volume for the most used vehicle within the period 9-17 has the highest value'
                                    'on Tuesday within a small range and the lowest value on Sunday with a large range.'
                                    'The most used vehicle is likely being used for purposes that align with a typical '
                                    'work week, such as commuting or business operations. This is suggested by the high'
                                    ' usage on Tuesday (a common workday) and low usage on Sunday (commonly a day off).')


if __name__ == "__main__":
    UI = UI()
    UI.run()
