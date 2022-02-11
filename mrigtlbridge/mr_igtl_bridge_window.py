import os, time, json, sys
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from . import widget_base


# ------------------------------------MAIN WINDOW------------------------------------
class MainWindow(QtWidgets.QWidget):
  
  def __init__(self):
    super(MainWindow, self).__init__()

    self.leftWidget = None
    self.rightWidget = None
    self.title = "MRI OpenIGTLink Bridge"

  def setTitle(self, title):
    self.title = title

  def setLeftWidget(self, widget):
    self.leftWidget = widget
    
  def setRightWidget(self, widget):    
    self.rightWidget = widget

  def setup(self):
    
    self.setWindowTitle(self.title)

    topLayout = QtWidgets.QHBoxLayout()
    self.setLayout(topLayout)

    # --- Left Layout (OpenIGTLink) ---
    leftWidget = QtWidgets.QWidget()
    topLayout.addWidget(leftWidget)
    self.leftWidget.buildGUI(leftWidget)

    # Separator
    vline = QtWidgets.QFrame()
    vline.setFrameShape(QtWidgets.QFrame.VLine)
    vline.setFrameShadow(QtWidgets.QFrame.Sunken)
    topLayout.addWidget(vline)        

    # --- Right Layout (Scanner) ---
    rightWidget = QtWidgets.QWidget()
    topLayout.addWidget(rightWidget)
    self.rightWidget.buildGUI(rightWidget)

  def closeEvent(self, event):
    
    self.leftWidget.closeEvent(event)
    self.rightWidget.closeEvent(event)
    super(MainWindow, self).closeEvent(event)




