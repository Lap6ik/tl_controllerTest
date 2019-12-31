from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from shiboken2 import wrapInstance 	
import pymel.core as pm

import controllerTest
reload(controllerTest)

class ControllerTestMaya(QtCore.QObject):
    objectSelected = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(ControllerTestMaya, self).__init__(parent) 
        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.emit_selchanged)


    def emit_selchanged(self,_):
        #a = pm.selected(type = 'mesh')
        self.objectSelected.emit(pm.selected(type = 'mesh'))
        print ('Signal Emited From Maya')

window = None
cont = ControllerTestMaya()
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