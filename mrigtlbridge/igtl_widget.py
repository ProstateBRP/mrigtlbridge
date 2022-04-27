from PyQt5 import QtCore, QtGui, QtWidgets

from .widget_base  import WidgetBase
from .igtl_listener import IGTLListener

class IGTLWidget(WidgetBase):

  def __init__(self, *args):
    super().__init__(*args)
    self.listener_class = ['mrigtlbridge.igtl_listener', 'IGTLListener']

    self.listenerParameter['ip'] = '127.0.0.1'
    self.listenerParameter['port'] = 18944

  def buildGUI(self, parent):
    
    # --- OpenIGTLink Layout ---
    layout = QtWidgets.QGridLayout()
    parent.setLayout(layout)

    self.openIGTConnectButton = QtWidgets.QPushButton("Connect to OpenIGTLink Server")
    self.openIGTConnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.openIGTConnectButton, 0, 0, 1, 3)
    self.openIGTConnectButton.setEnabled(True)
    self.openIGTConnectButton.clicked.connect(self.startListener)
    self.openIGTDisconnectButton = QtWidgets.QPushButton("Disconnect from OpenIGTLink Server")
    self.openIGTDisconnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.openIGTDisconnectButton, 0, 3, 1, 3)
    self.openIGTDisconnectButton.setEnabled(False)
    self.openIGTDisconnectButton.clicked.connect(self.stopListener)

    self.openIGT_IpEdit = QtWidgets.QLineEdit(self.listenerParameter['ip'])
    #self.openIGT_IpEdit.textChanged[str].connect(self.onIPChanged)
    self.openIGT_IpEdit.textChanged.connect(self.onSocketParamChanged)

    layout.addWidget(self.openIGT_IpEdit, 1, 0, 1, 4)

    self.openIGT_PortEdit = QtWidgets.QLineEdit(str(self.listenerParameter['port']))
    #self.openIGT_PortEdit.textChanged[str].connect(self.onPortChanged)
    self.openIGT_PortEdit.textChanged.connect(self.onSocketParamChanged)
    layout.addWidget(self.openIGT_PortEdit, 1, 4, 1, 2)
    
    hline1 = QtWidgets.QFrame()
    hline1.setFrameShape(QtWidgets.QFrame.HLine)
    hline1.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(hline1, 2, 0, 1, 6)

    hline2 = QtWidgets.QFrame()
    hline2.setFrameShape(QtWidgets.QFrame.HLine)
    hline2.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(hline2, 4, 0, 1, 6)        

    self.openIGT_textBox = QtWidgets.QTextEdit()
    self.openIGT_textBox.setReadOnly(True)
    self.openIGT_textBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    layout.addWidget(self.openIGT_textBox, 5, 0, 6, 6)

    spacer = QtWidgets.QSpacerItem(1, 14, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    layout.addItem(spacer, 14, 0)


  def setSignalManager(self, sm):
    super().setSignalManager(sm)
    self.signalManager.connectSlot('consoleTextIGTL', self.updateConsoleText)
    
      
  def onSocketParamChanged(self):
    self.listenerParameter['ip'] = str(self.openIGT_IpEdit.text())
    self.listenerParameter['port'] = int(self.openIGT_PortEdit.text())

    
  def updateGUI(self, state):
    if state == 'listenerConnected':
      self.openIGTConnectButton.setEnabled(False)
      self.openIGTDisconnectButton.setEnabled(True)
      self.openIGT_IpEdit.setEnabled(False)
      self.openIGT_PortEdit.setEnabled(False)
      #self.listener.textBoxSignal.connect(self.updateIGTLBox)
    elif state == 'listenerDisconnected':
      self.openIGTConnectButton.setEnabled(True)
      self.openIGTDisconnectButton.setEnabled(False)
      self.openIGT_IpEdit.setEnabled(True)
      self.openIGT_PortEdit.setEnabled(True)
    pass


  def updateConsoleText(self, text):
    self.openIGT_textBox.append(text)



