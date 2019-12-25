from PySide2 import QtCore, QtGui, QtWidgets

import controllerTestUI as ui
reload(ui)

class ControllerTest(QtWidgets.QMainWindow):
    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)
        
        # we define our own signal

if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

