from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from shiboken2 import wrapInstance 	
import pymel.core as pm

import controllerTest
reload(controllerTest)

class ControllerTestMaya(QtCore.QObject):
    objectSelected = QtCore.Signal(list)
    windowClosed = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(ControllerTestMaya, self).__init__(parent) 

        self.callBackId = []

        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.emit_selchanged)
        self.objectSelected.connect(self.printF)

    def emit_selchanged(self,_):
        print ('Signal Emited From Maya')
        self.objectSelected.emit(pm.selected(type = 'mesh'))
    
        self.callBackId = OpenMaya.MEventMessage.currentCallbackId()
        #OpenMaya.MEventMessage.removeCallback(self.callBackId)

    def printF(self):
        print ('here must be a UI changing script\n')
 
window = None
cont = ControllerTestMaya() 
print ('/n   printing callBackID outside maya')           

def show():
    global window
    if window is None:

        parent = get_maya_window()
        window = controllerTest.ControllerTest(parent)       

    window.show()
    
def get_maya_window():
    '''Return the QMainWindow for the main maya window'''

    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found\n')
    window = wrapInstance(winptr,QtWidgets.QMainWindow)
    assert isinstance(window, QtWidgets.QMainWindow)
    return window