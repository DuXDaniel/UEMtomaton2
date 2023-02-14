import sys
import os
from cx_Freeze import setup, Executable

PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

include_files = [(os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'), os.path.join('lib', 'tk86t.dll')),
                 (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'), os.path.join('lib', 'tcl86t.dll')),
                 "UEMtomaton_icon_256.ico"]

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

excludes = []
# "altgraph","colorama","cupy","Cython","dill","llvmlite","matplotlib","multiprocess","numba","numba-scipy","p-tqdm","pandas","PyQt5","PyQt5-Qt5","PyQt5-sip","scipy","scikit-learn","tqdm"
executables = [Executable('UEMtomaton.py', base=base, icon="UEMtomaton_icon_256.ico")]

setup(name = "UEMtomaton" ,
      version = "2.0" ,
      description = "Ultrafast laboratory implementation" ,
      options={'build_exe': {'include_files': include_files,'excludes':excludes}},
      executables=executables)