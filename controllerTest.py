from PySide2 import QtCore, QtGui, QtWidgets
import os, sys
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
    The Class
    '''
    changeMayaSelSig = QtCore.Signal(str)
    changeUiSelSig = QtCore.Signal(str)
    closeWindowSig = QtCore.Signal(str)
    refillUiSig = QtCore.Signal(str)    

    def __init__(self, parent = None):    
        super(ControllerTest, self).__init__(parent) 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.selectionCallBackId = None  
        self.nodeAddCallBackId = None  
        self.nodeRemoveCallBackId = None

        self.__buildUi()
    
    def __buildUi(self):
        '''
        Function used to build the UI. All the signal, slot and default state are initialized here
        ''' 
        self.ui = ui.ControllerTestUI()
        self.ui.create_window(self)
        
        #the methods at the UI openning
        self.__fillTheUi()
        self.__changeUiSel() 
        self.__createMayaSelChangedCallBack()
        self.__createMayaNodeChangedCallBacks()

        #event loop signals
        self.ui.nodesListWidget.itemSelectionChanged.connect(self._emitChangeMayaSelSig)

        self.changeMayaSelSig.connect(self.__changeMayaSel)
        self.changeUiSelSig.connect(self.__changeUiSel)       
        self.refillUiSig.connect(self.__fillTheUi)
        self.closeWindowSig.connect(self.__windowWasClosed)


    def _emitChangeMayaSelSig(self):
        self.changeMayaSelSig.emit('Selection in UI changed')

    def __createMayaSelChangedCallBack(self):
        self.selectionCallBackId = OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.__emitMayaSelChangedSig) 

    def __emitMayaSelChangedSig(self,_):
        self.changeUiSelSig.emit('Selection in Maya changed')

    def __removeMayaSelChangedCallBack(self):
         OpenMaya.MEventMessage.removeCallback(self.selectionCallBackId)

    def __createMayaNodeChangedCallBacks(self):
        self.nodeAddCallBackId = OpenMaya.MDGMessage.addNodeAddedCallback(self.__emitRefillUiSig, 'mesh')
        self.nodeRemoveCallBackId = OpenMaya.MDGMessage.addNodeRemovedCallback(self.__emitRefillUiSig, 'mesh')

    def __emitRefillUiSig(self, *args):
        self.refillUiSig.emit('Node Added or Removed')

    def __removeMayaNodeChangedCallBacks(self):
        OpenMaya.MDGMessage.removeCallback(self.nodeAddCallBackId)
        OpenMaya.MDGMessage.removeCallback(self.nodeRemoveCallBackId)

    def closeEvent(self, *event):   
        #print (self.isVisible())
        self.closeWindowSig.emit('Window Closing')

        
    def __fillTheUi(self):
        '''
        The method evoked by Maya event, by adding or removing 'mesh' node in Maya
        The only signal of ListWidget('itemSelectionChanged') is blocked to avoid evoking changes back in Maya
        The method filles the UI ListWidget with mesh objects from Maya
        'itemSelectionChanged' signal is unblocked back in the end
        '''
        self.ui.nodesListWidget.blockSignals(True)

        self.ui.nodesListWidget.clear()
        self.ui.nodesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        meshObjects = pm.ls(dag =True, type = 'mesh')
        for obj in meshObjects:
            transformNode = pm.PyNode(obj)
            self.ui.nodesListWidget.addItem(str(transformNode)) 
        self.ui.nodesListWidget.blockSignals(False)   
        
    def __changeMayaSel(self):
        '''
        The method evoked by ui event, by change of selection of items in ListWidget
        'SelectionChanged' Maya callback is removed to avoid evoking changes back in the ui
        The method selects objects in Maya according to recent selection made in ListWidget
        'SelectionChanged' Maya callback added back in the end 
        '''
        self.__removeMayaSelChangedCallBack()

        #print ('Maya selection set to update')

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
                pm.select(item, add = True)
        
        for item in notSelectedItems:
            if item in selectedMeshes:

                pm.select(item, deselect = True)
            else:
                pass

        self.__createMayaSelChangedCallBack()
        
    def __changeUiSel(self):
        '''
        Method evoked by Maya events, by change of selection in Maya, by adding or removing 'mesh' object in Maya
        The only signal of ListWidget('itemSelectionChanged') is blocked to avoid evoking changes back in Maya
        The method selects items in the UI according to recent selection made in Maya
        'itemSelectionChanged' signal is unblocked back in the end
        '''
        self.ui.nodesListWidget.blockSignals(True)

        #print ('UI selection set to update')

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
        
        self.ui.nodesListWidget.blockSignals(False)
           

    def __windowWasClosed(self):
        '''
        The function is called when the Ui window closing signal is emited
        It removes the Selection Changed callback
        and removes the Node Added and Node Removed callbacks
        '''
        self.__removeMayaSelChangedCallBack()
        self.__removeMayaNodeChangedCallBacks()
        self.close()


if __name__ == '__main__':
    
    app = QtWidgets.QApplication([])  
    win = ControllerTest()   
    win.show()
    sys.exit(app.exec_())
