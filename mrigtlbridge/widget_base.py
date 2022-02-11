from PyQt5 import QtCore, QtGui, QtWidgets

class WidgetBase():

  def __init__(self, label="WidgetBase"):

    self.label = label
    self.catheters = None     #CatheterCollection
    self.currentCatheter = None

  def buildGUI(self, parent):
    pass
    
  def closeEvent(self, event):      
    pass


