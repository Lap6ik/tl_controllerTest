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

    itemSelectedSignal = QtCore.Signal(list,list)    
    objectSelectedSignal = QtCore.Signal(list)
    windowClosedSignal = QtCore.Signal(str)

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.allItems = []
        self.selectedItems = []
        self.notSelectedItems = []

        self.callBackId = None
        self.shapeNodes = []
        self.currentItemLabel = []        
        self.windowClosed = None

        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)
        
        self.__updateUiItemsList()

        self.ui.shapeNodesListWidget.itemClicked.connect(self._uiItemClicked)
        #self.ui.shapeNodesListWidget.itemClicked.connect(self.__fromUiObjectSelect)
        self.itemSelectedSignal.connect(self.__fromUiObjectSelect)

        #maya callBacks
        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._mayaObjectSelected)
        self.objectSelectedSignal.connect(self._fromMayaItemSelection)
        self.windowClosedSignal.connect(self.__windowWasClosed)
        self.windowClosedSignal.connect(self.close)
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
        #self.__setItemSelection()

    '''
    UI affecting Maya functions
    self.selectedItems - all items selected in the listWidget
    self.notSelectedItems - all items in the listWidget which are not selected
    '''
    #(1.2)signal item clicked is emited with list argument 
    def _uiItemClicked(self):
        self.selectedItems = self.ui.shapeNodesListWidget.selectedItems()
        self.notSelectedItems = [item for item in self.allItems if item not in self.selectedItems]
        print ('self.notSelectedItems %s'%self.notSelectedItems)
        self.itemSelectedSignal.emit(self.selectedItems, self.notSelectedItems)
        ## here we need to assign INDICATOR a value #1

    def __fromUiObjectSelect(self):
        #convert 
        selectedItemsNames = []
        notSelectedItemsNames = []
        allItemsNames = []

        for item in self.selectedItems:
            a = item.text()
            selectedItemsNames.append(a)
        for item in self.notSelectedItems:
            b = item.shortName()
            notSelectedItemsNames.append(b)
        for item in self.allItems:
            c = item.shortName()
            allItemsNames.append(c)

        print ('Items Lists:')
        print ('%s'%selectedItemsNames)
        print ('%s'%notSelectedItemsNames)
        print ('%s'%allItemsNames)

        for item in allItemsNames:
            if item in selectedItemsNames:
                pm.select(item, add = True)
            elif item in notSelectedItemsNames:
                pm.select(item, deselect = True) 
            else:
                print ('Item exists but neither selected nor deselected')
                
    '''
    Maya callbacks affecting UI functions
    self.allObjects - all objects in maya
    self.selectedObjects - all objects selected in maya
    self.notSelectedObjects - all objects not selected in maya
    '''    
    def _mayaObjectSelected(self,_):
        self.objectSelectedSignal.emit(self.allItems)
        self.callBackId = OpenMaya.MEvenckId = OpenMaya.MEventMessage.currentCallbackId()

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

