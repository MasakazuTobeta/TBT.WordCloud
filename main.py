## coding: UTF-8
import sys
import argparse
import pathlib
from distutils.util import strtobool
from PyQt5.QtWidgets import QApplication

from gui import MainWindow

#--------------
# Parse args
#--------------
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hoge' , type=pathlib.Path, default=None)
    parser.add_argument('--fuga' , type=strtobool   , default=None)
    args = parser.parse_args()
    return args

#--------------
# Main
#--------------
if __name__ == "__main__":
    args     = parse_args()
    app      = QApplication(sys.argv)
    main_gui = MainWindow(app)
    main_gui.show()
    app.exec_()
    sys.exit()