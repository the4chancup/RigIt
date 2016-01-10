import sys
import imp
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *


# Application information #TODO: do this correctly and in a more practical way
name = 'RigIt'
version = '0.1.0'
wiki = 'https://implyingrigged.info/wiki/RigIt'
repository = 'https://github.com/the4chancup/RigIt/'
welcomeText = '''WARNING: this tool is in its beta phase and may not work
correctly. Backup before editing and be careful!'''

if __name__ == '__main__':
    # Compile *.ui files (only if not run as a stand-alone)
    if (not hasattr(sys, "frozen") and not imp.is_frozen("__main__")):
        uic.compileUiDir('ui')

    # Prepare main window
    app = QApplication(sys.argv)
    from ui.Ui_mainwindow import Ui_MainWindow
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.setWindowIcon(QIcon('img/cloverball.png'))
    mainWindow.setWindowTitle(name + ' v' + version)

    # Prepare status bar
    versionString = '<a href=\'' + repository + '\'>' + 'v' + version + '</a>'
    versionLabel = QLabel(versionString)
    versionLabel.setOpenExternalLinks(True)
    ui.statusbar.insertPermanentWidget(0, versionLabel)
    websiteLabel = QLabel('<a href=\'' + wiki + '\'>' + wiki + '</a>')
    websiteLabel.setOpenExternalLinks(True)
    ui.statusbar.insertPermanentWidget(0, websiteLabel)
    ui.statusbar.showMessage(welcomeText)

    # Add tabs and show main window #TODO: do this by searching the directory?
    from modules.players import PlayersWidget
    playersTab = PlayersWidget()
    ui.mainTabs.addTab(playersTab, playersTab.windowTitle())
    mainWindow.show()
    sys.exit(app.exec_())
