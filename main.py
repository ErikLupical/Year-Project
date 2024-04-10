import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv('Dataset/all_data.csv')

G = nx.Graph()

weights = ['Date',
           'Car_7-9', 'Van_7-9', 'Bus_7-9', 'Minibus_7-9', 'Truck_7-9', '3Cycle_7-9',
           'Car_9-17', 'Van_9-17', 'Bus_9-17', 'Minibus_9-17', 'Truck_9-17', '3Cycle_9-17',
           'Car_17-19', 'Van_17-19', 'Bus_17-19', 'Minibus_17-19', 'Truck_17-19', '3Cycle_17-19',
           'Total_Vol']

weight = 'Total_Vol'

for _, row in df.iterrows():
    if row['Crossroads'] == row['Road']:
        G.add_node(row['Crossroads'])
    else:
        G.add_edge(row['Crossroads'], row['Road'])
    # G.nodes[row['Crossroads']]['location'] = (row['Lat.'], row['Lon.'])

pos = nx.kamada_kawai_layout(G)
print(pos)

nx.draw(G, pos, with_labels=False, node_size=1, font_size=5)
plt.show()
