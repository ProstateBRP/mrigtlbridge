
SignalNames = {
    # For IGTL GUI
    'consoleTextIGTL' : 'str',
    # For IGTL Listener
    'disconnectIGTL' : None,
    'sendImageIGTL'  : 'dict',
    
    # For MR GUI
    'consoleTextMR' : 'str',

    # Signals for listeners to notify GUI of its connection/thread status
    'listenerConnected' : None,
    'listenerDisconnected' : None,
    'listenerTerminated' : None,
    
    # For MR Listener
    'startSequence' : None,
    'stopSequence' : None,
    'updateScanPlane' : 'dict'
}
  
DataTypeTable = {
    'int8':    [2, 1],   #TYPE_INT8    = 2, 1 byte
    'uint8':   [3, 1],   #TYPE_UINT8   = 3, 1 byte
    'int16':   [4, 2],   #TYPE_INT16   = 4, 2 bytes
    'uint16':  [5, 2],   #TYPE_UINT16  = 5, 2 bytes
    'int32':   [6, 4],   #TYPE_INT32   = 6, 4 bytes
    'uint32':  [7, 4],   #TYPE_UINT32  = 7, 4 bytes
    'float32': [10,4],   #TYPE_FLOAT32 = 10, 4 bytes 
    'float64': [11,8],   #TYPE_FLOAT64 = 11, 8 bytes
}
    
  #
  #    # Image dimensions
  #    self.dimension = [0, 0, 0]
  #    self.spacing = [1.0, 1.0, 1.0]
  #    self.name = 'None'
  #    self.numberOfComponents = 1
  #    self.endian = 2 # 1: big; 2: little
  #    self.matrix = [[0.0,0.0,0.0,0.0],
  #                   [0.0,0.0,0.0,0.0],
  #                   [0.0,0.0,0.0,0.0],
  #                   [0.0,0.0,0.0,1.0]]
  #    
  #    self.attribute = {}
  #    self.binary
  #
