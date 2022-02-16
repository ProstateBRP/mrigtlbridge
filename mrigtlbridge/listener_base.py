import os, time, json, sys
import numpy as np
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock

# ------------------------------------OPENIGTLINK------------------------------------
class ListenerBase(QtCore.QThread):
  
  def __init__(self, *args):
    super().__init__(*args)
    
    self.threadActive = False
    self.signalManager = None

    
  def connectSlots(self, signalManager):
    self.signalManager = signalManager    
    

  def run(self):
    
    if self.initialize() == False:
      return False

    # Initialization was successful. Start the main loop
    self.threadActive = True

    while self.threadActive:
      self.process()

      
  def initialize(self):
    # Return True if success
    return True


  def process(self):
    # This method is implemented in a child class and called from run()
    pass


  def stop(self):
    self.threadActive = False
    #self.terminate()
    self.wait()

      

