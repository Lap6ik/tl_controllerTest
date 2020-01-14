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
    '''
    lets see if it works here
    '''

    itemSelectedSignal = QtCore.Signal(str)    
    objectSelectedDeselectedSignal = QtCore.Signal(str)
    windowClosedSignal = QtCore.Signal(str)
    objectSelectionFromUIFinished = QtCore.Signal(str)
    nodeAddedRemovedSignal = QtCore.Signal(str)

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.selectionCallBackId = None  
        self.nodeAddCallBackId = None  
        self.nodeRemoveCallBackId = None
        self.windowClosed = None

        self.__buildUi()
    
    def __buildUi(self):
        '''
        Function used to build the UI. All the signal, slot and default state are initialized here
        ''' 
        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)

        self.__updateUiItemsList()
        self.__updateUiSelection()
        self.__createSelectionCallBack()
        self.__createNodeAddRemoceCallBack()

        self.ui.nodesListWidget.itemClicked.connect(self._uiItemClicked)
        self.itemSelectedSignal.connect(self.__fromUiObjectSelect)
        self.objectSelectionFromUIFinished.connect(self.__createSelectionCallBack)
        self.objectSelectedDeselectedSignal.connect(self.__updateUiSelection)
        self.nodeAddedRemovedSignal.connect(self.__updateUiItemsList)

        self.windowClosedSignal.connect(self.__windowWasClosed)
        self.windowClosedSignal.connect(self.close)

    def __createSelectionCallBack(self):
        self.selectionCallBackId = OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.__signalSelectionChanged) 

    def __removeSelectionCallBack(self):
         OpenMaya.MEventMessage.removeCallback(self.selectionCallBackId)

    def __createNodeAddRemoceCallBack(self):
        self.nodeAddCallBackId = OpenMaya.MDGMessage.addNodeAddedCallback(self.__signalNodeAddedRemoved, 'mesh')
        self.nodeRemoveCallBackId = OpenMaya.MDGMessage.addNodeRemovedCallback(self.__signalNodeAddedRemoved, 'mesh')

    def __removeNodeAddRemoveCallBack(self):
        OpenMaya.MDGMessage.removeCallback(self.nodeAddCallBackId)
        OpenMaya.MDGMessage.removeCallback(self.nodeRemoveCallBackId)

    def __signalNodeAddedRemoved(self, *args):
        self.nodeAddedRemovedSignal.emit('Node Added or Removed')
        
    def __updateUiItemsList(self):
        '''
        The function is called when UI is openned and when new mesh node added or removes from Maya Scene
        The functiom filles the ui ListWidget with the mesh objects we have in Maya
        '''
        self.ui.nodesListWidget.clear()
        self.ui.nodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        meshObjects = pm.ls(dag =True, type = 'mesh')
        for obj in meshObjects:
            transformNode = pm.PyNode(obj)
            self.ui.nodesListWidget.addItem(str(transformNode)) 
        
    def _uiItemClicked(self):
        """
        Fuction is called when ui item is clicked
        It removes the 'Selection Changed' callback, we don't want maya callbacks affect the when the ui affecting maya actions ate executed
        It emits signal that the ui selection is changed
        """
        self.__removeSelectionCallBack()
        self.itemSelectedSignal.emit('Selection in the ui changed')       
        
    def __fromUiObjectSelect(self):
        '''
        Functiom is called when ui selection changed signal is emited
        It divides all item names in UI on selected and not selected
        It sets selected in maya items which are selected in the UI
        And sets deselected in maya items which deselected in the UI
        It also emits a signal at the end that the selection/deselection happenned (to bring back the Selection Changed callback)
        '''
        itemsInUi = []
        selectedItems = []
        notSelectedItems = []
        a = None
        b = None
        c = None

        selectedMeshes = pm.ls(selection = True, dag = True, type = 'transform')

        for index in range(self.ui.nodesListWidget.count()):
             itemsInUi.append(self.ui.nodesListWidget.item(index))

        for item in itemsInUi:
            if item.isSelected():
                a = pm.listRelatives(item.text(), parent = True)
                selectedItems.append(a[0])
            else:
                b = pm.listRelatives(item.text(), parent = True)
                notSelectedItems.append(b[0])

        for item in selectedItems:
            if item in selectedMeshes:
                pass
            else:
                print ('we are here')
                pm.select(item, add = True)
        
        for item in notSelectedItems:
            if item in selectedMeshes:
                print ('to deselect%s'%item)

                pm.select(item, deselect = True)
            else:
                pass

        self.objectSelectionFromUIFinished.emit('objectSelectionFromUIFinished')
         
    def __signalSelectionChanged(self,_):
        '''
        Fuction is called when selection in maya is changed
        It emits the signal that something Selected/Deselected in maya
        '''
        self.objectSelectedDeselectedSignal.emit('Object selected')

    def __updateUiSelection(self):
        '''
        Function is called when Selected/Deselected signal is emited
        It divides the list of items in the Ui on those which corresponding objects selected in Maya and not selected in Maya
        items which corresponding objects selected in maya are set to select in UI
        items which corresponding objects not selected in maya are deselected in UI 
        '''
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
                item.setSelected(True)

        for item in itemsToDeselect:
            if self.ui.nodesListWidget.isItemSelected(item):
                item.setSelected(False)
            elif not self.ui.nodesListWidget.isItemSelected(item):
                pass
           
    def closeEvent(self, *event):
        '''
        The function emits signal that the Ui window closing
        '''
        #print (self.isVisible())
        self.windowClosed = 'Window Closing'
        self.windowClosedSignal.emit(self.windowClosed)

    def __windowWasClosed(self):
        '''
        The function is called when the Ui window closing signal is emited
        It removes the Selection Changed callback
        and removes the Node Added and Node Removed callbacks
        '''
        print (self.windowClosed)
        self.__removeSelectionCallBack()
        self.__removeNodeAddRemoveCallBack()

if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    app.exec_()

