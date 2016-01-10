from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir
from RigLib.pes16enums import GameDataEnum


def _createQIconFromColor(color, width=24, height=12):
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)

def fillQComboBox(comboBox, data):
    if hasattr(data, '__bases__'):
        if GameDataEnum in data.__bases__:
            for _, member in data.__members__.items():
                if (member.data != None):
                    icon = _createQIconFromColor(member.data)
                    comboBox.addItem(icon, member.description)
                else:
                    comboBox.addItem(member.description)
            return
    raise TypeError('%s or its parents is not supported' % type(data))

def getOpenFileName(parent=None, dir=None, filter=None, caption=None):
    if (dir == None):
        dir = QDir.currentPath()
    if (filter == None):
        filter = 'File (*.*)'
    filename = QFileDialog.getOpenFileName(parent, caption, dir, filter)
    if (filename == ('', '')): # two null strings for cancel
        return None
    return filename[0]

def getSaveFileName(parent=None, dir=None, filter=None, caption=None):
    if (dir == None):
        dir = QDir.currentPath()
    if (filter == None):
        filter = 'File (*)'
    filename = QFileDialog.getSaveFileName(parent, caption, dir, filter)
    if (filename == ('', '')): # two null strings for cancel
        return None
    return filename[0]
