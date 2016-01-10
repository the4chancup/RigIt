# py2exe setup file
# Running this file under Windows creates a stand-alone executable
# 
# Run with the following command:
# python setup.py py2exe
# 
# If you get an error in file .../PyQt5/uic/port_v2/load_plugin.py in line 38
# replace:
#     except Exception, e:
# with:
#     except Exception as e:
#
# Note: building the .exe requires all libraries to be installed as well as
# some additional files that might not be in the repository.
#


from distutils.core import setup
import py2exe
import os
import PyQt5.uic
import rigit


_addPlatformsDll = True
_addPes16Decrypter = True

PyQt5.uic.compileUiDir('ui')

_zip = 'rigitlib.zip'
_dir = 'RigIt_v' + str(rigit.version)
_bundle_files = 1
_compressed = 1
_files = [('img', ['img/cloverball.png'])]
if (_addPlatformsDll):
    import PyQt5
    platformsPath = os.path.dirname(PyQt5.__file__)
    platformsPath += '\\plugins\\platforms\\qwindows.dll'
    _files.append(('platforms', [platformsPath]))
if (_addPes16Decrypter):
    crypterFiles = []
    crypterFiles.append('pes16decrypter/encrypter.exe')
    crypterFiles.append('pes16decrypter/decrypter.exe')
    crypterFiles.append('pes16decrypter/LICENSE.txt')
    crypterFiles.append('pes16decrypter/README.md')
    _files.append(('pes16decrypter', crypterFiles))
_windows = [{'script':'rigit.py',
'icon_resources': [(1, 'img/cloverball.ico')]}]
_options = {'py2exe':{'includes':['sip'], 'bundle_files':_bundle_files,
'dist_dir':_dir, 'compressed':_compressed}}

setup(zipfile=_zip, data_files = _files, windows=_windows, options=_options)
