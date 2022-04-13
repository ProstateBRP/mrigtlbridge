import os, time, json, sys
import numpy as np
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock

class ListenerBase(QtCore.QThread):
  
  def __init__(self, *args):
    super().__init__(*args)
    
    self.threadActive = False
    self.signalManager = None

    # If the listener uses a custom signals, list the names and types in the following dictionary.
    # The dictionally used to add the custom signals to the signal manager.
    # See WidgetBase.setSignalManager() for detail.
    self.customSignalList = {
    }

    self.parameter = {
    }

    
  def configure(self, param):
    
    for key in param:
      if key in self.parameter:
        self.parameter[key] = param[key]

    
  def connectSlots(self, signalManager):
    self.signalManager = signalManager    
    

  # Main Thread Function
  # This function should not be overridden by the child classes, unless any special steps are required.
  def run(self):
    
    if self.initialize() == False:
      self.signalManager.emitSignal('listenerTerminated')
      self.quit()
    
    # Initialization was successful. Start the main loop
    self.threadActive = True

    while self.threadActive:
      self.process()

    self.finalize()
    self.signalManager.emitSignal('listenerTerminated')
    self.quit()

  # Function to stop the thread
  # This function should not be overridden by the child classes, unless any special steps are required.
  def stop(self):
    self.threadActive = False
    self.wait()
    # TODO: Send a signal to notify the widget?

  # Initialization procedure called immediately after the thread is started.
  # To be implemented in the child classes
  def initialize(self):
    # Return True if success
    return True


  # Main procedure called from the main loop
  # To be implemented in the child classes
  def process(self):
    # This method is implemented in a child class and called from run()
    pass

  # Tearmination procedure called after the thread is stopped.
  # (the name 'terminate()' is not used to avoild conflict with QThread.terminate())
  # To be implemented in the child classes
  def finalize(self):
    pass

  
      

