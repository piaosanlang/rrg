import subprocess
from pathlib import Path

root_dir = Path(__file__).parent.parent

print("Installing dependencies...")
subprocess.run(["npm", "install"], cwd=root_dir, check=True)

print("\nBuilding project...")
subprocess.run(["npm", "run", "build"], cwd=root_dir, check=True)

print("\nStarting server...")
subprocess.run(["npm", "run", "preview"], cwd=root_dir)
