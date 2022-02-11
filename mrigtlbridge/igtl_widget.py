from PyQt5 import QtCore, QtGui, QtWidgets

from . import igtl_listener

class IGTLWidget():

  def __init__(self, label="WidgetBase"):

    self.label = label
    self.openIGTLinkThread = None

  def buildGUI(self, parent):
    
    # --- OpenIGTLink Layout ---
    layout = QtWidgets.QGridLayout()
    parent.setLayout(layout)

    self.openIGTConnectButton = QtWidgets.QPushButton("Connect to OpenIGTLink Server")
    self.openIGTConnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.openIGTConnectButton, 0, 0, 1, 3)
    self.openIGTConnectButton.setEnabled(True)
    self.openIGTConnectButton.clicked.connect(self.connectOpenIGT)
    self.openIGTDisconnectButton = QtWidgets.QPushButton("Disconnect from OpenIGTLink Server")
    self.openIGTDisconnectButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addWidget(self.openIGTDisconnectButton, 0, 3, 1, 3)
    self.openIGTDisconnectButton.setEnabled(False)
    self.openIGTDisconnectButton.clicked.connect(self.disconnectOpenIGT)

    self.openIGT_IpEdit = QtWidgets.QLineEdit("127.0.0.1")
    layout.addWidget(self.openIGT_IpEdit, 1, 0, 1, 4)

    self.openIGT_PortEdit = QtWidgets.QLineEdit("18944")
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
      
  def closeEvent(self, event):
    if self.openIGTLinkThread:
      self.openIGTLinkThread.stop()
      self.openIGTLinkThread = None

  def connectOpenIGT(self):
    if (not self.openIGTLinkThread):
      try:
        self.openIGTLinkThread = igtl_listener.OpenIGTLinkListener()

        # Signal connections
        self.openIGTLinkThread.textBoxSignal.connect(self.updateOpenIGTBox)
        self.openIGTLinkThread.connect(self.openIGT_IpEdit.text(), self.openIGT_PortEdit.text())
        self.openIGTLinkThread.start()

        self.openIGTConnectButton.setEnabled(False)
        self.openIGTDisconnectButton.setEnabled(True)
        self.openIGT_IpEdit.setEnabled(False)
        self.openIGT_PortEdit.setEnabled(False)
      except:
        print("Failed to connect to OpenIGT server!")
        self.openIGTLinkThread.stop()
        self.openIGTLinkThread = None
    else:
      raise Exception("Already connected!")

    
  def disconnectOpenIGT(self):
    if (self.openIGTLinkThread):
      self.openIGTLinkThread.stop()
      self.openIGTLinkThread = None

      self.openIGTConnectButton.setEnabled(True)
      self.openIGTDisconnectButton.setEnabled(False)
      self.openIGT_IpEdit.setEnabled(True)
      self.openIGT_PortEdit.setEnabled(True)
    else:
      raise Exception("No existing OpenIGTLink connection to disconnect from!")

  def updateOpenIGTBox(self, text):
    self.openIGT_textBox.append(text)    



