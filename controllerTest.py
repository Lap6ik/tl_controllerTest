from PySide2 import QtCore, QtGui, QtWidgets
import pymel.core as pm

import controllerTestUI as ui
reload(ui)

class ControllerTest(QtWidgets.QMainWindow):

    itemClicked = QtCore.Signal(list,list)

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
    
    #(1.2)signal object clicked is emited with list argument 
    def _onItemClicked(self):
        self.selectedItems = self.ui.shapeNodesListWidget.selectedItems()
        self.itemClicked.emit(self.listItems,self.selectedItems)

    def _onSelectionUpdate(self):
        selectedNames = []
        allItems = []

        for item in self.selectedItems:
            selectedName = item.text()
            selectedNames.append(selectedName)
        for item in self.listItems:
            itemName = item.shortName()
            allItems.append(itemName)
        notSelected =[item for item in allItems if item not in selectedNames]
        print ('selected Items: {0}'.format(selectedNames))
        print ('all  Items are: {0}'.format(allItems))
        print ('not  selected : {0}\n'.format(notSelected))

        for item in allItems:
            if item in selectedNames:
                pm.select(item, add = True)
            elif item in notSelected:
                pm.select(item, deselect = True)
            else:
                print ('Error!!! with selection')


if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

