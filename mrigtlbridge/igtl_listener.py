import os, time, json, sys
import numpy as np
from datetime import datetime

import openigtlink as igtl

from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock


# ------------------------------------OPENIGTLINK------------------------------------
class OpenIGTLinkListener(QtCore.QThread):
  textBoxSignal = QtCore.pyqtSignal(str)
  closeSocketSignal = QtCore.pyqtSignal()
  transformReceivedSignal = QtCore.pyqtSignal(np.ndarray,dict)
  startSequenceSignal = QtCore.pyqtSignal()
  stopSequenceSignal = QtCore.pyqtSignal()
  
  def __init__(self):
    QtCore.QThread.__init__(self)
    self.threadActive = False
    self.clientServer = None
    self.imageQueue = []
    self.imgIntvQueue = np.zeros(5)
    self.imgIntvQueueIndex = 0
    self.imgIntv = 1.0     # Frequency of incoming images (second)
    self.prevImgTime = 0.0 # Previous image arrival time (to estimate self.imgIntv) (second)

    # Connect signals
    self.transformReceivedSignal.connect(self.openIGTLinkTransformToSRC)
    self.startSequenceSignal.connect(self.startSequenceSRC)
    self.stopSequenceSignal.connect(self.stopSequenceSRC)
    #self.closeSocketSignal.connect(self.disconnectOpenIGTEvent)

  def connect(self, ip, port):
    self.clientServer = igtl.ClientSocket.New()
    self.clientServer.SetReceiveTimeout(1) # Milliseconds
    #self.clientServer.SetReceiveBlocking(0)
    #self.clientServer.SetSendBlocking(0)
    ret = self.clientServer.ConnectToServer(ip,int(port))
    if ret == 0:
      self.textBoxSignal.emit("Connection successful")
    else:
      self.textBoxSignal.emit("Connection failed")

    self.threadActive = True

  def run(self):
    transMsg = igtl.TransformMessage.New()
    headerMsg = igtl.MessageBase.New()
    stringMsg = igtl.StringMessage.New()
    
    # The following variables are used to regulate the incoming messages.
    prevImgTime = 0.0
    
    prevTransMsgTime = 0.0
    minTransMsgInterval = 0.1 # 10 Hz
    pendingTransMsg = False
    
    while self.threadActive:
      ## ---------------------- SENDING ----------------------------
      ## NOTE: Sending process has been moved to the other thread.
      ## See self.onSendImageRun()
      # for image in self.imageQueue:
      #   imgTime = time.time()
      #   imgIntv = imgTime - prevImgTime
      #   prevImgTime = imgTime
      #   self.onSendImageRun(image[0], image[1])
      # self.imageQueue = []

      # Dynamically adjust the threshold interval for transform messages
      minTransMsgInterval = self.imgIntv / 2.0
      if minTransMsgInterval > 0.5:
        minTransMsgInterval = 0.5
      elif minTransMsgInterval < 0.03:
        minTransMsgInterval = 0.03
      #print("imgIntv = %f, minTransMsgInterval = %f" % (self.imgIntv, minTransMsgInterval))

      # ---------------------- RECEIVING ----------------------------
      # Initialize receive buffer
      headerMsg.InitPack()

      self.clientServer.SetReceiveTimeout(1) # Milliseconds
      timeout = True
      [result, timeout] = self.clientServer.Receive(headerMsg.GetPackPointer(), headerMsg.GetPackSize(), timeout)

      if (result == 0 and not timeout):
        self.clientServer.CloseSocket()
        #self.closeSocketSignal.emit()
        return
      elif (result == -1):
        # Time out
        if pendingTransMsg:
          msgTime = time.time()
          if msgTime - prevTransMsgTime > minTransMsgInterval:
            print("Sending out pending transform.")
            self.onReceiveTransform(transMsg)
            prevTransMsgTime = msgTime
            pendingTransMsg = False
        continue        
      elif (result != headerMsg.GetPackSize()):
        if not timeout:
          print("Incorrect pack size!")
        continue
        

      # Deserialize the header
      headerMsg.Unpack()

      # Check data type and respond accordingly
      msgType = headerMsg.GetDeviceType()
      self.textBoxSignal.emit("Recieved: %s" % msgType)
      #print('reached')
      # ---------------------- TRANSFORM ----------------------------
      if (msgType == "TRANSFORM"):
        #print("TransformReceived")
        #onReceiveTransform(headerMsg)

        transMsg.Copy(headerMsg.GetPointer()) # Can't get MessageHeaders to instantiate, but SetMessageHeader seems to just be calling Copy
        transMsg.AllocatePack()

        # Receive transform data from the socket
        timeout = False
        [r, timeout] = self.clientServer.Receive(transMsg.GetPackBodyPointer(), transMsg.GetPackBodySize(), timeout)

        transMsg.Unpack()
        msgTime = time.time()
        
        # Check the time interval. Send the transform to MRI only if there was enough interval.
        if msgTime - prevTransMsgTime > minTransMsgInterval:
          self.onReceiveTransform(transMsg)
          prevTransMsgTime = msgTime
          pendingTransMsg = False
        else:
          pendingTransMsg = True
        
      # ---------------------- STRING ----------------------------
      elif (msgType == "STRING"):
        #Create a message buffer to receive string data
        stringMsg.Copy(headerMsg.GetPointer()) # Can't get MessageHeaders to instantiate, but SetMessageHeader seems to just be calling Copy
        stringMsg.AllocatePack()

        # Receive string data from the socket
        timeout = False
        [r, timeout] = self.clientServer.Receive(stringMsg.GetPackBodyPointer(), stringMsg.GetPackBodySize(), timeout)
        stringMsg.Unpack()
        
        self.onReceiveString(stringMsg)

      elif (msgType == "POINT"):
        pass
        #print("Point")

      QtCore.QThread.msleep(int((1000.0*minTransMsgInterval)/2.0)) # Give some time to the other thread.
      

  def stop(self):
    self.threadActive = False
    #self.terminate()
    self.wait()

  def onReceiveTransform(self,transMsg):

    matrix4x4 = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    matrix4x4 = transMsg.GetMatrix(matrix4x4)

    # Flip X/Y coordinates (R->L, A->P)
    for i in range(2):
      for j in range(4):
        matrix4x4[i][j] = -matrix4x4[i][j]
        
    matrix = np.array(matrix4x4)

    # Set slice group
    param={}
    if transMsg.GetDeviceName() == "PLANE_0":
      param['index'] = 0
    elif transMsg.GetDeviceName() == "PLANE_1":
      param['index'] = 1
    elif transMsg.GetDeviceName() == "PLANE_2":
      param['index'] = 2
    
    self.textBoxSignal.emit(str(matrix))
    self.transformReceivedSignal.emit(matrix,param)
    return 1

  def onReceiveString(self, headerMsg):
    string = headerMsg.GetString()

    #global FLIP
    if (string == "START_SEQUENCE"):
      self.startSequenceSignal.emit()
      #stream_commands = {'imageStreamStart': self.onImageStreamStart, 'imageStreamEnd': self.onStreamEnd, 'imageStream': self.onStreaming}
    elif (string == "STOP_SEQUENCE"):
      self.stopSequenceSignal.emit()

  def disconnectOpenIGTEvent(self):
    self.openIGTLinkThread.stop()
    self.openIGTLinkThread = None

    self.openIGTConnectButton.setEnabled(True)
    self.openIGTDisconnectButton.setEnabled(False)
    self.openIGT_IpEdit.setEnabled(True)
    self.openIGT_PortEdit.setEnabled(True)

  def openIGTLinkTransformToSRC(self, matrix, param):
    if (self.srcThread):
      self.srcThread.setSliceMatrix4x4(matrix, param)


