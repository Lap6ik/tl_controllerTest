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

        self.selectionCallBackId = None
        self.shapeNodes = []
        self.currentItemLabel = []        
        self.windowClosed = None

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)

        self.__updateUiItemsList()
        self.__updateUiSelection()
        #add callbacks for deleting and adding new node
        self.__createSelectionCallBack()

        self.ui.nodesListWidget.itemClicked.connect(self._uiItemClicked)
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
        self.ui.nodesListWidget.clear()
        self.ui.nodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        meshObjects = pm.ls(dag =True, type = 'mesh')
        #print (meshObjects)
        for obj in meshObjects:
            transformNode = pm.PyNode(obj)
            print (transformNode)
            self.ui.nodesListWidget.addItem(str(transformNode)) 
        
    '''
    UI affecting Maya functions
    self.selectedItems - all items selected in the listWidget
    self.notSelectedItems - all items in the listWidget which are not selected
    '''
    #(1.2)signal item clicked is emited with list argument 
    def _uiItemClicked(self):
        self.__removeSelectionCallBack()
        self.itemSelectedSignal.emit('Items Selected')       

    def __fromUiObjectSelect(self):
        itemsInUi = []
        selectedItems = []
        notSelectedItems = []

        selectedMeshes = pm.ls(selection = True, dag = True, type = 'mesh')
        print (selectedMeshes)

        for index in range(self.ui.nodesListWidget.count()):
             itemsInUi.append(self.ui.nodesListWidget.item(index))

        for item in itemsInUi:
            if item.isSelected():
                selectedItems.append(item)
            else:
                notSelectedItems.append(item)
        
        #this does not work
        for item in selectedItems:
            if item.text in selectedMeshes:
                pass
            else:
                pm.select(item.text(), add = True)
        
        for item in notSelectedItems:
            if item.text in selectedMeshes:
                print ('we are here')
                pm.select(item.text(), deselect = True)
            else:
                pass

        self.objectSelectionFromUIFinished.emit('objectSelectionFromUIFinished')
        
    '''
    Maya callbacks affecting UI functions
    '''    
    def _signalSelectionChanged(self,_):
        self.objectSelectedSignal.emit('Object selected')

    def __updateUiSelection(self):
        itemsInUi = []
        selectedMeshes = pm.ls(selection = True, dag = True, type = 'mesh')
        
        for index in range(self.ui.nodesListWidget.count()):
            itemsInUi.append(self.ui.nodesListWidget.item(index))

        itemsToSelect = [item for item in itemsInUi if item.text() in selectedMeshes]
        itemsToDeselect = [item for item in itemsInUi if item.text() not in selectedMeshes]

        for item in itemsToSelect:
            if self.ui.nodesListWidget.isItemSelected(item):
                pass
            elif not self.ui.nodesListWidget.isItemSelected(item):
                print ('item to select %s'%item)
                item.setSelected(True)
        for item in itemsToDeselect:
            if self.ui.nodesListWidget.isItemSelected(item):
                item.setSelected(False)
            elif not self.ui.nodesListWidget.isItemSelected(item):
                pass
           

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

