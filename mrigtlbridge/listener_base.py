import os, time, json, sys
import numpy as np
from datetime import datetime

from multiprocessing import Process, Queue, Pipe, Value, Manager

import logging


class ListenerBase(Process):
  
  def __init__(self, daemon=True):
    super().__init__()

    self.daemon = daemon

    self.threadActive = Value('b', False)

    self.signalPipe = None

    # If the listener uses a custom signals, list the names and types in the following dictionary.
    # The dictionally used to add the custom signals to the signal manager.
    # See WidgetBase.setSignalManager() for detail.
    self.customSignalList = {
    }

    self.parameter = {
    }

    
  def __del__(self):
    pass
    #self.emitSignal('listenerTerminated', self.__class__.__name__)
    
    
  def configure(self, param):
    
    for key in param:
      if key in self.parameter:
        self.parameter[key] = param[key]


  def setSignalPipe(self, pipe):
    self.signalPipe = pipe


  def emitSignal(self, name, param=None):
    if self.signalPipe:
      self.signalPipe.send((name, param))


  def connectSlots(self, signalManager):
    pass


  def disconnectSlots(self):
    pass


  # Main Child Process Function
  # This function should not be overridden by the child classes, unless any special steps are required.
  def run(self):

    # Note: 'self.__class__.__name__' is intended to give the name of the chlid class, not this base class.

    print('ListenerBase.run() started.')
    if self.initialize() == True:
      # Initialization was successful. Start the main loop
      self.emitSignal('listenerConnected', self.__class__.__name__)
      self.threadActive.value = True
      while self.threadActive.value:
        self.process()
      self.emitSignal('listenerDisconnected', self.__class__.__name__)
    else:
      pass

    self.finalize()
    self.emitSignal('listenerTerminated', self.__class__.__name__)


  # Function to stop the thread
  # This function should not be overridden by the child classes, unless any special steps are required.
  def stop(self):
    self.threadActive.value = False
    time.sleep(0.2)
    self.terminate()
    #self.wait()
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
    #self.disconnectSlots();
