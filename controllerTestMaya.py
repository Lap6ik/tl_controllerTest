import controllerTest as cT
window = None
def show():
    global window
    if window is None:
        window = cT.ControllerTest()

    window.show()
         