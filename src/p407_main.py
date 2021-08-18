import sys
from GUI.interface.main import MainWindow
from PySide2.QtWidgets import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
