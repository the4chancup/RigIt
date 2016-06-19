import sys
import imp
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from RigLib.pes16crypto import EditFile


# Application information #TODO: do this correctly and in a more practical way
name = 'RigIt'
version = '0.4.1'
wiki = 'https://implyingrigged.info/wiki/RigIt'
repository = 'https://github.com/the4chancup/RigIt/'
welcomeText = '''WARNING: this tool is in its beta phase and may not work
correctly. Backup before editing and be careful!'''

if __name__ == '__main__':
    # Compile *.ui files (only if not run as a stand-alone)
    if (not hasattr(sys, "frozen") and not imp.is_frozen("__main__")):
        uic.compileUiDir('ui')

    # Prepare main window
    from modules.mainwindow import MainWindow # import after compilation
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.setWindowTitle(name + ' v' + version)

    # Prepare status bar
    versionString = '<a href=\'' + repository + '\'>' + 'v' + version + '</a>'
    versionLabel = QLabel(versionString)
    versionLabel.setOpenExternalLinks(True)
    mainWindow.statusbar.insertPermanentWidget(0, versionLabel)
    websiteLabel = QLabel('<a href=\'' + wiki + '\'>' + wiki + '</a>')
    websiteLabel.setOpenExternalLinks(True)
    mainWindow.statusbar.insertPermanentWidget(0, websiteLabel)
    decrypterText = '<a href="https://github.com/the4chancup/pes16decrypter">'
    decrypterText += 'pes16decrypter</a> status: '
    if (EditFile.crypterAvailable()):
        decrypterText += 'found'
    else:
        decrypterText += 'missing'
    pes16decrypterLabel = QLabel(decrypterText)
    mainWindow.statusbar.insertPermanentWidget(0, pes16decrypterLabel)
    mainWindow.statusbar.showMessage(welcomeText)

    # Add tabs and show main window #TODO: do this by searching the directory?
    from modules.players import PlayersWidget
    playersTab = PlayersWidget(mainWindow)
    mainWindow.mainTabs.addTab(playersTab, playersTab.windowTitle())
    from modules.batchplayerediting4cc import BatchPlayerEditing4ccWidget
    batchTab = BatchPlayerEditing4ccWidget(mainWindow)
    mainWindow.mainTabs.addTab(batchTab, batchTab.windowTitle())
    mainWindow.show()
    sys.exit(app.exec_())
