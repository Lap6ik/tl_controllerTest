from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from shiboken2 import wrapInstance 	
import pymel.core as pm

import controllerTest
reload(controllerTest)

class ControllerTestMaya(QtCore.QObject):
    objectSelected = QtCore.Signal(list)

window = None
def show():
    global window
    if window is None:
        cont = ControllerTestMaya()
        parent = get_maya_window()
        window = controllerTest.ControllerTest(parent)

        def emit_selchanged(_):
            cont.objectSelected.emit(pm.selected(type = 'mesh'))
            print ('Signal Emited From Maya')
        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', emit_selchanged)
    window.show()

def get_maya_window():
    '''Return the QMainWindow for the main maya window'''

    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found\n')
    window = wrapInstance(winptr,QtWidgets.QMainWindow)
    assert isinstance(window, QtWidgets.QMainWindow)
    return window