import os
import subprocess
import pathlib


class EditFile:
    _DECRYPTER = 'pes16decrypter/decrypter'
    _ENCRYPTER = 'pes16decrypter/encrypter' 
    _TEMP_DIRECTORY = 'pes16decrypter/'
    _NAME_ENCRYPT_HEADER = 'encryptHeader.dat'
    _NAME_HEADER = 'header.dat'
    _NAME_DESCRIPTION = 'description.dat'
    _NAME_LOGO = 'logo.png'
    _NAME_DATA = 'data.dat'
    _NAME_VERSION = 'version.txt'
    
    def __init__(self, filename=None):
        if (filename != None):
            self.decryptEditFile(filename)
        else:
            self.encryptHeader = None
            self.header = None
            self.description = None
            self.logo = None
            self.data = None
            self.version = None
    
    @classmethod
    def crypterAvailable(cls):
        if (not pathlib.Path(cls._DECRYPTER).is_file()):
            if (not pathlib.Path(cls._DECRYPTER + '.exe').is_file()):
                return False
        if (not pathlib.Path(cls._ENCRYPTER).is_file()):
            if (not pathlib.Path(cls._ENCRYPTER + '.exe').is_file()):
                return False
        return True
    
    @classmethod
    def _cleanUp(cls):
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_ENCRYPT_HEADER)
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_HEADER)
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_DESCRIPTION)
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_LOGO)
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_DATA)
        os.remove(cls._TEMP_DIRECTORY + cls._NAME_VERSION)
        
    def fromEditFile(self, filename):
        subprocess.call([self._DECRYPTER, filename, self._TEMP_DIRECTORY])
        with open(self._TEMP_DIRECTORY + self._NAME_ENCRYPT_HEADER, 'rb') as f:
            self.encryptHeader = bytearray(f.read())
        with open(self._TEMP_DIRECTORY + self._NAME_HEADER, 'rb') as f:
            self.header = bytearray(f.read())
        with open(self._TEMP_DIRECTORY + self._NAME_DESCRIPTION, 'rb') as f:
            self.description = bytearray(f.read())
        with open(self._TEMP_DIRECTORY + self._NAME_LOGO, 'rb') as f:
            self.logo = bytearray(f.read())
        with open(self._TEMP_DIRECTORY + self._NAME_DATA, 'rb') as f:
            self.data = bytearray(f.read())
        with open(self._TEMP_DIRECTORY + self._NAME_VERSION, 'rb') as f:
            self.version = bytearray(f.read())
        EditFile._cleanUp()
        
    def saveToEditFile(self, filename):
        with open(self._TEMP_DIRECTORY + self._NAME_ENCRYPT_HEADER, 'wb') as f:
            f.write(self.encryptHeader)
        with open(self._TEMP_DIRECTORY + self._NAME_HEADER, 'wb') as f:
            f.write(self.header)
        with open(self._TEMP_DIRECTORY + self._NAME_DESCRIPTION, 'wb') as f:
            f.write(self.description)
        with open(self._TEMP_DIRECTORY + self._NAME_LOGO, 'wb') as f:
            f.write(self.logo)
        with open(self._TEMP_DIRECTORY + self._NAME_DATA, 'wb') as f:
            f.write(self.data)
        with open(self._TEMP_DIRECTORY + self._NAME_VERSION, 'wb') as f:
            f.write(self.version)
        subprocess.call([self._ENCRYPTER, self._TEMP_DIRECTORY, filename])
        EditFile._cleanUp()

