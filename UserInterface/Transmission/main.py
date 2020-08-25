import sys
from transmission_user_interface import *
from communication.general_use import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = GraphicalUserInterface(self)
        self.ui.SetActions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # atasam functia de inchidere sigura a conexiunii (socket-ului)
    app.aboutToQuit.connect(SafeClose)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
