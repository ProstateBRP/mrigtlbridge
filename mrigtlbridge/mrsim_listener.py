import os, time, json, sys
import numpy as np
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock

# ------------------------------------MR------------------------------------
class MRLSIMistener(QtCore.QThread):
  textBoxSignal = QtCore.pyqtSignal(str)
  imageSignal = QtCore.pyqtSignal(object)
  streamSignal = QtCore.pyqtSignal(bool)

  def __init__(self):
    QtCore.QThread.__init__(self)
    self.threadActive = False
    self.jobQueue = False
    self.counter = 0
    self.lock = Lock()

    self.baseline = False
    self.singleSlice = False

    self.streaming = False

  def connect(self, ip, port, licenseFile):
    self.textBoxSignal.emit('Connected.')
    self.threadActive = True

  def disconnect(self):
    pass

  def run(self):
    while self.threadActive:
      if self.jobQueue:
        self.startSequence()
        self.jobQueue = False
      QtCore.QThread.msleep(10)



