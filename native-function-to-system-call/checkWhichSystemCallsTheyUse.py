import json
import os
import subprocess

# Path to your JSON file
json_file_path = "../native_functions_jdk22.json"


# Function to extract functions from C files using ctags
def extract_functions(file):
    tags_output = subprocess.check_output(["ctags", "-x", "--c-kinds=fp", file])
    functions = [line.split()[0] for line in tags_output.decode("utf-8").split("\n") if line]
    return functions


# Function to parse C files and check for system calls
def check_syscalls(file, functions):
    syscalls = []
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if any(func in line for func in functions):
                if "syscall" in line:
                    syscalls.append(line.strip())
    return syscalls


# Load JSON data
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

# Extract and check system calls from each file
for function, file_list in data.items():
    for file in file_list:
        if os.path.exists(file):
            functions = extract_functions(file)
            syscalls = check_syscalls(file, functions)
            print(f"System calls in {file} ({function}):")
            for syscall in syscalls:
                print(syscall)
            print("\n")
        else:
            print(f"File {file} not found.\n")
