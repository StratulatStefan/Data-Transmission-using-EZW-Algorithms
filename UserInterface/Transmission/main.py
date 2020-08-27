from transmission_user_interface import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = GraphicalUserInterface(self)
        self.ui.SetActions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # atasam functia de callback a inchiderii ferestrei; se va inchide sigur conexiunea dintre noduri (socket-ul)
    app.aboutToQuit.connect(SafeClose)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
