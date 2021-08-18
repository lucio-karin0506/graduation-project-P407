import logging
import PySide2
import sys
import os

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2 import QtGui, QtCore, QtWidgets

logging.getLogger().setLevel(logging.CRITICAL)

"""
    Debug & Processing Log text output
    프로그램 상의 text output을 받는 class
"""
class debug_log(QWidget):
    printOccur = Signal(str, str, name="print")

    def __init__(self, *param):
        QWidget.__init__(self, None)
        self.daemon = True
        self.sysstdout = sys.stdout.write
        self.sysstderr = sys.stderr.write

    def stop(self):
        sys.stdout.write = self.sysstdout
        sys.stderr.write = self.sysstderr

    def start(self):
        sys.stdout.write = self.write
        sys.stderr.write = lambda msg: self.write(msg, color="red")

    def write(self, s, color="black"):
        pass
        sys.stdout.flush()
        self.printOccur.emit(s, color)


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = debug_log()
    mainWin.show()
    sys.exit(app.exec_())