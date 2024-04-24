import copy
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

        # Creating Display graph
        self.display_Graph = nx.Graph()
        self.init_graph()
        self.shortest_path = []

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
        self.display_Graph = nx.Graph((self.shortest_path[i], self.shortest_path[i + 1])
                                      for i in range(len(self.shortest_path) - 1))

    def draw_graph(self, node_size=0.5, font_size=2.5, edge_width=0.5, resolution=500, with_labels=True, with_weights=False, weight_attribute='Total_Vol'):

        # Graph Layout
        pos = nx.fruchterman_reingold_layout(self.display_Graph)

        nx.draw(self.display_Graph, pos, with_labels=with_labels, node_size=node_size, font_size=font_size, width=edge_width)

        # Drawing edges
        if with_weights:
            edge_labels = {(u, v): f"{w:.0f}" for (u, v, w) in self.display_Graph.edges(data=weight_attribute)}
            nx.draw_networkx_edge_labels(self.display_Graph, pos, edge_labels=edge_labels, font_size=4)

        plt.gcf().set_dpi(resolution)
        self.plot = plt.gcf()
        plt.show()


# def filter_df_by_month(self, month: int):
#     self.df = self.df[self.df['Date'].dt.month == month]

# def reset_df(self):
#     self.df = pd.read_csv('Dataset/all_data.csv')

# def filter_loops(self):
#     self.Graph = self.Graph.subgraph([node for node in self.Graph.nodes() if not self.Graph.has_edge(node, node)])


# # Filtering the dataframe by month
# filtered_df = df  # [df['Date'].dt.month == 10]

# looplessG = G.subgraph([node for node in G.nodes() if not G.has_edge(node, node)])

# subG = G.subgraph([node for node, degree in looplessG.degree if degree >= 2])

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
        return [source]

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


if __name__ == "__main__":
    traffic = TrafficGraph()
    traffic.clear_cache()
    traffic.filter_shortest_path('AlongthePhasiCharoenCanal,northside', 'WangHin')

    traffic.draw_graph()
