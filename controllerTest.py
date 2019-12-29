from PySide2 import QtCore, QtGui, QtWidgets
import pymel.core as pm

import controllerTestUI as ui
reload(ui)

class ControllerTest(QtWidgets.QMainWindow):

    itemClicked = QtCore.Signal(list)

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.shapeNodes = []
        self.currentItemLabel = []
        self.listItems = []

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)
        
        self.__updateShapeNodesListWidget()

        # (1.1)we define our own signal
        self.ui.shapeNodesListWidget.itemClicked.connect(self._onItemClicked)
        self.ui.shapeNodesListWidget.itemClicked.connect(self._onSelectionUpdate)

    def __updateShapeNodesListWidget(self):
        self.ui.shapeNodesListWidget.clear()
        self.ui.shapeNodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.shapeNodes = pm.ls(exactType = 'mesh')
        for obj in self.shapeNodes:
            self.ui.shapeNodesListWidget.addItem(str(obj))
            self.listItems.append(obj)
            
    
    #(1.2)signal object clicked is emited with list argument = 
    def _onItemClicked(self):
        self.selectedItems = self.ui.shapeNodesListWidget.selectedItems()
        self.itemClicked.emit(self.selectedItems)
       # print (selectedItemsNames)


    def _onSelectionUpdate(self):
        mayaSelectedObjects = pm.ls(selection = True)
        for item in self.selectedItems:
            print (item.text())
            if item.text() in mayaSelectedObjects:
                pass
            elif item.text() not in mayaSelectedObjects:
                pm.select(item.text(), add = True)
        notSelectedItems =             
            
if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

