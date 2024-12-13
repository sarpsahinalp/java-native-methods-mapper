import json
import os
import pickle

import clang.cindex
import networkx as nx
import matplotlib.pyplot as plt
import signal

# Initialize Clang - Adjust the path to your libclang.dll file
clang.cindex.Config.set_library_file(r'C:\Program Files\LLVM\bin\libclang.dll')


# Function to preprocess and clean up the file
def preprocess_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Replace JNI macros with empty definitions
    content = content.replace('JNIEXPORT', '').replace('JNICALL', '').replace('JNIEnv', 'void').replace('jclass',
                                                                                                        'void').replace(
        'jobject', 'void')

    # Write the processed content to a temporary file
    if file_path.endswith('.cpp'):
        temp_file_path = file_path + '.processed.cpp'
    else:
        temp_file_path = file_path + '.processed.c'
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(content)

    return temp_file_path


# Function to extract function calls from a file
def extract_function_calls(file_path):
    index = clang.cindex.Index.create()
    args = ['-x', 'c++'] if file_path.endswith('.cpp') else ['-x', 'c']
    translation_unit = index.parse(file_path, args=args)
    function_calls = {}

    def visit_node(node, parent_func=None):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Use the display name to capture the full function name
            parent_func = node.spelling
            if parent_func not in function_calls:
                function_calls[parent_func] = []
        if node.kind == clang.cindex.CursorKind.CALL_EXPR and parent_func:
            # Use the spelling to capture the called function name
            callee_func = node.spelling
            if callee_func != '':
                function_calls[parent_func].append(callee_func)
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
            # Preprocess the file to handle JNI macros
            processed_file = preprocess_file(file)
            print(f"Preprocessed {processed_file}")
            function_calls.update(extract_function_calls(processed_file))
            print(f"Extracted function calls from {file}")
            os.remove(processed_file)


def save_graph(graph, filename):
    with open(filename, 'wb') as f:
        pickle.dump(graph, f)
        print(f"Graph serialized to {filename}")

# Create and visualize the call graph
call_graph = create_call_graph(function_calls)
print('Created call graph')
save_graph(call_graph, 'call_graph.pkl')
visualize_call_graph(call_graph)
