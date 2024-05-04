import pickle
import os
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


class TrafficGraph:
    def __init__(self):
        self.df = pd.read_csv('Dataset/all_data.csv')
        # Convert Date to datetime format
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        # Creating Initial graph
        # Initial positions
        self.i_pos = {}
        # Graph attributes
        attributes = ['Date',
                      'Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
                      'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
                      'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19',
                      'Total_Vol']

        if os.path.exists('Dataset/cached_graph.pkl'):
            with open('Dataset/cached_graph.pkl', 'rb') as f:
                self.i_Graph = pickle.load(f)
        else:
            self.i_Graph = nx.Graph()
            for _, row in self.df.iterrows():
                edge_attributes = {attr: row[attr] for attr in attributes if attr in row}
                self.i_Graph.add_edge(row['Crossroads'], row['Road'], **edge_attributes)

                # Initial positions not appropriated yet
                self.i_pos[row['Crossroads']] = ([row['Lat.'], row['Lon.']])

            with open('Dataset/cached_graph.pkl', 'wb') as f:
                pickle.dump(self.i_Graph, f)

        # Creating Display figure
        self.display_Graph = nx.Graph()
        self.init_graph()

        self.shortest_path = []
        self.percentages = {}
        self.stats = {}

        self.figure, self.ax = plt.subplots()

    def init_graph(self):
        self.display_Graph = nx.Graph((u, v) for u, v in self.i_Graph.edges() if u != v)

    def clear_cache(self):
        cache_file = 'Dataset/cached_graph.pkl'
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("Cache cleared successfully.")
        else:
            print("Cache file does not exist.")

    def filter_deg(self, deg: int):
        self.display_Graph = nx.Graph((u, v) for u, v in self.i_Graph.edges()
                                      if u != v
                                      and self.i_Graph.degree(u) >= deg
                                      and self.i_Graph.degree(v) >= deg)

    def filter_shortest_path(self, source, target):
        self.shortest_path = bidirectional_bfs_shortest_path(self.i_Graph, source, target)
        if self.shortest_path:
            self.display_Graph = nx.Graph((self.shortest_path[i], self.shortest_path[i + 1])
                                          for i in range(len(self.shortest_path) - 1))
        else:
            self.shortest_path = []
            self.display_Graph = nx.Graph()

    def find_percentages(self):
        self.percentages = {attr: 0 for attr in self.i_Graph.edges[list(self.i_Graph.edges())[0]]
                            if attr != 'Total_Vol' and attr != 'Date'}

        if self.shortest_path:
            total_volume = 0
            for i in range(len(self.shortest_path) - 1):
                edge = self.i_Graph[self.shortest_path[i]][self.shortest_path[i + 1]]
                total_volume += edge['Total_Vol']

            for i in range(len(self.shortest_path)-1):
                edge = self.i_Graph[self.shortest_path[i]][self.shortest_path[i + 1]]
                for attr in self.percentages:
                    self.percentages[attr] += float(edge[attr])

            for attr in self.percentages:
                self.percentages[attr] = (self.percentages[attr] / total_volume) * 100

    def find_stats(self, series1=None, series2=None):
        stats_dict = {}

        series_list = [series1, series2]
        for series in series_list:
            if series:
                stats_dict[series] = {
                    'Centrality': {
                        'mean': self.df[series1].mean(),
                        'median': self.df[series1].median(),
                        'mode': self.df[series1].mode().tolist()
                    },
                    'Variability': {
                        'range': self.df[series1].max() - self.df[series1].min(),
                        'variance': self.df[series1].var(),
                        'standard deviation': self.df[series1].std(),
                        'IQR': self.df[series1].quantile(0.75) - self.df[series1].quantile(0.25)
                    }
                }
        if series1 and series2:
            stats_dict['Comparison'] = {
                'covariance': self.df[[series1, series2]].cov().iloc[0, 1],
                'correlation coefficient': self.df[[series1, series2]].corr().iloc[0, 1]
            }

        self.stats = stats_dict

    def find_proportions(self):
        pass

    def init_graph_figure(self, resolution=100, **kwargs):
        self.ax.clear()
        plt.gcf().set_dpi(resolution)

        nx.draw(self.display_Graph, ax=self.ax, **kwargs)
        # self.figure.canvas.draw()
        self.figure = plt.gcf()

    def init_time_series_figure(self, series1=None, series2=None, resolution=100):
        plt.figure()
        plt.gcf().set_dpi(resolution)

        if series1:
            plt.plot(self.df['Date'], self.df[series1], label=series1)
        if series2:
            plt.plot(self.df['Date'], self.df[series2], label=series2)

        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.legend()
        self.figure = plt.gcf()

    def init_distribution_figure(self, series1=None, series2=None, resolution=100, **kwargs):
        plt.figure()
        plt.gcf().set_dpi(resolution)

        if series1:
            plt.hist(self.df[series1], label=series1, density=True, **kwargs)

        if series2:
            plt.hist(self.df[series2], label=series2, density=True, **kwargs)

        plt.legend(prop={'size': 16}, title='Attributes')
        plt.xlabel('Volume')
        plt.ylabel('Density')
        plt.xlim(left=0)

        self.figure = plt.gcf()

    def show_figure(self):
        """
        sets current figure as the object's figure and shows it
        """
        if self.figure:
            plt.figure(self.figure.number)
            plt.show()
        else:
            print("Plot has not been initialized. Call init_plot first.")


def combine_paths(prev, succ, w):
    path = []
    while w is not None:
        path.append(w)
        w = prev[w]
    path.reverse()
    w = succ[path[-1]]
    while w is not None:
        path.append(w)
        w = succ[w]

    return path


def bidirectional_bfs_shortest_path(G, source, target):
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    elif source == target:
        return [source, target]

    Gprev = G.adj
    Gsucc = G.adj

    prev = {source: None}
    succ = {target: None}

    forward_path = [source]
    reverse_path = [target]

    while forward_path and reverse_path:
        if len(forward_path) <= len(reverse_path):
            this_level = forward_path
            forward_path = []
            for v in this_level:
                for w in Gsucc[v]:
                    if w not in prev:
                        forward_path.append(w)
                        prev[w] = v
                    if w in succ:
                        return combine_paths(prev, succ, w)
        else:
            this_level = reverse_path
            reverse_path = []
            for v in this_level:
                for w in Gprev[v]:
                    if w not in succ:
                        succ[w] = v
                        reverse_path.append(w)
                    if w in prev:  # found path
                        return combine_paths(prev, succ, w)


# Potential functionality

# def filter_df_by_month(self, month: int):
#     self.df = self.df[self.df['Date'].dt.month == month]

# # Filtering the dataframe by month
# filtered_df = df  # [df['Date'].dt.month == 10]

# Graph Layout
# pos = nx.fruchterman_reingold_layout(self.display_Graph)


if __name__ == "__main__":
    traffic = TrafficGraph()
    traffic.clear_cache()
    traffic.filter_shortest_path('AlongthePhasiCharoenCanal,northside', 'WangHin')

    traffic.find_percentages()
    print(traffic.percentages)

    traffic.init_graph_figure(resolution=500, node_size=0.5, font_size=5, width=0.5, with_labels=True)
    traffic.show_figure()

    traffic.init_time_series_figure('Total_Vol', 'Car_9-17')
    traffic.show_figure()

    traffic.init_distribution_figure('Total_Vol', 'Car_9-17')
    traffic.show_figure()
    traffic.find_stats('Total_Vol', 'Car_9-17')
    print(traffic.stats)
