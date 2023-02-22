from PyQt5 import QtCore, QtGui, QtWidgets

from .widget_base import WidgetBase
from . import mrsim_listener

class MRSIMWidget(WidgetBase):

  def __init__(self, *args):
    super().__init__(*args)
    self.listener_class = ['mrigtlbridge.mrsim_listener', 'MRSIMListener']
    
    self.listenerParameter['imageListFile']    = ''

  def buildGUI(self, parent):
    
    layout = QtWidgets.QGridLayout()
    parent.setLayout(layout)

    self.MRSIMConnectButton = QtWidgets.QPushButton("Connect to MRSIM")
    self.MRSIMConnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.MRSIMConnectButton, 0, 0, 1, 3)
    self.MRSIMConnectButton.setEnabled(True)
    self.MRSIMConnectButton.clicked.connect(self.startListener)
    self.MRSIMDisconnectButton = QtWidgets.QPushButton("Disconnect from MRSIM")
    self.MRSIMDisconnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.MRSIMDisconnectButton, 0, 3, 1, 3)
    self.MRSIMDisconnectButton.setEnabled(False)
    self.MRSIMDisconnectButton.clicked.connect(self.stopListener)

    hline3 = QtWidgets.QFrame()
    hline3.setFrameShape(QtWidgets.QFrame.HLine)
    hline3.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(hline3, 5, 0, 1, 6)

    fileBoxLayout = QtWidgets.QHBoxLayout()
    fileLabel = QtWidgets.QLabel('Image List:')
    self.fileLineEdit = QtWidgets.QLineEdit()
    self.fileDialogBoxButton = QtWidgets.QPushButton()
    self.fileDialogBoxButton.setCheckable(False)
    self.fileDialogBoxButton.text = '...'
    self.fileDialogBoxButton.setToolTip("Open file dialog box.")
    fileBoxLayout.addWidget(fileLabel)
    fileBoxLayout.addWidget(self.fileLineEdit)
    fileBoxLayout.addWidget(self.fileDialogBoxButton)
    layout.addLayout(fileBoxLayout, 6,0,1,6)

    hline4 = QtWidgets.QFrame()
    hline4.setFrameShape(QtWidgets.QFrame.HLine)
    hline4.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(hline4, 7, 0, 1, 6)

    self.MRSIM_textBox = QtWidgets.QTextEdit()
    self.MRSIM_textBox.setReadOnly(True)
    self.MRSIM_textBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    layout.addWidget(self.MRSIM_textBox, 8, 0, 6, 6)

    self.fileDialogBoxButton.clicked.connect(self.openDialogBox)

    
  def connectSlot(self, event):
    super(MRSIMWidget, self).connectSlot(event)

    
  def setSignalManager(self, sm):
    super().setSignalManager(sm)
    self.signalManager.connectSlot('consoleTextMR', self.updateConsoleText)
    self.signalManager.connectSlot('hostDisconnected', self.onHostDisconnected) # former disconnectMRSIM()
    self.signalManager.connectSlot('hostConnected', self.onHostConnected)
    
  def updateConsoleText(self, text):
    self.MRSIM_textBox.append(text)

  def onHostConnected(self):
    self.MRSIMConnectButton.setEnabled(False)
    self.MRSIMDisconnectButton.setEnabled(True)

  def onHostDisconnected(self):
    self.MRSIMConnectButton.setEnabled(True)
    self.MRSIMDisconnectButton.setEnabled(False)
    

  def openDialogBox(self):
    dlg = QtWidgets.QFileDialog()
    dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
    dlg.setNameFilter("List files (*.json)")
    dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

    if dlg.exec_():
      filename = dlg.selectedFiles()[0]
      print(filename)

      self.fileLineEdit.text = filename
      self.listenerParameter['imageListFile'] = filename
