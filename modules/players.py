from ui.Ui_players import Ui_PlayersWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from random import randint
from RigLib.pes16edit import *
from RigLib.pes16proxies import *
from RigLib.pes16enums import *
from RigLib.pyqthelperfunctions import *
import os


class PlayersListWidgetItem(QListWidgetItem):
    def __init__(self, playerEntry=None):
        super().__init__()
        self.playerEntry = playerEntry


class PlayersWidget(QWidget, Ui_PlayersWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setPlayerEntryFieldsEnabled(False)
        
        self._editData = None
        self.playerEntryProxy = PlayerEntryProxy()
        self.appearanceEntryProxy = AppearanceEntryProxy()
        
        # 4CC related variables
        self.cardLimit = 0
        self.medalType = 'bronze'
        
        # Connect to load/save menu
        self.parent().loadedEditData.connect(self.loadEditData)
        
        # Fill comboboxes
        fillQComboBox(self.cbxStrongerFoot, StrongerFoot)
        fillQComboBox(self.cbxPlayingStyle, PlayingStyle)
        fillQComboBox(self.cbxRegisteredPosition, RegisteredPosition)
        fillQComboBox(self.cbxSkinColor, SkinColor)
        fillQComboBox(self.cbxSpectacles, Spectacles)
        fillQComboBox(self.cbxSpectaclesFrameColor, SpectaclesFrameColor)
        fillQComboBox(self.cbxIrisColor, IrisColor)
        
        # Connect signals to slots
        self.lstPlayerEntries.currentItemChanged.connect(self.loadPlayerEntry)
        self.btnMakeGoldPlayer.clicked.connect(lambda:
        self.makeMedalPlayer('gold'))
        self.btnMakeSilverPlayer.clicked.connect(lambda:
        self.makeMedalPlayer('silver'))
        self.btnMakeBronzePlayer.clicked.connect(lambda:
        self.makeMedalPlayer('bronze'))
        self.spxPlayerId.valueChanged.connect(self.setPlayerIdHex)
        self.ldtPlayerName.textChanged.connect(self._updateListWidgetText) 
        self.btnCommentaryNone.clicked.connect(self.setCommentaryToNone)
        self.btnMotionRandomize.clicked.connect(self.randomizeMotions)
        for child in self.boxPlayerSkills.findChildren(QCheckBox):
            child.clicked.connect(lambda checked:
            self.changeValueByOne(self.spxRemainingPlayerSkills, checked))
            child.clicked.connect(lambda checked:
            self.changeValueByOne(self.spxRemainingCards, checked))    
        for child in self.boxComPlayingStyles.findChildren(QCheckBox):
            child.clicked.connect(lambda checked:
            self.changeValueByOne(self.spxRemainingComPlayingStyles, checked))
            child.clicked.connect(lambda checked:
            self.changeValueByOne(self.spxRemainingCards, checked))
        self._wireUpPlayerEntryProxy()
        self._wireUpAppearanceEntryProxy()
    
    def _wireUpPlayerEntryProxy(self):
        proxy = self.playerEntryProxy
        proxy.cleverConnect(self.chbEditedCreatedPlayer, 'editedCreatedPlayer')
        proxy.cleverConnect(self.spxPlayerId, 'playerId')
        proxy.cleverConnect(self.ldtPlayerName, 'playerName')
        proxy.cleverConnect(self.ldtPrintName, 'printName')
        proxy.cleverConnect(self.spxCommentaryId, 'commentaryName')
        proxy.cleverConnect(self.spxNationalityRegion, 'nationalityRegion')
        proxy.cleverConnect(self.spxAge, 'age')
        proxy.cleverConnect(self.cbxStrongerFoot, 'strongerFootMenuId')
        proxy.cleverConnect(self.cbxRegisteredPosition, 'registeredPositionMenuId')
        proxy.cleverConnect(self.cbxPlayingStyle, 'playingStyleMenuId')
        proxy.cleverConnect(self.spxHeight, 'height')
        proxy.cleverConnect(self.spxWeight, 'weight')
        proxy.cleverConnect(self.spxUnknownA, 'unknownA')
        proxy.cleverConnect(self.spxUnknownC, 'unknownC')
        proxy.cleverConnect(self.chbUnknownD, 'unknownD')
        proxy.cleverConnect(self.chbUnknownE, 'unknownE')
        proxy.cleverConnect(self.chbUnknownF, 'unknownF')
        proxy.cleverConnect(self.spxUnknownG, 'unknownG')
        proxy.cleverConnect(self.chbUnknownH, 'unknownH')
        proxy.cleverConnect(self.spxUnknownI, 'unknownI')
        proxy.cleverConnect(self.sldCentreForward, 'centreForward')
        proxy.cleverConnect(self.sldSecondStriker, 'secondStriker')
        proxy.cleverConnect(self.sldLeftWingForward, 'leftWingForward')
        proxy.cleverConnect(self.sldRightWingForward, 'rightWingForward')
        proxy.cleverConnect(self.sldAttackingMidfielder, 'attackingMidfielder')
        proxy.cleverConnect(self.sldLeftMidfielder, 'leftMidfielder')
        proxy.cleverConnect(self.sldRightMidfielder, 'rightMidfielder')
        proxy.cleverConnect(self.sldCentreMidfielder, 'centreMidfielder')
        proxy.cleverConnect(self.sldDefensiveMidfielder, 'defensiveMidfielder')
        proxy.cleverConnect(self.sldLeftBack, 'leftBack')
        proxy.cleverConnect(self.sldRightBack, 'rightBack')
        proxy.cleverConnect(self.sldCentreBack, 'centreBack')
        proxy.cleverConnect(self.sldGoalkeeper, 'goalkeeper')
        proxy.cleverConnect(self.spxMotionHunchingDribbling,
        'motionHunchingDribbling')
        proxy.cleverConnect(self.spxMotionArmMovementDribbling,
        'motionArmMovementDribbling')
        proxy.cleverConnect(self.spxMotionHunchingRunning,
        'motionHunchingRunning')
        proxy.cleverConnect(self.spxMotionArmMovementRunning,
        'motionArmMovementRunning')
        proxy.cleverConnect(self.spxMotionCornerKick, 'motionCornerKick')
        proxy.cleverConnect(self.spxMotionFreeKick, 'motionFreeKick')
        proxy.cleverConnect(self.spxMotionPenaltyKick, 'motionPenaltyKick')
        proxy.cleverConnect(self.spxMotionGoalCelebration1,
        'motionGoalCelebration1')
        proxy.cleverConnect(self.spxMotionGoalCelebration2,
        'motionGoalCelebration2')
        proxy.cleverConnect(self.chbTrickster, 'cpsTrickster')
        proxy.cleverConnect(self.chbMazingRun, 'cpsMazingRun')
        proxy.cleverConnect(self.chbSpeedingBullet, 'cpsSpeedingBullet')
        proxy.cleverConnect(self.chbIncisiveRun, 'cpsIncisiveRun')
        proxy.cleverConnect(self.chbLongBallExpert, 'cpsLongBallExpert')
        proxy.cleverConnect(self.chbEarlyCross, 'cpsEarlyCross')
        proxy.cleverConnect(self.chbLongRanger, 'cpsLongRanger')
        proxy.cleverConnect(self.chbScissorsFeint, 'skillScissorsFeint')
        proxy.cleverConnect(self.chbMarseilleTurn, 'skillMarseilleTurn')
        proxy.cleverConnect(self.chbFlipFlap, 'skillFlipFlap')
        proxy.cleverConnect(self.chbSombrero, 'skillSombrero')
        proxy.cleverConnect(self.chbCutBehindAndTurn, 'skillCutBehindAndTurn')
        proxy.cleverConnect(self.chbScotchMove, 'skillScotchMove')
        proxy.cleverConnect(self.chbHeading, 'skillHeading')
        proxy.cleverConnect(self.chbLongRangeDrive, 'skillLongRangeDrive')
        proxy.cleverConnect(self.chbKnuckleShot, 'skillKnuckleShot')
        proxy.cleverConnect(self.chbAcrobaticFinishing,
        'skillAcrobaticFinishing')
        proxy.cleverConnect(self.chbHeelTrick, 'skillHeelTrick')
        proxy.cleverConnect(self.chbFirstTimeShot, 'skillFirstTimeShot')
        proxy.cleverConnect(self.chbOneTouchPass, 'skillOneTouchPass')
        proxy.cleverConnect(self.chbWeightedPass, 'skillWeightedPass')
        proxy.cleverConnect(self.chbPinpointCrossing, 'skillPinpointCrossing')
        proxy.cleverConnect(self.chbOutsideCurler, 'skillOutsideCurler')
        proxy.cleverConnect(self.chbRabona, 'skillRabona')
        proxy.cleverConnect(self.chbLowLoftedPass, 'skillLowLoftedPass')
        proxy.cleverConnect(self.chbLowPuntTrajectory,
        'skillLowPuntTrajectory')
        proxy.cleverConnect(self.chbLongThrow, 'skillLongThrow')
        proxy.cleverConnect(self.chbGkLongThrow, 'skillGkLongThrow')
        proxy.cleverConnect(self.chbMalicia, 'skillMalicia')
        proxy.cleverConnect(self.chbManMarking, 'skillManMarking')
        proxy.cleverConnect(self.chbTrackback, 'skillTrackback')
        proxy.cleverConnect(self.chbAcrobaticClear, 'skillAcrobaticClear')
        proxy.cleverConnect(self.chbCaptaincy, 'skillCaptaincy')
        proxy.cleverConnect(self.chbSuperSub, 'skillSuperSub')
        proxy.cleverConnect(self.chbFightingSpirit, 'skillFightingSpirit')
        proxy.cleverConnect(self.spxAttackingProwess, 'attackingProwess')
        proxy.cleverConnect(self.spxBallControl, 'ballControl')
        proxy.cleverConnect(self.spxDribbling, 'dribbling')
        proxy.cleverConnect(self.spxLowPass, 'lowPass')
        proxy.cleverConnect(self.spxLoftedPass, 'loftedPass')
        proxy.cleverConnect(self.spxFinishing, 'finishing')
        proxy.cleverConnect(self.spxPlaceKicking, 'placeKicking')
        proxy.cleverConnect(self.spxSwerve, 'swerve')
        proxy.cleverConnect(self.spxHeader, 'header')
        proxy.cleverConnect(self.spxDefensiveProwess, 'defensiveProwess')
        proxy.cleverConnect(self.spxBallWinning, 'ballWinning')
        proxy.cleverConnect(self.spxKickingPower, 'kickingPower')
        proxy.cleverConnect(self.spxSpeed, 'speed')
        proxy.cleverConnect(self.spxExplosivePower, 'explosivePower')
        proxy.cleverConnect(self.spxBodyBalance, 'bodyBalance')
        proxy.cleverConnect(self.spxJump, 'jump')
        proxy.cleverConnect(self.spxStamina, 'stamina')
        proxy.cleverConnect(self.spxGoalkeeping, 'goalkeeping')
        proxy.cleverConnect(self.spxCatching, 'catching')
        proxy.cleverConnect(self.spxClearing, 'clearing')
        proxy.cleverConnect(self.spxReflexes, 'reflexes')
        proxy.cleverConnect(self.spxCoverage, 'coverage')
        proxy.cleverConnect(self.spxWeakFootUsage, 'weakFootUsage')
        proxy.cleverConnect(self.spxWeakFootAccuracy, 'weakFootAccuracy')
        proxy.cleverConnect(self.spxForm, 'form')
        proxy.cleverConnect(self.spxInjuryResistance, 'injuryResistance')
    
    def _wireUpAppearanceEntryProxy(self):
        proxy = self.appearanceEntryProxy
        proxy.cleverConnect(self.chbEditedFaceSettings, 'editedFaceSettings')
        proxy.cleverConnect(self.chbEditedHairstyleSettings,
        'editedHairstyleSettings')
        proxy.cleverConnect(self.chbEditedPhysiqueSettings,
        'editedPhysiqueSettings')
        proxy.cleverConnect(self.chbEditedStripStyleSettings,
        'editedStripStyleSettings')
        proxy.cleverConnect(self.spxBootsId, 'boots')
        proxy.cleverConnect(self.spxGoalkeeperGlovesId, 'goalkeeperGloves')
        proxy.cleverConnect(self.cbxSpectaclesFrameColor,
        'spectaclesFrameColorMenuId')
        proxy.cleverConnect(self.cbxSpectacles, 'spectaclesMenuId')
        proxy.cleverConnect(self.cbxSkinColor, 'skinColorMenuId')
        proxy.cleverConnect(self.cbxIrisColor, 'irisColorMenuId')
        
    def _setPlayerEntryFieldsEnabled(self, enable):
        self.boxPlayers.setEnabled(enable)
        self.box4CC.setEnabled(enable)
        self.boxBasic.setEnabled(enable)
        self.boxUnknown.setEnabled(enable)
        self.boxPlayablePosition.setEnabled(enable)
        self.boxComPlayingStyles.setEnabled(enable)
        self.boxMotion.setEnabled(enable)
        self.boxPlayerSkills.setEnabled(enable)
        self.boxAbility.setEnabled(enable)
        self.boxAppearanceLimited.setEnabled(enable)
     
    @pyqtSlot(QObject, QObject)
    def loadPlayerEntry(self, current, previous):
        self.playerEntryProxy.setProxySubject(None)
        self.appearanceEntryProxy.setProxySubject(None)
        if (current != None):
            self.playerEntryProxy.setProxySubject(current.playerEntry)
            try:
                appearanceEntry = self._editData.findAppearanceEntryById(
            current.playerEntry.playerId)
            except KeyError:
                QMessageBox.critical(None, 'Error', 'Player has no ' +
                'appearance entry.\n\nChanges made to the appearance will ' + 
                'not be saved. Please create a custom face in-game first.')
                appearanceEntry = AppearanceEntry()
                
            self.appearanceEntryProxy.setProxySubject(appearanceEntry)
            self.determineMedalStatus()
            self.spxRemainingCards.setValue(self.cardLimit)
            self.spxRemainingPlayerSkills.setValue(10) #TODO: pull from db
            self.spxRemainingComPlayingStyles.setValue(5) #TODO: pull from db
            self.playerEntryProxy.emitAllSignals()
            self.appearanceEntryProxy.emitAllSignals()
            for child in self.boxComPlayingStyles.findChildren(QCheckBox):
                if (child.isChecked()):
                    self.spxRemainingComPlayingStyles.setValue(
                    self.spxRemainingComPlayingStyles.value() - 1)
                    self.spxRemainingCards.setValue(
                    self.spxRemainingCards.value() - 1)
            for child in self.boxPlayerSkills.findChildren(QCheckBox):
                if (child.isChecked()):
                    self.spxRemainingPlayerSkills.setValue(
                    self.spxRemainingPlayerSkills.value() - 1)
                    self.spxRemainingCards.setValue(
                    self.spxRemainingCards.value() - 1)
            print('The player was determined to be a ' + self.medalType +
            ' medal')
    
    def determineMedalStatus(self): #TODO: improve
        if (self.playerEntryProxy.ballControl <= 77):
            self.medalType = 'bronze'
            if (self.playerEntryProxy.registeredPosition !=
            RegisteredPosition.GK):
                self.cardLimit = 2
            else:
                self.cardLimit = 1
        elif (self.playerEntryProxy.ballControl <= 88):
            self.medalType = 'silver'
            self.cardLimit = 3
        else:
            self.medalType = 'gold'
            self.cardLimit = 4
    
    @pyqtSlot(int)
    def setPlayerIdHex(self, value): #TODO: this is pretty dirty
        le = (value & 0x000000FF) << 24
        le += (value & 0x0000FF00) << 8
        le += (value & 0x00FF0000) >> 8
        le += (value & 0xFF000000) >> 24
        self.spxPlayerIdHex.setValue(-1)
        self.spxPlayerIdHex.setSpecialValueText('0x' + hex(le)[2:].upper())
    
    @pyqtSlot(EditData)
    def loadEditData(self, editData):
        self._editData = editData
        self.lstPlayerEntries.clear() #TODO: delete old QListWidgetItems?
        for id in sorted(editData.playerEntries.keys()):
            item = PlayersListWidgetItem()
            item.playerEntry = editData.playerEntries[id]
            item.setText(item.playerEntry.playerName)
            self.lstPlayerEntries.addItem(item)
        self.lstPlayerEntries.setCurrentRow(0) # select first item
        self.spxPlayerCount.setValue(len(editData.playerEntries))
        self._setPlayerEntryFieldsEnabled(True)
    
    @pyqtSlot(str)
    def _updateListWidgetText(self, str):
        self.lstPlayerEntries.currentItem().setText(str)
    
    @pyqtSlot(str)    
    def makeMedalPlayer(self, medal):
        print('Make ' + medal.capitalize() + ' Medal player...')
        self.medalType = medal
        cards = self.spxRemainingCards.value() - self.cardLimit
        if (medal == 'gold'):
            stats = 99
            form = 8
            self.cardLimit = 4
        elif (medal == 'silver'):
            stats = 88
            form = 8
            self.cardLimit = 3
        elif (medal == 'bronze'):
            stats = 77
            form = 4
            if (self.playerEntryProxy.registeredPosition !=
                RegisteredPosition.GK):
                    self.cardLimit = 2
            else:
                self.cardLimit = 1
        self.spxRemainingCards.setValue(cards + self.cardLimit)
        if (self.spxHeight.value() < 180):
            self.spxWeakFootUsage.setValue(4)
            self.spxWeakFootAccuracy.setValue(4)
        else:
            self.spxWeakFootUsage.setValue(2)
            self.spxWeakFootAccuracy.setValue(2)
        self.spxBallControl.setValue(stats)
        self.spxDribbling.setValue(stats)
        self.spxLowPass.setValue(stats)
        self.spxLoftedPass.setValue(stats)
        self.spxFinishing.setValue(stats)
        self.spxPlaceKicking.setValue(stats)
        self.spxSwerve.setValue(stats)
        self.spxHeader.setValue(stats)
        self.spxBallWinning.setValue(stats)
        self.spxKickingPower.setValue(stats)
        self.spxSpeed.setValue(stats)
        self.spxExplosivePower.setValue(stats)
        self.spxBodyBalance.setValue(stats)
        self.spxJump.setValue(stats)
        self.spxStamina.setValue(stats)
        self.spxGoalkeeping.setValue(stats)
        self.spxCatching.setValue(stats)
        self.spxClearing.setValue(stats)
        self.spxReflexes.setValue(stats)
        self.spxCoverage.setValue(stats)
        self.spxForm.setValue(form)
        self.spxInjuryResistance.setValue(3)
        self.spxAttackingProwess.setValue(stats)
        self.spxDefensiveProwess.setValue(stats)
        QMessageBox.information(None, 'Note', 'Adjust Defensive/Attacking'
        + ' Prowess to your needs (neither must exceed ' + str(stats) + ').')

    @pyqtSlot(QObject, bool)
    def changeValueByOne(self, object, checked): #TODO: put somewhere else?
        if (checked):
            object.setValue(object.value() - 1)
        else:
            object.setValue(object.value() + 1)
    
    @pyqtSlot()
    def setCommentaryToNone(self):
        self.playerEntryProxy.commentaryName = -1 # equals 0xFFFFFFFF
    
    @pyqtSlot(str)
    def randomizeMotions(self): #TODO: pull these numbers from somewhere
        self.playerEntryProxy.motionHunchingDribbling = randint(1, 3)
        self.playerEntryProxy.motionArmMovementDribbling = randint(1, 8)
        self.playerEntryProxy.motionHunchingRunning = randint(1, 3)
        self.playerEntryProxy.motionArmMovementRunning = randint(1, 8)
        self.playerEntryProxy.motionCornerKick = randint(1, 6)
        self.playerEntryProxy.motionFreeKick = randint(1, 16)
        self.playerEntryProxy.motionPenaltyKick = randint(1, 4)
        self.playerEntryProxy.motionGoalCelebration1 = randint(1, 122)
        self.playerEntryProxy.motionGoalCelebration2 = randint(1, 122)

