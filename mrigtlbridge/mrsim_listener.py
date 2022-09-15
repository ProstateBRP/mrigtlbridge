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
      'sequenceStarted' : None,
      'updateParameter' : 'dict'
    }

    self.threadActive = False
    self.jobQueue = False
    self.counter = 0
    self.streaming = False

    self.state = 'IDLE' # either 'IDLE' or 'SCAN'
    self.interval = 1000 # ms
    self.imageParams = {}
    self.imageParams['columns']      = 256
    self.imageParams['rows']         = 256
    self.imageParams['slices']       = 1
    self.imageParams['colSpacing']   = 1.0
    self.imageParams['rowSpacing']   = 1.0
    self.imageParams['sliceSpacing'] = 5.0
    
    self.matrix = {}
    self.matrix[0] = [[1.0,0.0,0.0,0.0],
                      [0.0,1.0,0.0,0.0],
                      [0.0,0.0,1.0,0.0],
                      [0.0,0.0,0.0,1.0]]
    
  def connectSlots(self, signalManager):
    super().connectSlots(signalManager)
    print('MRSIMListener.connectSlots()')
    self.signalManager.connectSlot('startSequence', self.startSequence)
    self.signalManager.connectSlot('stopSequence', self.stopSequence)
    self.signalManager.connectSlot('updateScanPlane', self.updateScanPlane)
    self.signalManager.connectSlot('updateParameter', self.updateParameter)

  def disconnectSlots(self):
    
    super().disconnectSlots()
    
    print('MRSIMListener.disconnectSlots()')
    if self.signalManager:
      self.signalManager.disconnectSlot('startSequence', self.startSequence)
      self.signalManager.disconnectSlot('stopSequence', self.stopSequence)
      self.signalManager.disconnectSlot('updateScanPlane', self.updateScanPlane)
      self.signalManager.disconnectSlot('updateParameter', self.updateParameter)

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

    if self.state == 'SCAN':
      
      self.sendDummyImage()

    QtCore.QThread.msleep(self.interval) # TODO: This may give SRC more time to process images 

    
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
    self.state = 'SCAN'

    
  def stopSequence(self):
    print('stopSequence()')
    self.state = 'IDLE'

    
  def updateScanPlane(self, param):
    print(param)

    #
    # param['plane_id'] : Plane ID (0, 1, 2, 3, ...)
    # param['matrix'  ] : 4x4 matrix
    #

    matrix4x4 = param['matrix']

    for i in range(4):
      matrix4x4[i][0] = - matrix4x4[i][0]
      matrix4x4[i][1] = - matrix4x4[i][1]
        
    matrix = np.array(matrix4x4)

    # Set slice group
    plane_id = param['plane_id']
    self.matrix[plane_id] = matrix

    self.signalManager.emitSignal('consoleTextMR', str(matrix))


  def updateParameter(self, param):
    
    if 'interval' in param.keys():
      value = flaot(param['interval'])
      if value > 0.0 and value < 10.0:
        self.interval = value
      else:
        self.signalManager.emitSignal('consoleTextMR', 'MRSIMListner.updateParameter(): ERROR: the interval is out of range.')
    if 'columns' in param.keys():
      self.imageParams['columns']      = self.param['columns']
    if 'rows' in param.keys():
      self.imageParams['rows']         = self.param['rows']
    if 'slices' in param.keys():
      self.imageParams['slices']       = self.param['slices']
    if 'colSpacing' in param.keys():
      self.imageParams['colSpacing']   = self.param['colSpacing']
    if 'rowSpacing' in param.keys():
      self.imageParams['rowSpacing']   = self.param['rowSpacing']
    if 'sliceSpacing' in param.keys():
      self.imageParams['sliceSpacing'] = self.param['sliceSpacing']

    
  def sendDummyImage(self):

    param = {}
        
    columns      = self.imageParams['columns']
    rows         = self.imageParams['rows']
    slices       = self.imageParams['slices']
    colSpacing   = self.imageParams['colSpacing']
    rowSpacing   = self.imageParams['rowSpacing']
    sliceSpacing = self.imageParams['sliceSpacing']
    
    dtypeName = 'int16'
    #dtypeTable = {
    #  'int8':    [2, 1],   #TYPE_INT8    = 2, 1 byte
    #  'uint8':   [3, 1],   #TYPE_UINT8   = 3, 1 byte
    #  'int16':   [4, 2],   #TYPE_INT16   = 4, 2 bytes
    #  'uint16':  [5, 2],   #TYPE_UINT16  = 5, 2 bytes
    #  'int32':   [6, 4],   #TYPE_INT32   = 6, 4 bytes
    #  'uint32':  [7, 4],   #TYPE_UINT32  = 7, 4 bytes
    #  'float32': [10,4],   #TYPE_FLOAT32 = 10, 4 bytes 
    #  'float64': [11,8],   #TYPE_FLOAT64 = 11, 8 bytes
    #}

    binary = []
    binaryOffset = []


    # Generate image
    image_size = [columns, rows, slices]
    radius = 60

    timestep = 0

    # The following dummy image code was based on https://github.com/lassoan/pyigtl/blob/master/examples/example_image_server.py
    cx = (1+np.sin(timestep*0.05)) * 0.5 * (image_size[0]-2*radius)+radius
    cy = (1+np.sin(timestep*0.06)) * 0.5 * (image_size[1]-2*radius)+radius
    y, x = np.ogrid[-cx:image_size[0]-cx, -cy:image_size[1]-cy]
    mask = x*x + y*y <= radius*radius
    voxels = np.ones((image_size[0], image_size[1], image_size[2]), dtype=np.int16)
    voxels[mask] = 255

    # numpy image axes are in kji order, while we generated the image with ijk axes
    voxels = np.transpose(voxels, axes=(2, 1, 0))

    binary.append(voxels)
    binaryOffset.append(0)

    
    #rawMatrix = [[0.0,0.0,0.0,0.0],
    #             [0.0,0.0,0.0,0.0],
    #             [0.0,0.0,0.0,0.0],
    #             [0.0,0.0,0.0,1.0]]
    #
    ## Create C array for coordinates
    ## Position
    #rawMatrix[0][3] = 0.0
    #rawMatrix[1][3] = 0.0
    #rawMatrix[2][3] = 0.0
    #
    ## Orientation
    #rawMatrix[0][0] = 1.0
    #rawMatrix[1][0] = 0.0
    #rawMatrix[2][0] = 0.0
    #rawMatrix[0][1] = 0.0
    #rawMatrix[1][1] = 1.0
    #rawMatrix[2][1] = 0.0      
    #rawMatrix[0][2] = 0.0
    #rawMatrix[1][2] = 0.0
    #rawMatrix[2][2] = 1.0

    rawMatrix = self.matrix[0]

    endianness = 1 if voxels.dtype.byteorder == ">" else 2
           
    param['dtype']               = dtypeName
    param['dimension']           = [columns, rows, slices]
    param['spacing']             = [colSpacing, rowSpacing, sliceSpacing]
    param['name']                = 'MRSIM Image'
    param['numberOfComponents']  = 1
    param['endian']              = endianness
    param['matrix']              = rawMatrix
    param['attribute']           = {}
    param['binary']              = binary
    param['binaryOffset']        = binaryOffset

    if self.signalManager:
      self.signalManager.emitSignal('sendImageIGTL', param)


    



