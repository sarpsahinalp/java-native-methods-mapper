import pickle

def load_graph(filename):
    with open(filename, 'rb') as f:
        graph = pickle.load(f)
        print(f"Graph deserialized from {filename}")
        return graph

loaded = load_graph('call_graph_v2.pkl')

print(load_graph('call_graph_v2.pkl'))