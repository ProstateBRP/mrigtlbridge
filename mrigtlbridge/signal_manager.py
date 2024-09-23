import os, time, json, sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

from multiprocessing import Process, Queue, Pipe

from typing import TypeVar, Generic, List
from .common import SignalNames

import logging


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
  signals = {}
    
  def __init__(self, *args):
    super().__init__(*args)
    for name in SignalNames:
      self.addSlot(name, SignalNames[name])

    self.signalManagerProxy = SignalManagerProxy()
    self.signalManagerProxy.setSignalManager(self)
    self.signalManagerProxy.start()

  def getSignalManagerProxy(self):
    return self.signalManagerProxy


  def addSlot(self, name, paramType):
    logging.debug('SignalManager.addSlot(%s, %s)' % (name, paramType))
    if name in self.signals.keys():
      if paramType == self.signals[name].paramType:
        logging.debug('SignalManager.addSlot(): Slot already exists.')
      else:
        logging.debug('SignalManager.addSlot(): The parameter type conflicts with the existing slot')
      return False
      
    if paramType == None:
      self.signals[name] = self.SignalWrap()
    elif paramType == 'str':
      self.signals[name] = self.SignalWrapStr()
    elif paramType == 'dict':
      self.signals[name] = self.SignalWrapDict()
    else:
      logging.debug('SignalManager.addSlot(): Illegal parameter type.')
      return False

    return True


  def addCustomSignal(self, name, paramType):
    return self.addSlot(name, paramType)

    
  def addCustomSlot(self, name, paramType, slot):
    logging.debug('SignalManager.addCustomSlot(%s)' % name)
    if self.addSlot(name, paramType):
      self.connectSlot(name, slot)
      return True
    else:
      return False

    
  def connectSlot(self, name, slot):
    logging.debug('SignalManager.connectSlot(%s)' % name)
    if name in self.signals.keys():
      self.signals[name].signal.connect(slot)
      return True
    else:
      return False

    
  def disconnectSlot(self, name, slot=None):
    logging.debug('SignalManager.disconnectSlot(%s)' % name)
    if name in self.signals.keys():
      if slot:
        self.signals[name].signal.disconnect(slot)
      else:
        self.signals[name].signal.disconnect()
      return True
    else:
      return False
  

  def emitSignal(self, name, param=None):
    logging.debug('SignalManager.emitSignal(%s)' % name)
    if name in self.signals.keys():
      if param == None:
        self.signals[name].signal.emit()
      else:
        self.signals[name].signal.emit(param)
      return True
    else:
      print('Error in emitting signal')
      return False


# SignalManager Proxy for multiprocessing
# Once SignalManagerProxy is set up, other processes can emit signals by sending signal
# to the pipe returned by getSignalPipe().

class SignalManagerProxy(QThread):

    def __init__(self):
      super().__init__()
      self.signalManager = None
      self.pipe_from, self.pipe_to = Pipe()


    def setSignalManager(self, signalManager):
      self.signalManager = signalManager


    def emitSignal(self, name, param=None):
      self.pipe_from.send((name, param))


    def getSignalPipe(self):
      return self.pipe_from


    def run(self):

      counter = 0
      while True:
        try:
          data = self.pipe_to.recv()
        except EOFError:
          break

        if self.signalManager:
          name = data[0]
          param = data[1]
          self.signalManager.emitSignal(name, param)

        QtCore.QThread.msleep(5)

