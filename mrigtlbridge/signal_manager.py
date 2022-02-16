import os, time, json, sys
from PyQt5 import QtCore, QtGui, QtWidgets


from typing import TypeVar, Generic, List

class SignalManager(QtCore.QObject):

  # Since PyQt does not allow making an array or a dictionary of pyqtSignal(),
  # we create a wrapper class. See:
  # https://stackoverflow.com/questions/38506979/creating-an-array-of-pyqtsignal
  
  class SignalWrap(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    paramType = None

  class SignalWrapStr(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    paramType = 'str'
    
  class SignalWrapDict(QtCore.QObject):
    signal = QtCore.pyqtSignal(dict)
    paramType = 'dict'

    
  # List of signal names and type of arguments for the slot functions.
  signalNames = {
    # For IGTL GUI
    'consoleTextIGTL' : 'str',
    # For IGTL Listener
    'disconnectIGTL' : None,
    # For MR GUI
    'consoleTextMR' : None,
    # For MR Listener
    'startSequence' : None,
    'stopSequence' : None,
    'updateScanPlane' : None
  }
  
  signals = {}
    
  def __init__(self, *args):
    super().__init__(*args)
    for name in self.signalNames:
      self.addSlot(name, self.signalNames[name])

  def addSlot(self, name, paramType):
    print('SignalManager.addSlot(%s, %s)' % (name, paramType))
    if name in self.signals.keys():
      if paramType == self.signals[name].paramType:
        print('SignalManager.addSlot(): Slot already exists.')
      else:
        print('SignalManager.addSlot(): The parameter type conflicts with the existing slot')
      return False
      
    if paramType == None:
      self.signals[name] = self.SignalWrap()
    elif paramType == 'str':
      self.signals[name] = self.SignalWrapStr()
    elif paramType == 'dict':
      self.signals[name] = self.SignalWrapDict()
    else:
      print('SignalManager.addSlot(): Illegal parameter type.')
      return False

    return True


  def addCustomSlot(self, name, paramType, slot):
    print('addCustomSlots()')
    if self.addSlot(name, paramType):
      self.connectSlot(name, slot)
      return True
    else:
      return False

    
  def connectSlot(self, name, slot):
    if name in self.signals.keys():
      print('Connecting slot: ' + name)
      self.signals[name].signal.connect(slot)
  

  def emitSignal(self, name, param=None):
    print('emitSignal: %s' % name)
    if name in self.signals.keys():
      print('SignalManger.emitSignal(): key found')
      self.signals[name].signal.emit(param)
      return True
    else:
      print('SignalManger.emitSigal(): Invalid signal name')
      return False
