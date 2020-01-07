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

    itemClickedSignal = QtCore.Signal(list,list)    
    objectSelectedSignal = QtCore.Signal(list)
    windowClosedSignal = QtCore.Signal(str)

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.listItems = []
        self.callBackId = None
        self.shapeNodes = []
        self.currentItemLabel = []        
        self.windowClosed = None

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)
        
        self.__updateUiItemsList()

        self.ui.shapeNodesListWidget.itemClicked.connect(self._uiItemClicked)
        #self.ui.shapeNodesListWidget.itemClicked.connect(self.__fromUiObjectSelection)
        self.itemClickedSignal.connect(self.__fromUiObjectSelection)

        #maya callBacks
        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._mayaObjectSelected)
        self.objectSelectedSignal.connect(self._fromMayaItemSelection)
        self.windowClosedSignal.connect(self.__windowWasClosed)
    '''
    The functiom filles the text filed of the UI with the Objects we have in Maya
    '''
    def __updateUiItemsList(self):
        self.ui.shapeNodesListWidget.clear()
        self.ui.shapeNodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.shapeNodes = pm.ls(exactType = 'mesh')
        for obj in self.shapeNodes:
            self.ui.shapeNodesListWidget.addItem(str(obj))
            self.listItems.append(obj)  
        #self.__setItemSelection()

    '''
    UI affecting Maya functions
    '''
    #(1.2)signal item clicked is emited with list argument 
    def _uiItemClicked(self):
        self.selectedItems = self.ui.shapeNodesListWidget.selectedItems()
        self.itemClickedSignal.emit(self.listItems,self.selectedItems)

    def __fromUiObjectSelection(self):
        selectedNames = []
        allItems = []

        for item in self.selectedItems:
            selectedName = item.text()
            selectedNames.append(selectedName)
        for item in self.listItems:
            itemName = item.shortName()
            allItems.append(itemName)
        notSelected =[item for item in allItems if item not in selectedNames]

        for item in allItems:
            if item in selectedNames:
                pm.select(item, add = True)
            elif item in notSelected:
                pm.select(item, deselect = True)
            else:
                print ('Error!!! with selection')

    '''
    Maya callbacks affecting UI functions
    '''    
    def _mayaObjectSelected(self,_):
        self.objectSelectedSignal.emit(pm.ls(selection = True, exactType = 'transform'))
    
        self.callBackId = OpenMaya.MEventMessage.currentCallbackId()

    def _fromMayaItemSelection(self):
        selectedObjectsShapes = []
        allObjectsShapes = []
        allObjects = pm.ls(exactType='mesh')
        for obj in allObjects:
            allObjShape = obj.shortName(stripNamespace = True)
            allObjectsShapes.append(allObjShape)
            
        selectedObjects = pm.ls(selection = True, exactType = 'transform')
        for obj in selectedObjects:
            objectShape = pm.listRelatives(obj, children = True, shapes = True)         
            b = objectShape[0].shortName(stripNamespace = True)
            selectedObjectsShapes.append(b)

        #print (allObjectsShapes)    
        #print (selectedObjectsShapes)
        
        #compare two lists of selection
        notSelectedObjects = [obj for obj in allObjectsShapes if obj not in selectedObjectsShapes]
        print ('not selected at the moment%s'%notSelectedObjects)

        for obj in selectedObjectsShapes:
            item = self.ui.shapeNodesListWidget.findItems(str(obj),QtCore.Qt.MatchContains)
            print ('selected item found%s'%item)
        


    '''
    If the UI closing we close the 
    '''
    def closeEvent(self, *event):
        #print (self.isVisible())
        self.windowClosed = 'Window Closing'
        self.windowClosedSignal.emit(self.windowClosed)

    def __windowWasClosed(self):
        print (self.windowClosed)
        OpenMaya.MEventMessage.removeCallback(self.callBackId)


if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

