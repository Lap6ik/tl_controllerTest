from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance 	

def get_maya_window():
    '''Return the QMainWindow for the main maya window'''

    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found\n')
    window = wrapInstance(winptr,QtWidgets.QMainWindow)
    assert isinstance(window, QtWidgets.QMainWindow)
    return window