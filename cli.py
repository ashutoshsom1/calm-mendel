"""
Shim entrypoint for backwards compatibility.
You can run this file directly via `python cli.py` or install the package
and use the console command `linkedin-jobhunter`.
"""
import sys
from pathlib import Path

# Add src to sys.path if running directly from checkout
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from linkedin_jobhunter.cli import main

if __name__ == "__main__":
    main()
