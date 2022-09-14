import os, time, json, sys
import numpy as np
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from .listener_base import ListenerBase

# ------------------------------------MR------------------------------------
class MRSIMListener(ListenerBase):

  def __init__(self, *args):
    super().__init__(*args)

    self.customSignalList = {
      'hostConnected' : None,
      'hostDisconnected' : None,
      'sequenceStarted' : None
    }

    self.threadActive = False
    self.jobQueue = False
    self.counter = 0
    self.streaming = False

  def connectSlots(self, signalManager):
    super().connectSlots(signalManager)
    print('MRSIMListener.connectSlots()')
    self.signalManager.connectSlot('startSequence', self.startSequence)
    self.signalManager.connectSlot('stopSequence', self.stopSequence)
    self.signalManager.connectSlot('updateScanPlane', self.updateScanPlane)

  def disconnectSlots(self):
    
    super().disconnectSlots()
    
    print('MRSIMListener.disconnectSlots()')
    if self.signalManager:
      self.signalManager.disconnectSlot('startSequence', self.startSequence)
      self.signalManager.disconnectSlot('stopSequence', self.stopSequence)
      self.signalManager.disconnectSlot('updateScanPlane', self.updateScanPlane)

  def initialize(self):
    
    print('MRSIMListener: initializing...')
    ret = self.connect()

    if ret:
      print("MRSIMListener: Connected.")
      time.sleep(0.5)
      self.signalManager.emitSignal('hostConnected')
      return True
    else:
      print("MRSIMListener: Connection failed.")
      return False


  def process(self):
    #self.startSequence()
    QtCore.QThread.msleep(50) # TODO: This may give SRC more time to process images 

    
  def finalize(self):
    self.disconnect()
    self.signalManager.emitSignal('hostDisconnected')
    super().finalize()

    
  def connect(self):

    self.signalManager.emitSignal('consoleTextMR', 'MRSIMListener connected.')
    self.signalManager.emitSignal('hostConnected')
    return True

  
  def disconnect(self):
    self.signalManager.emitSignal('consoleTextMR', 'MRSIMListener disconnected')
    self.signalManager.emitSignal('hostDisconnected')

    
  def startSequence(self):
    print('startSequence()')
    pass

    
  def stopSequence(self):
    print('stopSequence()')

    
  def updateScanPlane(self, param):
    self.signalManager.emitSignal('consoleTextMR', 'Updating scan plane..')
    print(param)
    



