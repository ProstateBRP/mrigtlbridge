from PyQt5 import QtCore, QtGui, QtWidgets

from .widget_base import WidgetBase
from . import mrsim_listener

class MRSIMWidget(WidgetBase):

  def __init__(self, *args):
    super().__init__(*args)
    self.listener_class = ['mrigtlbridge.mrsim_listener', 'MRSIMListener']

  def buildGUI(self, parent):
    
    layout = QtWidgets.QGridLayout()
    parent.setLayout(layout)

    self.MRSIMConnectButton = QtWidgets.QPushButton("Connect to MRSIM")
    self.MRSIMConnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.MRSIMConnectButton, 0, 0, 1, 3)
    self.MRSIMConnectButton.setEnabled(True)
    self.MRSIMConnectButton.clicked.connect(self.connectSlot)
    #self.MRSIMConnectButton.clicked.connect(self.connectMRSIM)
    self.MRSIMDisconnectButton = QtWidgets.QPushButton("Disconnect from MRSIM")
    self.MRSIMDisconnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.MRSIMDisconnectButton, 0, 3, 1, 3)
    self.MRSIMDisconnectButton.setEnabled(False)
    #self.MRSIMDisconnectButton.clicked.connect(self.disconnectMRSIM)

    hline3 = QtWidgets.QFrame()
    hline3.setFrameShape(QtWidgets.QFrame.HLine)
    hline3.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(hline3, 7, 0, 1, 6)    

    self.MRSIM_textBox = QtWidgets.QTextEdit()
    self.MRSIM_textBox.setReadOnly(True)
    self.MRSIM_textBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    layout.addWidget(self.MRSIM_textBox, 8, 0, 6, 6)

    
  def connectSlot(self, event):
    super(MRSIMWidget, self).connectSlot(event)

    
  def closeEvent(self, event):
    pass
    
  def setSignalManager(self, sm):
    super().setSignalManager(sm)
    self.signalManager.connectSlot('consoleTextMR', self.updateConsoleText)
    
  def updateConsoleText(self, text):
    self.MRSIM_textBox.append(text)
