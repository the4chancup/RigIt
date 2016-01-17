from ui.Ui_batchplayerediting4cc import Ui_BatchPlayerEditing4cc
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from random import randint
from RigLib.pes16edit import *
from RigLib.pes16proxies import *
from RigLib.pes16enums import *
from RigLib.pyqthelperfunctions import *
from math import pow
import os


class BatchPlayerEditing4ccWidget(QWidget, Ui_BatchPlayerEditing4cc):
    _batchStats = []
    _batchStats.append('height')
    _batchStats.append('weight')
    _batchStats.append('attackingProwess')
    _batchStats.append('ballControl')
    _batchStats.append('dribbling')
    _batchStats.append('lowPass')
    _batchStats.append('loftedPass')
    _batchStats.append('finishing')
    _batchStats.append('placeKicking')
    _batchStats.append('swerve')
    _batchStats.append('header')
    _batchStats.append('defensiveProwess')
    _batchStats.append('ballWinning')
    _batchStats.append('kickingPower')
    _batchStats.append('speed')
    _batchStats.append('explosivePower')
    _batchStats.append('bodyBalance')
    _batchStats.append('jump')
    _batchStats.append('stamina')
    _batchStats.append('goalkeeping')
    _batchStats.append('catching')
    _batchStats.append('clearing')
    _batchStats.append('reflexes')
    _batchStats.append('coverage')
    _batchStats.append('weakFootUsage')
    _batchStats.append('weakFootAccuracy')
    _batchStats.append('form')
    _batchStats.append('injuryResistance')
    _APPLY_MEDAL_STATS_INFO = '''Done.
Don't forget to save but keep the unchanged Edit file!''' #TODO

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btnApplyMedalStats.setEnabled(False)
        
        self._editData = None
        self.playerEntryProxyBronze = PlayerEntryProxy(PlayerEntry())
        self.playerEntryProxySilver = PlayerEntryProxy(PlayerEntry())
        self.playerEntryProxyGold = PlayerEntryProxy(PlayerEntry())
          
        # Connect to load/save menu
        self.parent().loadedEditData.connect(self.loadEditData)
        
        # Connect signals to slots
        self.btnApplyMedalStats.clicked.connect(self.applyMedalStats)
        self._fillMedalBox(self.boxBronze, self.playerEntryProxyBronze)
        self._fillMedalBox(self.boxSilver, self.playerEntryProxySilver)
        self._fillMedalBox(self.boxGold, self.playerEntryProxyGold)
    
    def _fillMedalBox(self, box, player):
        layout = QFormLayout(box)
        layout.setVerticalSpacing(1)
        checkAll = QCheckBox(box) #TODO: breaks the tab order
        checkAll.setText('All')
        spinAll = QSpinBox(box) #TODO: breaks the tab order
        spinAll.setRange(0, 999)
        for stat in self._batchStats:
            checkBox = QCheckBox(box)
            checkBox.setText(stat) # TODO: pull the name from somewhere
            checkBox.playerAttribute = stat
            spinBox = QSpinBox(box)
            spinBox.setRange(PlayerEntry._attributes[stat][1],
            pow(2, PlayerEntry._attributes[stat][0]) +
            PlayerEntry._attributes[stat][1] - 1)
            layout.addRow(checkBox, spinBox)
            player.cleverConnect(spinBox, stat)
            checkAll.toggled.connect(checkBox.setChecked)
            spinAll.valueChanged.connect(spinBox.setValue)
        layout.addRow(checkAll, spinAll)
        box.setLayout(layout)
    
    @pyqtSlot()
    def applyMedalStats(self):
        for i in self._editData.playerEntries:
            player = self._editData.playerEntries[i] #TODO: move to for line
            medal = BatchPlayerEditing4ccWidget.determineMedalStatus(player)
            if (medal == 'bronze'):
                self.changePlayerStats(player, self.playerEntryProxyBronze,
                self.boxBronze)
            elif (medal == 'silver'):
                self.changePlayerStats(player, self.playerEntryProxySilver,
                self.boxSilver)
            elif (medal == 'gold'):
                self.changePlayerStats(player, self.playerEntryProxyGold,
                self.boxGold)
        QMessageBox.information(None, 'RigIt', self._APPLY_MEDAL_STATS_INFO)
    
    def changePlayerStats(self, player, basePlayer, box):
        for checkBox in box.findChildren(QCheckBox):
            if (checkBox.isChecked()):
                if (hasattr(checkBox, 'playerAttribute')):
                    setattr(player, checkBox.playerAttribute,
                    getattr(basePlayer, checkBox.playerAttribute))
        player.editedCreatedPlayer = True
    
    @classmethod
    def determineMedalStatus(cls, player): #TODO: put it somewhere else?
        if (player.stamina == 77):
            return 'bronze'
        elif (player.stamina == 88):
            return 'silver'
        elif (player.stamina == 99):
            return'gold'
        else:
            return 'none'
    
    @pyqtSlot(EditData)
    def loadEditData(self, editData):
        self._editData = editData
        self.btnApplyMedalStats.setEnabled(True)
    
