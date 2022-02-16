import os, time, json, sys
import numpy as np
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock

# ------------------------------------MR------------------------------------
class MRLSIMistener(QtCore.QThread):

  def __init__(self, *args):
    super().__init__(*args)
    self.threadActive = False
    self.jobQueue = False
    self.counter = 0
    self.lock = Lock()

    self.baseline = False
    self.singleSlice = False

    self.streaming = False

  def registerSlots(self, signalManager):
    signalManager.registerSlot('startSequence', self.startSequence)
    signalManager.registerSlot('stopSequence', self.stopSequence)
    signalManager.registerSlot('updateScanPlane', self.updateScanPlane)
    
  def connect(self, ip, port, licenseFile):
    self.textBoxSignal.emit('Connected.')
    self.threadActive = True

  def disconnect(self):
    pass

  def startSequence(self):
    print('startSequence()')

  def stopSequence(self):
    print('stopSequence()')

  def updateScanPlane(self, param):
    print('updateScanPlane()')
    print(param)
    
  def run(self):
    while self.threadActive:
      if self.jobQueue:
        self.startSequence()
        self.jobQueue = False
      QtCore.QThread.msleep(10)



