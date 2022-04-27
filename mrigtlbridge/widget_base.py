from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import importlib
import time

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

    
  def __del__(self):
    if self.listener:
      self.listener.terminate()
      
      
  def buildGUI(self, parent):
    pass

  
  def updateGUI(self, state):
    if state == 'listenerConnected':
      pass
    elif state == 'listenerDisconnected':
      pass
    pass

    
  def setSignalManager(self, sm):
    self.signalManager = sm
    self.signalManager.connectSlot('listenerConnected', self.onListenerConnected)
    self.signalManager.connectSlot('listenerDisconnected', self.onListenerDisconnected)
    self.signalManager.connectSlot('listenerTerminated', self.onListenerTerminated)

    # Add custom signals for the listener
    module = importlib.import_module(self.listener_class[0])
    class_ = getattr(module, self.listener_class[1])
    listener = class_()
    signalList = listener.customSignalList
    for name in signalList.keys():
      self.signalManager.addCustomSignal(name, signalList[name])


  def startListener(self):
    if self.signalManager == None:
      raise Exception("SignalManager is not set!")

    if (not self.listener):
      try:
        module = importlib.import_module(self.listener_class[0])
        class_ = getattr(module, self.listener_class[1])
        self.listener = class_()
        self.listener.connectSlots(self.signalManager)
        self.listener.configure(self.listenerParameter)
        self.listener.start()
        # At this point, it is not clear if the connection is succsssful.
        #self.updateGUI('listenerConnected')
      except:
        print("Failed to start Listener: ")
        self.listener.stop()
        del self.listner
        self.listener = None
        return
    else:
      dlg = QMessageBox()
      dlg.setWindowTitle("Warning")
      dlg.setText("A listener is already running. Kill it?")
      dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      dlg.setIcon(QMessageBox.Question)
      button = dlg.exec()
      
      if button == QMessageBox.Yes:
        # TODO: Should we call terminate() instead?
        self.listener.terminate()
        del self.listener
        self.listener = None
      else:
        # Do nothing. Keep the existing listener.
        pass
      return
    
    
  def stopListener(self):
    
    if (self.listener):
      self.listener.stop()
      del self.listener
      self.listener = None
      self.updateGUI('Disconnected')

    else:
      raise Exception("No existing Listener to stop!")


  def onListenerConnected(self, className):

    module = importlib.import_module(self.listener_class[0])
    class_ = getattr(module, self.listener_class[1])
    if self.listener and class_.__name__ == className:
      self.updateGUI('listenerConnected')
  
  def onListenerDisconnected(self, className):

    module = importlib.import_module(self.listener_class[0])    
    class_ = getattr(module, self.listener_class[1])
    if class_.__name__ == className:
      del self.listener
      self.listener = None
      self.updateGUI('listenerDisconnected')
    
  def onListenerTerminated(self, className):
    module = importlib.import_module(self.listener_class[0])    
    class_ = getattr(module, self.listener_class[1])
    if class_.__name__ == className:
      self.listener = None
      self.updateGUI('listenerDisconnected')
      
