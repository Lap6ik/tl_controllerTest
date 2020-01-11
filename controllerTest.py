from PySide2 import QtCore, QtGui, QtWidgets
import pymel.core as pm
import time
import maya.OpenMaya as OpenMaya

import controllerTestUI as ui
reload(ui)

def doOpenUI(delete=False):
    '''
    Function used to call the instansantation of the tool avoiding 
    the duplicate of leaving extra class behind
    ''' 
    dial = None
    for qt in QtWidgets.QApplication.topLevelWidgets():
        if qt.__class__.__name__== 'ControllerTest':
            dial = qt
            print (dial)

        if not dial:
            dial = ControllerTest()
            return dial 
        else:
            dial.close()
            dial = ControllerTest()
            return dial

class ControllerTest(QtWidgets.QMainWindow):

    itemSelectedSignal = QtCore.Signal(str)    
    objectSelectedSignal = QtCore.Signal(str)
    windowClosedSignal = QtCore.Signal(str)
    objectSelectionFromUIFinished = QtCore.Signal(str)

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.allItems = []
        self.selectedItems = []
        self.notSelectedItems = []

        self.selectionCallBackId = None
        self.shapeNodes = []
        self.currentItemLabel = []        
        self.windowClosed = None

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)

        self.__updateUiItemsList()
        #add functions for selecting items of the UI based on maya
        #add callbacks for deleting and adding new node
        self.__createSelectionCallBack()

        self.ui.shapeNodesListWidget.itemClicked.connect(self._uiItemClicked)
        self.itemSelectedSignal.connect(self.__fromUiObjectSelect)
        self.objectSelectionFromUIFinished.connect(self.__createSelectionCallBack)
        self.objectSelectedSignal.connect(self.__updateUiSelection)

        self.windowClosedSignal.connect(self.__windowWasClosed)
        self.windowClosedSignal.connect(self.close)

    def __createSelectionCallBack(self):
        self.selectionCallBackId = OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._signalSelectionChanged) 

    def __removeSelectionCallBack(self):
         OpenMaya.MEventMessage.removeCallback(self.selectionCallBackId)
    '''
    The functiom filles the text filed of the UI with the Objects we have in Maya
    self.allItems - is the all items added to the listWidget
    '''
    def __updateUiItemsList(self):
        self.ui.shapeNodesListWidget.clear()
        self.ui.shapeNodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.shapeNodes = pm.ls(exactType = 'mesh')
        for obj in self.shapeNodes:
            self.ui.shapeNodesListWidget.addItem(str(obj))
            self.allItems.append(obj)  
        
    '''
    UI affecting Maya functions
    self.selectedItems - all items selected in the listWidget
    self.notSelectedItems - all items in the listWidget which are not selected
    '''
    #(1.2)signal item clicked is emited with list argument 
    def _uiItemClicked(self):
        self.__removeSelectionCallBack()
        listSelectedItems = self.ui.shapeNodesListWidget.selectedItems()
        self.selectedItems = []
        for item in listSelectedItems:
            selectedItem = item.text()
            self.selectedItems.append(selectedItem)
        print ('self.allItems %s'%self.allItems)
        print ('self.selectedItems %s'%self.selectedItems)
        self.notSelectedItems = [item for item in self.allItems if item not in self.selectedItems]
        print ('self.notSelectedItems %s\n'%self.notSelectedItems)
        self.itemSelectedSignal.emit('Items Selected')

    def __fromUiObjectSelect(self):
        for item in self.allItems:

            if item in self.selectedItems:
                pm.select(item, add = True)
            elif item in self.notSelectedItems:
                pm.select(item, deselect = True) 
            else:
                print ('Item exists but neither selected nor deselected') 

        self.objectSelectionFromUIFinished.emit('objectSelectionFromUIFinished')
        
    '''
    Maya callbacks affecting UI functions
    self.allObjects - all objects in maya
    self.selectedObjects - all objects selected in maya
    self.notSelectedObjects - all objects not selected in maya
    '''    
    def _signalSelectionChanged(self,_):
        self.objectSelectedSignal.emit('Object selected')
        print ('selection in Maya changed')

    def __updateUiSelection(self):
        
    '''
    If the UI closing we remove the callback
    '''
    def closeEvent(self, *event):
        #print (self.isVisible())
        self.windowClosed = 'Window Closing'
        self.windowClosedSignal.emit(self.windowClosed)

    def __windowWasClosed(self):
        print (self.windowClosed)
        self.__removeSelectionCallBack()


if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

