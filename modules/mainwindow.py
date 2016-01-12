from ui.Ui_mainwindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from RigLib.pyqthelperfunctions import *
from RigLib.pes16edit import *
from RigLib.pes16crypto import EditFile
import os


class MainWindow(QMainWindow, Ui_MainWindow):
    loadedEditData = pyqtSignal(EditData)
    savedEditFile = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('img/cloverball.png'))
        
        editDir = QDir.homePath()
        editDir += '/documents/KONAMI/Pro Evolution Soccer 2016/save'
        if (os.path.isdir(editDir)):
            self._directory = editDir
        else:
            self._directory = QDir.currentPath()
        self._editFile = EditFile()
        self._editData = None
       
        # Handle open/save buttons
        if (EditFile.crypterAvailable()):
            self.actionOpen_Edit_File.setEnabled(True)
        else:
            self.actionOpen_Edit_File.setEnabled(False)
        self.actionSave_As_Edit_File.setEnabled(False)
        self.actionOpen_Edit_data.setEnabled(True)
        self.actionSave_As_Edit_data.setEnabled(False)
        
        self.actionOpen_Edit_File.triggered.connect(lambda:
        self.openEdit(False))
        self.actionSave_As_Edit_File.triggered.connect(lambda:
        self.saveEdit(False))
        self.actionOpen_Edit_data.triggered.connect(lambda:
        self.openEdit(True))
        self.actionSave_As_Edit_data.triggered.connect(lambda:
        self.saveEdit(True))
        self.actionExit.triggered.connect(self.close)
        
    @pyqtSlot(bool, str)
    def openEdit(self, dataOnly, filename=None):
        if (self._editData != None):
            QMessageBox.warning(None, 'Warning',
            'You will lose any unsaved changes!')
        
        # Get open filename if needed
        if (filename == None):
            if (dataOnly):
                filter = 'Edit data file (*.dat *)'
            else:
                filter = 'Edit file (*)'
            filename = getOpenFileName(self, self._directory, filter)
        if (filename == None):
            return
        
        # Parse data
        if (dataOnly):
            # Read input file #TODO: move outside of block with proper cryptor
            try:
                with open(filename, 'rb') as f:
                    data = bytearray(f.read())
            except FileNotFoundError:
                QMessageBox.critical(None, 'Error', 'File not found!')
                return False
            self._editData = EditData(data) #TODO: needs error handling
        else: #TODO: needs error handling
            self._editFile.fromEditFile(filename)
            self._editData = EditData(self._editFile.data) 
            self.actionSave_As_Edit_File.setEnabled(True) # we got an edit file
        self._directory = os.path.dirname(filename)

        # Update GUI
        self.actionSave_As_Edit_data.setEnabled(True)
        self.loadedEditData.emit(self._editData)
        self.statusbar.showMessage('Loaded ' + os.path.basename(filename) +
        ' successfully.')

    @pyqtSlot(bool, str)
    def saveEdit(self, dataOnly, filename=None):
        # Get save filename if needed
        if (filename == None):
            if (dataOnly):
                filter = 'Edit data file (*.dat *)'
            else:
                filter = 'Edit file (*)'
            filename = getSaveFileName(self, self._directory, filter)
        if (filename == None):
            return
        
        # Write to file #TODO: error handling
        if (dataOnly):
            with open(filename, 'wb') as f:
                f.write(self._editData.toBytearray())
        else:
            self._editFile.data = self._editData.toBytearray()
            self._editFile.saveToEditFile(filename)
        self._directory = os.path.dirname(filename)
        self.savedEditFile.emit()
        self.statusbar.showMessage('Saved ' + os.path.basename(filename) +
        ' successfully.')

