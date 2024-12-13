import json
import os
import clang.cindex
import networkx as nx
import matplotlib.pyplot as plt

# Initialize Clang - Adjust the path to your libclang.dll file
clang.cindex.Config.set_library_file(r'C:\Program Files\LLVM\bin\libclang.dll')


# Function to extract function calls from a file
def extract_function_calls(file_path):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path)
    function_calls = {}

    def visit_node(node, parent_func=None):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            parent_func = node.spelling
            if parent_func not in function_calls:
                function_calls[parent_func] = []
        if node.kind == clang.cindex.CursorKind.CALL_EXPR and parent_func:
            function_calls[parent_func].append(node.spelling)
        for child in node.get_children():
            visit_node(child, parent_func)

    visit_node(translation_unit.cursor)
    return function_calls


# Create a graph from function calls
def create_call_graph(function_calls):
    G = nx.DiGraph()
    for caller, callees in function_calls.items():
        for callee in callees:
            G.add_edge(caller, callee)
    return G


# Function to visualize the call graph
def visualize_call_graph(G, output_file='call_graph.png'):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
    plt.title("Call Graph")
    plt.savefig(output_file)
    plt.show()


# Path to your JSON file
json_file_path = "../native_functions.json"

# Load JSON data
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

# Extract and check system calls from each file
function_calls = {}
for function, file_list in data.items():
    for file in file_list:
        if os.path.exists(file):
            function_calls.update(extract_function_calls(file))
        else:
            print(f"File {file} not found.\n")

# Create and visualize the call graph
call_graph = create_call_graph(function_calls)
visualize_call_graph(call_graph)
