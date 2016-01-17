from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import inspect
from warnings import warn
from RigLib.pes16edit import *


class SignalSlotProxy(QObject): # TODO: disconnect/clean up methods
    _signals = {} #TODO: make sure _signals is not taken

    def __init__(self, subject=None):
        super().__init__() # needed for defining signals
        self._subject = subject #TODO: make sure _subject is not taken
        self._setupSignals()
    
    def setProxySubject(self, subject):
        self._subject = subject
        
    def getProxySubject(self):
        return self._subject
    
    @pyqtSlot(bool)
    @pyqtSlot(int)
    @pyqtSlot(float) # substitute for double #TODO: verify
    def _setAttrNumericalSlot(self, name, value):
        self.__setattr__(name, value)
    
    @pyqtSlot(str) # we need this for overloaded signals
    def _setAttrStringSlot(self, name, value):
        self.__setattr__(name, value)
    
    def __setattr__(self, name, value):
        if (name == '_subject' or name == '_signals'):
            super().__setattr__(name, value)
        else:
            if (self._subject != None):
                if getattr(self._subject, name, value) != value:
                    print('Setting ' + name + ' to', value)
                setattr(self._subject, name, value)
                if (getattr(self._subject, name, value) != value):
                    print('Value was not accepted as-is!')
                    print('New value:', getattr(self._subject, name, value))
                self.emitSignal(name)

    def __getattr__(self, name):
        if (name == '_subject' or name == '_signals'):
            return super().__getattr__(name)
        else:
            if (self._subject != None):
                return getattr(self._subject, name)
            
    def connectToNumericalAttribute(self, signal, attr):
        signal.connect(lambda v: self._setAttrNumericalSlot(attr, v))

    def connectToStringAttribute(self, signal, attr):
        signal.connect(lambda v: self._setAttrStringSlot(attr, v))
    
    def cleverConnect(self, widget, attr):
        parents = inspect.getmro(widget.__class__)
        if (QSpinBox in parents or QAbstractSlider in parents):
            self.connectToNumericalAttribute(widget.valueChanged, attr)
            slot = widget.setValue
        elif (QAbstractButton in parents):
            self.connectToNumericalAttribute(widget.toggled, attr)
            slot = widget.setChecked
        elif (QLineEdit in parents):
            self.connectToStringAttribute(widget.textChanged, attr)
            slot = widget.setText
        elif (QComboBox in parents):
            self.connectToNumericalAttribute(widget.currentIndexChanged, attr)
            slot = widget.setCurrentIndex
        elif (QDoubleSpinBox in parents):
            self.connectToNumericalAttribute(widget.clicked, attr)
            slot = widget.setValue
        else:
            raise LookupError('Could not find a known parent class')
            return
        try:
            self._signals[attr].connect(slot)
        except KeyError:
            warn('No defined signal for attribute ' + attr)
    
    def emitSignal(self, attr):
        if hasattr(self._signals[attr], 'emit'):
            self._signals[attr].emit(getattr(self._subject, attr))
        else:
            warn('Signal for ' + signal + ' seems to be unbound')
    
    def emitAllSignals(self):
        for signal in self._signals:
            if hasattr(self._signals[signal], 'emit'):
                self._signals[signal].emit(getattr(self._subject, signal))
            else:
                warn('Signal for ' + signal + ' seems to be unbound')


class SignalWrapper(QObject):
    _signal = None
    
    def __getattr__(self, name):
        if (name != '_signal'):
            return getattr(self._signal, name)
        else: #TODO: check if getattr triggers __getattr__
            return self._signal #if not, this is not needed


class AttributeSignal():
    _signalTypes = {}

    def __new__(self, signature): #TODO: verify that signature lists work, too
        if signature not in self._signalTypes:
            self._signalTypes[signature] = type(__name__ + str(signature),#TODO
            (SignalWrapper,), {'_signal': pyqtSignal(signature)}) #Python3 way?
        return self._signalTypes[signature]()

