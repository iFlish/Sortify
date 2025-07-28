import os
import subprocess

def build_cpp_library():
    cpp_file = "sort.cpp"
    output_file = "libsort.so"
    if os.path.exists(cpp_file):
        print("🛠 Compiling C++...")
        result = subprocess.run(
            ["g++", "-shared", "-o", output_file, "-fPIC", cpp_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ C++ compiled successfully.")
        else:
            print("❌ Compilation failed:")
            print(result.stderr)
    else:
        print("❌ sort.cpp not found!")

# Example: call this before launching the GUI
build_cpp_library()
