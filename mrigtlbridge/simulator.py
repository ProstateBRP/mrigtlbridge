import os, time, json, sys

from PyQt5 import QtCore, QtGui, QtWidgets

from . import igtl_widget
from . import mrsim_widget
from . import mr_igtl_bridge_window
from . import signal_manager
 
def main():
  
  app = QtWidgets.QApplication(sys.argv)

  app.setStyle("Fusion")

  dark_palette = QtGui.QPalette()

  dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
  dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
  dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
  dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
  dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
  dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
  dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
  dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
  dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
  dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
  dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
  dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
  dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
  dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
  dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)  

  app.setPalette(dark_palette)
  app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

  leftWidget = igtl_widget.IGTLWidget()
  rightWidget = mrsim_widget.MRSIMWidget()

  # Register slots
  sigManager = signal_manager.SignalManager()
  leftWidget.setSignalManager(sigManager)
  rightWidget.setSignalManager(sigManager)

  # Add widgets to the main window
  window = mr_igtl_bridge_window.MainWindow()
  window.setLeftWidget(leftWidget)
  window.setRightWidget(rightWidget)
  window.setTitle("OpenIGTLink MR Bridge")
  window.setup()
  
  window.resize(720, 480)
  window.show()
  sys.exit(app.exec_())    


if __name__ == "__main__":
  sys.exit(main())
