import os
import re
from codecs import ignore_errors
from pathlib import Path
import json
from collections import defaultdict

# Paths
JDK_SOURCE_DIR = Path("/home/sarps/IdeaProjects/jdk22")
RESULTS_FILE = "native_methods_mapping.json"

# Regex Patterns
JAVA_NATIVE_METHOD_PATTERN = re.compile(
    r"(?:private|protected|public)?\s*(?:static)?\s*(?:synchronized)?\s*native\s+\w+\s+(\w+)\s*\(.*\)\s*(?:throws\s+\w+(?:,\s*\w+)*)?\s*;"
)
NATIVE_FUNCTION_PATTERN = re.compile(
    r"\bJNIEXPORT\s+\w+\s+JNICALL\s+(\w+)\s*\(.*?\)", re.DOTALL
)


# Step 1: Discover Native Methods in Java
def discover_native_methods(java_source_dir):
    print("Discovering native methods in Java source files...")
    native_methods = defaultdict(list)
    count = 0

    for java_file in java_source_dir.rglob("*"):
        if java_file.is_file() and java_file.suffix in [".java"]:
            with open(java_file, "r", errors="ignore") as file:
                content = file.read()
                for match in JAVA_NATIVE_METHOD_PATTERN.finditer(content):
                    count += 1
                    method_name = match.group(1)
                    native_methods[str(java_file)].append(method_name)
    print(f"Discovered {count} native methods.")
    return native_methods


# Step 2: Map Native Methods to C/C++ Functions
def index_native_files(native_source_dir):
    print("Indexing C/C++ files...")
    function_map = defaultdict(list)
    for native_file in native_source_dir.rglob("*"):
        if native_file.is_file() and native_file.suffix in [".c", ".cpp"]:
            try:
                with open(native_file, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    for match in NATIVE_FUNCTION_PATTERN.finditer(content):
                        function_name = match.group(1)
                        function_map[function_name].append(str(native_file))
            except Exception as e:
                print(f"Error processing file {native_file}: {e}")
    print(f"Indexed {len(function_map)} native functions.")
    return function_map


# Main Function
def main():
    native_methods = discover_native_methods(JDK_SOURCE_DIR)
    native_function_index = index_native_files(JDK_SOURCE_DIR)

    # save the native methods and functions as a json in different files and create a new file
    with open("native_methods_jdk22.json", "w") as f:
        json.dump(native_methods, f, indent=4)

    with open("native_functions_jdk22.json", "w") as f:
        json.dump(native_function_index, f, indent=4)

    print("Completed")


if __name__ == "__main__":
    main()
