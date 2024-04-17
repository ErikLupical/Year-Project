import pickle
import os
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


class TrafficGraph:
    def __init__(self):
        self.df = pd.read_csv('Dataset/all_data.csv')
        # Convert Date to datetime format
        self.df['Date'] = pd.to_datetime(df['Date'])

        self.i_pos = {}

        if os.path.exists('Dataset/cached_graph.pkl'):
            with open('Dataset/cached_graph.pkl', 'rb') as f:
                self.Graph = pickle.load(f)

        else:
            self.Graph = nx.Graph
            for _, row in self.df.iterrows():
                self.Graph.add_edge(row['Crossroads'], row['Road'])  # , weight=row[weight])
                self.i_pos[row['Crossroads']] = ([row['Lat.'], row['Lon.']])

            # Graph Layout
            self.pos = nx.fruchterman_reingold_layout(self.Graph)

            with open('Dataset/all_data.csv', 'wb') as f:
                pickle.dump(self.Graph, f)

    def filter_df_by_month(self, month: int):
        self.df = self.df[df['Date'].dt.month == month]

    def reset_df(self):
        self.df = pd.read_csv('Dataset/all_data.csv')

    def filter_deg(self, deg: int):
        self.Graph = self.Graph.subgraph([node for node, degree in looplessG.degree if degree >= deg])

    def filter_loops(self):
        self.Graph = self.Graph.subgraph([node for node in G.nodes() if not G.has_edge(node, node)])

    def draw_graph(self, node_size, font_size, edge_width, resolution=500, with_labels=True):
        nx.draw(self.Graph, self.pos, with_labels=with_labels, node_size=node_size, font_size=font_size, width=edge_width)

        # Drawing edges
        # edge_labels = {(u, v): f"{w:.0f}" for (u, v, w) in G.edges(data='weight')}
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=4)

        plt.gcf().set_dpi(resolution)
        plt.show()


# weights = ['Date',
#            'Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
#            'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
#            'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19',
#            'Total_Vol']
# weight = 'Total_Vol'


df = pd.read_csv('Dataset/all_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

G = nx.Graph()

# Filtering the dataframe by month
filtered_df = df  # [df['Date'].dt.month == 10]

i_pos = {}

for _, row in filtered_df.iterrows():
    G.add_edge(row['Crossroads'], row['Road'])  # , weight=row[weight])
    i_pos[row['Crossroads']] = ([row['Lat.'], row['Lon.']])

looplessG = G.subgraph([node for node in G.nodes() if not G.has_edge(node, node)])

subG = G.subgraph([node for node, degree in looplessG.degree if degree >= 2])


pos = nx.fruchterman_reingold_layout(subG)


nx.draw(subG, pos, with_labels=True, node_size=0.5, font_size=5, width=0.5)

# Drawing edges
# edge_labels = {(u, v): f"{w:.0f}" for (u, v, w) in G.edges(data='weight')}
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=4)

plt.gcf().set_dpi(500)
plt.show()
