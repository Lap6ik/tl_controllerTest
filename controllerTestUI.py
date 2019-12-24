from PySide2 import QtCore, QtGui, QtWidgets

class ControllerTest(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        
        super(ControllerTest, self).__init__(parent) 
        self.__create_window()   
        
    def __create_window(self):
        self.mainWindow = self # Main Window
        self.centralWidget1 = QtWidgets.QWidget(self.mainWindow) #central widget1
        self.widget1 = QtWidgets.QWidget(self.centralWidget1) #widget1
        self.shapeNodesComboBox = QtWidgets.QComboBox(self.widget1) #comboBox
        self.label1 = QtWidgets.QLabel(self.widget1)
        self.label1.setText('Object')

        #creating layout for Central Widget and placing widget_1 there
        self.verticalLayout1 = QtWidgets.QVBoxLayout(self.centralWidget1)
        self.centralWidget1.setLayout(self.verticalLayout1)
        self.verticalLayout1.addWidget(self.widget1)
    
        #creating layout for widget_1 and placing label and ComboBox there
        self.horizontalLayout1 = QtWidgets.QHBoxLayout(self.widget1)
        self.widget1.setLayout(self.horizontalLayout1)
        self.horizontalLayout1.addWidget(self.label1)
        self.horizontalLayout1.addWidget(self.shapeNodesComboBox)

        #set central widget for mainWindow
        self.mainWindow.setCentralWidget(self.centralWidget1)

if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

