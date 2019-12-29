from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as OpenMayaUI
from shiboken2 import wrapInstance 	

import controllerTest
reload(controllerTest)

window = None
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