import os
from pathlib import Path

import clang.cindex
import matplotlib.pyplot as plt
import networkx as nx


def collect_header_directories(root_dir):
    header_dirs = set()
    for path in Path(root_dir).rglob("*.h"):  # Search for .h headers
        header_dirs.add(path.parent)  # Add the parent directory of each header
    return header_dirs


JDK_SOURCE_DIR = Path(os.path.join(os.getenv("HOME") or "C:\\", "Users", "sarps", "IdeaProjects", "jdk21", "src"))
header_dirs = collect_header_directories(JDK_SOURCE_DIR)
include_args = [f"-I{str(header_dir)}" for header_dir in header_dirs]


# Initialize Clang - Adjust the path to your libclang.dll file
clang.cindex.Config.set_library_file(r'C:\Program Files\LLVM\bin\libclang.dll')


# Function to preprocess and clean up the file
def preprocess_file(file_path):
    if 'processed' in file_path:
        return None

    with open(file_path, 'r') as file:
        content = file.read()

    # Replace JNI macros with empty definitions
    content = content.replace('(*env)->', '').replace('JNIEXPORT', '').replace('JNICALL', '')

    # Write the processed content to a temporary file
    if file_path.endswith('cpp'):
        temp_file_path = file_path + '.processed.cpp'
    else:
        temp_file_path = file_path + '.processed.c'
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(content)

    return temp_file_path

# Function to extract function calls from a file
def extract_function_calls(file_path):
    index = clang.cindex.Index.create()
    args = ['-x', 'c++', '-std=c++17'] + include_args if file_path.endswith('.cpp') else ['-x', 'c'] + include_args
    translation_unit = index.parse(file_path, args=args)
    function_calls = {}

    def visit_node(node, parent_func=None):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Track function declarations
            parent_func = node.spelling or node.displayname
            if parent_func not in function_calls:
                function_calls[parent_func] = []
        elif node.kind == clang.cindex.CursorKind.CALL_EXPR and parent_func:
            # Capture function calls
            referenced = node.referenced
            callee_func = referenced.spelling if referenced else node.displayname
            if callee_func:
                function_calls[parent_func].append(callee_func)
        for child in node.get_children():
            visit_node(child, parent_func)

    try:
        visit_node(translation_unit.cursor)
    except Exception as e:
        print(f"Error visiting nodes in {file_path}: {e}")

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

# Updated loop to handle preprocessing and extraction robustly
function_calls = {}
all_files = JDK_SOURCE_DIR.rglob("*")
for native_file in all_files:
    if native_file.is_file() and native_file.suffix in [".c", ".cpp"]:
        try:
            file = str(native_file)
            print(f"Processing file {file}")
            processed_file = preprocess_file(file)
            if not processed_file:
                print(f"Skipped {file} (already processed)")
                continue
            print(f"Preprocessed file {processed_file}")
            file_calls = extract_function_calls(processed_file)
            for key, value in file_calls.items():
                function_calls.setdefault(key, []).extend(value)
            os.remove(processed_file)
            print(f"Finished processing file {native_file}")
        except Exception as e:
            print(f"Error processing file {native_file}: {e}")

# Rest of the logic remains unchanged
call_graph = create_call_graph(function_calls)
