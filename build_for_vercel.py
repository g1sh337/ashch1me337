#!/usr/bin/env python3
"""Build script for Vercel deployment"""
import os
import shutil
import subprocess

print("=== Starting Pygbag build ===")

# Run Pygbag build
result = subprocess.run([
    "python", "-m", "pygbag", 
    "--build", 
    "--ume_block", "0",
    "main.py"
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Enable autorun in generated HTML
index_path = "build/web/index.html"
if os.path.exists(index_path):
    print(f"=== Updating {index_path} ===")
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('autorun : 0', 'autorun : 1')
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("=== Autorun enabled ===")
    
    # Copy to play.html
    shutil.copy(index_path, "play.html")
    print("=== Copied to play.html ===")
else:
    print(f"ERROR: {index_path} not found!")
    exit(1)

print("=== Build complete ===")
