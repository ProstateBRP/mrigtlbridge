import os, time, json, sys
import numpy as np
import os.path
import SimpleITK as sitk

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

    self.parameter['imageListFile'] = '' # If 'None', randome images are generated.
    self.imageList = None
    self.imagePath = ''
    self.imageCurrentIndex = -1

    self.parameter['imagePosition'] = 'file' # Either 'file' or 'target'. If 'target', use the target given by the server.

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

      if self.imageList:
        self.sendImageFromFile()
      else:
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

    if os.path.isfile(self.parameter['imageListFile']):
      self.signalManager.emitSignal('consoleTextMR', 'Sending images using the list.')
      (self.imageList, self.imagePath) = self.loadImageList(self.parameter['imageListFile'])
    else:
      self.signalManager.emitSignal('consoleTextMR', 'Sending dummy images.')
      self.imageList = None
      self.imagePath = ''
      self.imageCurrentIndex = -1

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


  def loadImageList(self, filepath):

    imageList = None
    path = ''

    with open(filepath) as listfile:
        imageList = json.load(listfile)

    if imageList:
      path = os.path.dirname(filepath)

    return (imageList, path)

    
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

    ts = time.time()

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
    param['timestamp']           = ts

    if self.signalManager:
      self.signalManager.emitSignal('sendImageIGTL', param)


  def sendImageFromFile(self):

    self.imageCurrentIndex += 1

    if self.imageCurrentIndex < 0 or self.imageCurrentIndex >= len(self.imageList):
      self.imageCurrentIndex = 0

    k = list(self.imageList)[self.imageCurrentIndex]
    filePathMag = self.imagePath + '/' + self.imageList[k]['M']
    filePathPh = self.imagePath + '/' + self.imageList[k]['P']

    self.signalManager.emitSignal('consoleTextMR', 'Sending:')
    self.signalManager.emitSignal('consoleTextMR', '  ' + self.imageList[k]['M'])
    self.signalManager.emitSignal('consoleTextMR', '  ' + self.imageList[k]['P'])

    image = {}
    image['M'] = sitk.ReadImage(filePathMag)
    image['P'] = sitk.ReadImage(filePathPh)

    for k, v in image.items():
      param = {}

      image_size = np.array(v.GetSize())
      image_spacing = np.array(v.GetSpacing())
      image_direction = np.array(v.GetDirection())
      image_position = np.array(v.GetOrigin())

      # Image orientation matrix
      # The orientation matrix is defined as N = [n1, n2, n3], where n1, n2, and n3 are
      # normal column vectors representing the directions of the i, j, and k indicies.
      norm = image_direction
      norm = norm.reshape(3,3)

      # Switch from LPS to RAS
      lpsToRas = np.transpose(np.array([[-1., -1.,1.]]))
      norm = norm * lpsToRas

      # Location of the first voxel in RAS
      pos = image_position.reshape(3,1) * lpsToRas

      # Location of the the image center
      # OpenIGTLink uses the location of the volume center while SliceLocation in DICOM is the position of the first voxel.
      offset = norm * (image_spacing * (image_size-1.0)/2.0)
      pos = pos + offset[:,[0]] + offset[:,[1]] + offset[:,[2]]

      rawMatrix = [[0.0,0.0,0.0,0.0],
                   [0.0,0.0,0.0,0.0],
                   [0.0,0.0,0.0,0.0],
                   [0.0,0.0,0.0,1.0]]

      if self.parameter['imagePosition'] == 'file':
        # Create C array for coordinates
        # Position
        rawMatrix[0][3] = pos[0]
        rawMatrix[1][3] = pos[1]
        rawMatrix[2][3] = pos[2]

        ## Orientation
        rawMatrix[0][0] = norm[0][0]
        rawMatrix[1][0] = norm[1][0]
        rawMatrix[2][0] = norm[2][0]
        rawMatrix[0][1] = norm[0][1]
        rawMatrix[1][1] = norm[1][1]
        rawMatrix[2][1] = norm[2][1]
        rawMatrix[0][2] = norm[0][2]
        rawMatrix[1][2] = norm[1][2]
        rawMatrix[2][2] = norm[2][2]

      else:
        # Create C array for coordinates
        # Position
        targetMatrix = self.matrix[0]
        rawMatrix[0][3] = targetMatrix[0][3]
        rawMatrix[1][3] = targetMatrix[1][3]
        rawMatrix[2][3] = targetMatrix[2][3]

        ## Orientation
        rawMatrix[0][0] = targetMatrix[0][0]
        rawMatrix[1][0] = targetMatrix[1][0]
        rawMatrix[2][0] = targetMatrix[2][0]
        rawMatrix[0][1] = targetMatrix[0][1]
        rawMatrix[1][1] = targetMatrix[1][1]
        rawMatrix[2][1] = targetMatrix[2][1]
        rawMatrix[0][2] = targetMatrix[0][2]
        rawMatrix[1][2] = targetMatrix[1][2]
        rawMatrix[2][2] = targetMatrix[2][2]

      voxels = sitk.GetArrayFromImage(v)

      dtypeName = str(voxels.dtype)
      print('Data type = ' + str(dtypeName))

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

      # numpy image axes are in kji order, while we generated the image with ijk axes
      #voxels = np.transpose(voxels, axes=(2, 1, 0))

      binary.append(voxels)
      binaryOffset.append(0)

      endianness = 1 if voxels.dtype.byteorder == ">" else 2
      image_size.astype(np.int16)

      ts = time.time()

      param['dtype']               = dtypeName
      param['dimension']           = image_size
      param['spacing']             = image_spacing
      param['name']                = 'MRSIM2 Image ' + str(k)
      param['numberOfComponents']  = 1
      param['endian']              = endianness
      param['matrix']              = rawMatrix
      param['attribute']           = {}
      param['binary']              = binary
      param['binaryOffset']        = binaryOffset
      param['timestamp']           = ts

      if self.signalManager:
        self.signalManager.emitSignal('sendImageIGTL', param)
