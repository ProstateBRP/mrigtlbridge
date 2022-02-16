from PyQt5 import QtCore, QtGui, QtWidgets
import importlib

class WidgetBase(QtCore.QObject):

  messageBoxSignal = QtCore.pyqtSignal(str)
  
  def __init__(self, *args):
    super().__init__(*args)
    self.signalManager = None
    self.listener = None
    self.listener_class = ['mrigtlbridge.listener_base', 'ListenerBase']

    self.threadActive = False
    self.signalManager = None
    self.listenerParameter = {}

    
  def buildGUI(self, parent):
    pass

  
  def updateGUI(self, state):
    if state == 'Connected':
      pass
    elif state == 'Disconnected':
      pass
    pass

    
  def closeEvent(self, event):
    if self.listener:
      self.listener.stopListener()
      self.listener = None

  
  def setSignalManager(self, sm):
    self.signalManager = sm

    ## Add custom signals for the listener
    #module = importlib.import_module(self.listener_class[0])
    #class_ = getattr(module, self.listener_class[1])
    #listener = class_()
    #signalList = listener.customSignalList
    #for name in signalList.keys():
    #  self.signalManager.addCustomSignal(name, signalList[name])


  def startListener(self):
    print('startListener(self, event)')

    if self.signalManager == None:
      raise Exception("SignalManager is not set!")
      return

    if (not self.listener):
      try:
        module = importlib.import_module(self.listener_class[0])
        class_ = getattr(module, self.listener_class[1])
        self.listener = class_()
        self.listener.connectSlots(self.signalManager)
        print("connected slots ")
        self.listener.configure(self.listenerParameter)
        print("configured ")
        self.listener.start()
        self.updateGUI('Connected')
      except:
        print("Failed to start Listener: ")
        self.listener.stop()
        self.listener = None
    else:
      raise Exception("Already connected! : ")

    
  def stopListener(self):
    
    if (self.listener):
      self.listener.stop()
      self.listener = None
      self.updateGUI('Disconnected')

    else:
      raise Exception("No existing Listener to stop!")
    
