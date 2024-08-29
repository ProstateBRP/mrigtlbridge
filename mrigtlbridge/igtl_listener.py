import os, time, json, sys
import numpy as np
from datetime import datetime

import openigtlink as igtl


from PyQt5 import QtCore, QtGui, QtWidgets

from threading import Lock

from .listener_base import ListenerBase
from .common import DataTypeTable

import logging

# ------------------------------------OPENIGTLINK------------------------------------
class IGTLListener(ListenerBase):
  
  closeSocketSignal = QtCore.pyqtSignal()
  transformReceivedSignal = QtCore.pyqtSignal(np.ndarray,dict)
  startSequenceSignal = QtCore.pyqtSignal()
  stopSequenceSignal = QtCore.pyqtSignal()

  def __init__(self, *args):
    super().__init__(*args)
    self.clientServer = None
    self.imageQueue = []
    self.imgIntvQueue = np.zeros(5)
    self.imgIntvQueueIndex = 0
    self.imgIntv = 1.0     # Frequency of incoming images (second)
    self.prevImgTime = 0.0 # Previous image arrival time (to estimate self.imgIntv) (second)
    
    self.parameter['ip'] = 'localhost'
    self.parameter['port'] = '18944'
    self.parameter['sendTimestamp'] = 1

    self.state = 'INIT' # Either 'INIT', 'IDLE', or 'SCAN'

    
  def connectSlots(self, signalManager):
    super().connectSlots(signalManager)
    signalManager.connectSlot('disconnectIGTL',  self.disconnectOpenIGTEvent)
    signalManager.connectSlot('sendImageIGTL',  self.sendImageIGTL)
    signalManager.connectSlot('sendTrackingDataIGTL', self.sendTrackingDataIGTL)
    #self.signalManager.connectSlot('setSocketParam', self.setSocketParam)

    
  def disconnectSlots(self, signalManager):
    super().disconnectSlots()
    signalManager.disconnectSlot('disconnectIGTL',  self.disconnectOpenIGTEvent)
    signalManager.disconnectSlot('sendImageIGTL',  self.sendImageIGTL)
    signalManager.disconnectSlot('sendTrackingDataIGTL', self.sendTrackingDataIGTL)
      

  def initialize(self):
    self.emitSignal('consoleTextIGTL', "Initializing IGTL Listener...")
    #self.transMsg = igtl.TransformMessage.New()
    #self.headerMsg = igtl.MessageBase.New()
    #self.stringMsg = igtl.StringMessage.New()
    
    # The following variables are used to regulate the incoming messages.
    self.prevImgTime = 0.0
    self.prevTransMsgTime = 0.0
    self.minTransMsgInterval = 0.1 # 10 Hz
    self.pendingTransMsg = False

    socketIP = self.parameter['ip']
    socketPort = self.parameter['port']

    ret = self.connect(socketIP, socketPort)
    return ret


  def process(self):

    self.minTransMsgInterval = 0.1 # 100ms

    # Initialize receive buffer
    self.headerMsg = igtl.MessageBase.New()    
    self.headerMsg.InitPack()

    self.clientServer.SetReceiveTimeout(50) # Milliseconds
    #self.clientServer.SetReceiveTimeout(int(self.minTransMsgInterval*1000.0)) # Milliseconds
    timeout = True
    [result, timeout] = self.clientServer.Receive(self.headerMsg.GetPackPointer(), self.headerMsg.GetPackSize(), timeout)

    ## TODO: timeout always return True - is it a bug?
    
    ## TODO: Need to detect disconnection
    #if result == 0:
    #  self.clientServer.CloseSocket()
    #  #self.closeSocketSignal.emit()
    #  return
    msgTime = time.time()
    
    if result==0 and timeout:
      # Time out
      if self.pendingTransMsg:
        if msgTime - self.prevTransMsgTime > self.minTransMsgInterval:
          self.emitSignal('consoleTextIGTL', "Sending out pending transform.")
          self.transMsg.Unpack()
          self.onReceiveTransform(self.transMsg)
          self.prevTransMsgTime = msgTime
          self.pendingTransMsg = False
      return
      
    if (result != self.headerMsg.GetPackSize()):
      self.emitSignal('consoleTextIGTL', "Incorrect pack size!")
      return
      
    # Deserialize the header
    self.headerMsg.Unpack()

    # Check data type and respond accordingly
    msgType = self.headerMsg.GetDeviceType()
    if msgType != '':
      self.emitSignal('consoleTextIGTL', "Recieved: %s" % msgType)
    
    # ---------------------- TRANSFORM ----------------------------
    if (msgType == "TRANSFORM"):
      self.transMsg = igtl.TransformMessage.New()
      self.transMsg.Copy(self.headerMsg.GetPointer()) # Can't get MessageHeaders to instantiate, but SetMessageHeader seems to just be calling Copy
      self.transMsg.AllocatePack()

      # Receive transform data from the socket
      timeout = False
      [r, timeout] = self.clientServer.Receive(self.transMsg.GetPackBodyPointer(), self.transMsg.GetPackBodySize(), timeout)

      # Check the time interval. Send the transform to MRI only if there was enough interval.
      if msgTime - self.prevTransMsgTime > self.minTransMsgInterval:
        self.transMsg.Unpack()
        self.onReceiveTransform(self.transMsg)
        self.prevTransMsgTime = msgTime
        self.pendingTransMsg = False
      else:
        self.pendingTransMsg = True
      
    # ---------------------- STRING ----------------------------
    elif (msgType == "STRING"):
      #Create a message buffer to receive string data
      self.stringMsg = igtl.StringMessage.New()


      self.stringMsg.Copy(self.headerMsg.GetPointer()) # Can't get MessageHeaders to instantiate, but SetMessageHeader seems to just be calling Copy
      self.stringMsg.AllocatePack()

      # Receive string data from the socket
      timeout = False
      [r, timeout] = self.clientServer.Receive(self.stringMsg.GetPackBodyPointer(), self.stringMsg.GetPackBodySize(), timeout)
      self.stringMsg.Unpack()
      
      self.onReceiveString(self.stringMsg)

    elif (msgType == "POINT"):
      pass

    endTime = time.time()
    sleepTime = self.minTransMsgInterval - (endTime - msgTime)
    logging.debug('sleep time = ' + str(sleepTime))
    if sleepTime < 0:
      sleepTime = 0

    QtCore.QThread.msleep(int(1000.0*sleepTime)) # Give some time to the other thread. TODO: Is this OK?

    
  def finalize(self):
    self.emitSignal('consoleTextIGTL', "Finalizing... close socket.")
    self.clientServer.CloseSocket()
    del self.clientServer
    self.clientServer = None

    super().finalize()

    
  def connect(self, ip, port):

    self.clientServer = igtl.ClientSocket.New()
    self.clientServer.SetReceiveTimeout(1) # Milliseconds
    #self.clientServer.SetReceiveBlocking(0)
    #self.clientServer.SetSendBlocking(0)
    ret = self.clientServer.ConnectToServer(ip,int(port))
    if ret == 0:
      self.emitSignal('consoleTextIGTL', "Connection successful")
      return True
    else:
      self.emitSignal('consoleTextIGTL', "Connection failed")
      return False

      
  def onReceiveTransform(self,transMsg):

    matrix4x4 = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    matrix4x4 = transMsg.GetMatrix(matrix4x4)

    param={}
    if transMsg.GetDeviceName() == "PLANE_0" or transMsg.GetDeviceName() == "PLANE":
      param['plane_id'] = 0
    elif transMsg.GetDeviceName() == "PLANE_1":
      param['plane_id'] = 1
    elif transMsg.GetDeviceName() == "PLANE_2":
      param['plane_id'] = 2

    param['matrix'] = matrix4x4
    
    self.emitSignal('consoleTextIGTL', str(matrix4x4))
    self.emitSignal('updateScanPlane', param)
    
    return 1

  
  def onReceiveString(self, headerMsg):
    string = headerMsg.GetString()

    if (string == "START_SEQUENCE"):
      self.state = 'SCAN'
      self.emitSignal('startSequence')
    elif (string == "STOP_SEQUENCE"):
      self.state = 'IDLE'
      self.emitSignal('stopSequence')
    elif (string == "START_UP"):   # Initialize
      self.state = 'IDLE'

      
  def disconnectOpenIGTEvent(self):
    #self.openIGTLinkThread.stop()
    #del self.openIGTLinkThread
    #self.openIGTLinkThread = None
    #
    #self.openIGTConnectButton.setEnabled(True)
    #self.openIGTDisconnectButton.setEnabled(False)
    #self.openIGT_IpEdit.setEnabled(True)
    #self.openIGT_PortEdit.setEnabled(True)
    pass

  #def openIGTLinkTransformToSRC(self, matrix, param):
  #  if (self.srcThread):
  #    self.srcThread.setSliceMatrix4x4(matrix, param)

  
  def sendImageIGTL(self, param):

    self.emitSignal('consoleTextIGTL', "Sending image...")
    #
    # 'param' dictionary must contain the following members:
    #
    #  param['dtype']       : Data type in str. See mrigtlbridge/common.py
    #  param['dimension']   : Matrix size in each dimension e.g., [256, 256, 128]
    #  param['spacing']     : Pixel spacing in each dimension e.g., [1.0, 1.0, 5.0]
    #  param['name']        : Name of the image in the string type.
    #  param['numberOfComponents'] : Number of components per voxel.
    #  param['endian']      : Endian used in the binary data. 1: big; 2: little
    #  param['matrix']      : 4x4 transformation matrix to map the pixel to the physical space. e.g.,
    #                        [[0.0,0.0,0.0,0.0],
    #                         [0.0,0.0,0.0,0.0],
    #                         [0.0,0.0,0.0,0.0],
    #                         [0.0,0.0,0.0,1.0]]
    #  param['attribute']   : Dictionary to pass miscellaneous attributes (e.g., imaging parameters) (OPTIONAL)
    #  param['binary']      : List of binary arrays. The list allows fragmenting the the binary image
    #                       into multiple binary arrays (e.g., each slice in a multi-slice image can be
    #                       stored in independent binary arrays).
    #  param['binaryOffset']: Offset to each binary array.
    #  param['timestamp']   : Timestamp (OPTIONAL)

    #
    # TODO: This could be moved to another thread?
    #

    try:
      dtype              = param['dtype']
      dimension          = param['dimension']
      spacing            = param['spacing']
      name               = param['name']
      numberOfComponents = param['numberOfComponents']
      endian             = param['endian']
      matrix             = param['matrix']
      binary             = param['binary']
      binaryOffset       = param['binaryOffset']
    except KeyError:
      self.emitSignal('consoleTextIGTL', "ERROR: Missing message information.")
      return

    # Since param['attribute'] is optional, we don't return on the KeyError exception.
    try:
      attribute          = param['attribute']
    except KeyError:
      attribute = None

    try:
      timestamp          = param['timestamp']
    except KeyError:
      timestamp = None

    imageMsg = igtl.ImageMessage.New()
    imageMsg.SetDimensions(int(dimension[0]), int(dimension[1]), int(dimension[2]))
    
    if dtype in DataTypeTable:
      imageMsg.SetScalarType(DataTypeTable[dtype][0])
      scalarSize = DataTypeTable[dtype][1]

    imageMsg.SetDeviceName(name)
    imageMsg.SetNumComponents(numberOfComponents)
    imageMsg.SetEndian(endian) # little is 2, big is 1
    imageMsg.AllocateScalars()

    # Copy the binary data
    i = 0
    for offset in binaryOffset:
      igtl.copyBytesToPointer(binary[i].tobytes(), igtl.offsetPointer(imageMsg.GetScalarPointer(), offset))
      i = i + 1

    imageMsg.SetSpacing(spacing[0], spacing[1], spacing[2])
    imageMsg.SetMatrix(matrix)
    imageMsg.Pack()
    
    self.clientServer.Send(imageMsg.GetPackPointer(), imageMsg.GetPackSize())

    # Send a separate timestamp message.

    if self.parameter['sendTimestamp'] == 1 and timestamp is not None:
      textMsg = igtl.StringMessage.New()
      textMsg.SetDeviceName('IMAGE_TIMESTAMP')
      textMsg.SetString(str(timestamp))
      textMsg.Pack()
      self.clientServer.Send(textMsg.GetPackPointer(), textMsg.GetPackSize())


  def sendTrackingDataIGTL(self, param):

    self.emitSignal('consoleTextIGTL', "Sending tracking data...")
    #
    # 'param' is an array of coil data, which consists of the following fields:
    #
    #  coil['name']         : Coil name
    #  coil['position_pcs'] : Coil position in the patient coordinate system
    #  coil['position_dcs'] : Coil position in the device coordinate system

    #
    # TODO: This could be moved to another thread?
    #

    if len(param) == 0:
      self.emitSignal('consoleTextIGTL', "ERROR: No tracking data.")
      return

    trackingDataMsg = igtl.TrackingDataMessage.New()
    trackingDataMsg.SetDeviceName("MRTracking")

    for name, coil in param.items():
      pos = coil['position_pcs'] # In the patient coordinate system
      trackElement = igtl.TrackingDataElement.New();
      trackElement.SetName(name)
      trackElement.SetType(igtl.TrackingDataElement.TYPE_TRACKER)
      trackElement.SetPosition(pos[0], pos[1], pos[2])
      trackingDataMsg.AddTrackingDataElement(trackElement)

    trackingDataMsg.Pack()
    self.clientServer.Send(trackingDataMsg.GetPackPointer(), trackingDataMsg.GetPackSize())
