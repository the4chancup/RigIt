import struct
from RigLib.pes16enums import *


class EditData:
    HEADER_LENGTH = 76
    PLAYER_ENTRY_LENGTH = 112
    APPEARANCE_ENTRY_LENGTH = 72
    TEAM_ENTRY_LENGTH = 456
    CHAMPIONSHIP_ENTRY_LENGTH = 92
    STADIUM_ENTRY_LENGTH  = 128
    UNIFORM_ENTRY_LENGTH  = 88 #TODO: needs confirmation
    TEAM_ROSTER_ENTRY_LENGTH  = 164
    LEAGUE_ROSTER_ENTRY_LENGTH  = 4
    TEAM_TACTICS_ENTRY_LENGTH  = 520
    PLAYER_ENTRY_COUNT = 25000
    APPEARANCE_ENTRY_COUNT = 25000
    TEAM_ENTRY_COUNT = 850
    CHAMPIONSHIP_ENTRY_COUNT = 100
    STADIUM_ENTRY_COUNT = 100
    UNIFORM_ENTRY_COUNT = 2500 #TODO: needs confirmation
    TEAM_ROSTER_ENTRY_COUNT = 850
    LEAGUE_ROSTER_ENTRY_COUNT = 712
    TEAM_TACTICS_ENTRY_COUNT = 850
    TRAILER = 0 #TODO: needs to be researched
    
    def __init__(self, data): #TODO: allow default values
        self.fromBytearray(data)

    def fromBytearray(self, data):
        #TODO: length check
        #TODO: turn everything into class or something else
        # Read header
        self._header = data[:self.HEADER_LENGTH]
        playerCount = struct.unpack("<H", data[52:54])[0]
        
        # Read player entries
        self.playerEntries = {} # dictionary to disallow duplicate IDs
        begin = self.HEADER_LENGTH
        end = begin + self.PLAYER_ENTRY_LENGTH * playerCount
        for pos in range(begin, end, self.PLAYER_ENTRY_LENGTH):
            d = data[pos:self.PLAYER_ENTRY_LENGTH + pos]
            playerEntry = PlayerEntry(d)
            self.playerEntries[playerEntry.playerId] = playerEntry

        # Read appearance entries
        self.appearanceEntries = {} # dictionary to disallow duplicate IDs
        begin += self.PLAYER_ENTRY_LENGTH * self.PLAYER_ENTRY_COUNT
        end = begin + self.APPEARANCE_ENTRY_LENGTH * playerCount
        for pos in range(begin, end, self.APPEARANCE_ENTRY_LENGTH):
            d = data[pos:self.APPEARANCE_ENTRY_LENGTH + pos]
            appearanceEntry = AppearanceEntry(d)
            self.appearanceEntries[appearanceEntry.player] = appearanceEntry
        
        # Read rest
        length = self.HEADER_LENGTH
        length += self.PLAYER_ENTRY_LENGTH * self.PLAYER_ENTRY_COUNT
        length += self.APPEARANCE_ENTRY_LENGTH * self.APPEARANCE_ENTRY_COUNT
        self._rest = data[length:]
        
    def toBytearray(self):
        # Add header
        result = self._header + b'' # make an actual copy
        
        # Add player entries
        for id in sorted(self.playerEntries.keys()):
            result += self.playerEntries[id].toBytearray()
        unusedEntries = (self.PLAYER_ENTRY_COUNT - len(self.playerEntries))
        result += self.PLAYER_ENTRY_LENGTH * unusedEntries * b'\0'
        
        # Add appearance entries
        for id in sorted(self.appearanceEntries.keys()):
            result += self.appearanceEntries[id].toBytearray()
        unusedEntries = (self.APPEARANCE_ENTRY_COUNT
        - len(self.appearanceEntries))
        result += self.APPEARANCE_ENTRY_LENGTH * unusedEntries * b'\0'
        
        # Add rest and return
        return result + self._rest
    
    def findPlayerEntryById(self, id):
        return self.playerEntries[id]
    
    def findPlayerEntriesByName(self, name, exact=False):
        results = []
        if (exact):
            for player in self.playerEntries:
                if (player.playerName == name):
                    results.append(player)
        else:
            for player in self.playerEntries:
                if (player.playerName.find(name) != -1):
                    results.append(player)
        return results
        
    def findPlayersByTeam(self, name):
        raise NotImplementedError('Method is not implemented yet')
    
    def getPlayerCount(self):
        return len(self.playerEntries)
    
    def updatePlayer(self, player, id=None):
        if (id == None):
            id = player.playerId
        
    def addPlayer(self, player=None):
        raise NotImplementedError('Method is not implemented yet')
    
    def deletePlayerById(self, id):
        raise NotImplementedError('Method is not implemented yet')
        
    def findAppearanceEntryById(self, id):
        return self.appearanceEntries[id]
        

class StoredDataStructure:
    _attributes = {}
    
    def __init__(self, data=None):
        if (data != None):
            self.fromBytearray(data)
        else:
            self.setDefaultValues()
    
    def __getattribute__(self, name):
        if (name == "_attributes" or not name in self._attributes):
            return object.__getattribute__(self, name) #TODO: super?
        else: #TODO: crashes if type can't handle value + integer
            if (self._attributes[name][1] != 0): #TODO: dirty hack
                return getattr(self, '_' + name) + self._attributes[name][1]
            else:
                return getattr(self, '_' + name)
    
    def __setattr__(self, name, value):
        if (name == "_attributes" or not name in self._attributes):
            object.__setattr__(self, name, value)
        else:
            newValue = value - self._attributes[name][1]
            if (self._attributes[name][0] == 32): #TODO: dirty hack for s int
                newValue = max(-0x7FFFFFFF, min(newValue, 0x7FFFFFFF - 1))
                setattr(self, '_' + name, newValue)
            else:
                mask = (1 << self._attributes[name][0]) - 1
                setattr(self, '_' + name, newValue & mask)
    
    def setDefaultValues(self): #TODO: add handlings for different types/None
        for name in self._attributes:
            setattr(self, '_' + name, self._attributes[name][2])
          
    def printAttributes(self):
        for name in sorted(self._attributes.keys()):
            print(name, getattr(self, name))

            
class PlayerEntry(StoredDataStructure):
    _struct = struct.Struct("<iiHHBBBBIIIIIBIHBQ46s16s")
    _attributes = {}
    _attributes['playerId'] = (32, 0, None)
    _attributes['commentaryName'] = (32, 0, -1)
    _attributes['unknownA'] = (16, 0, 0xFFFF)
    _attributes['nationalityRegion'] = (16, 0, 0x0401)
    _attributes['height'] = (8, 0, 180)
    _attributes['weight'] = (8, 0, 75)
    _attributes['motionGoalCelebration1'] = (8, 0, 0)
    _attributes['motionGoalCelebration2'] = (8, 0, 0)
    _attributes['attackingProwess'] = (7, 0, 80)
    _attributes['defensiveProwess'] = (7, 0, 80)
    _attributes['goalkeeping'] = (7, 0, 80)
    _attributes['dribbling'] = (7, 0, 80)
    _attributes['motionFreeKick'] = (4, 1, 0)
    _attributes['finishing'] = (7, 0, 80)
    _attributes['lowPass'] = (7, 0, 80)
    _attributes['loftedPass'] = (7, 0, 80)
    _attributes['header'] = (7, 0, 80)
    _attributes['form'] = (3, 1, 3)
    _attributes['editedCreatedPlayer'] = (1, 0, 1)
    _attributes['swerve'] = (7, 0, 80)
    _attributes['catching'] = (7, 0, 80)
    _attributes['clearing'] = (7, 0, 80)
    _attributes['reflexes'] = (7, 0, 80)
    _attributes['injuryResistance'] = (2, 1, 1)
    _attributes['unknownC'] = (2, 0, 0)
    _attributes['bodyBalance'] = (7, 0, 80)
    _attributes['kickingPower'] = (7, 0, 80)
    _attributes['explosivePower'] = (7, 0, 80)
    _attributes['jump'] = (7, 0, 80)
    _attributes['motionArmMovementDribbling'] = (3, 1, 0)
    _attributes['unknownD'] = (1, 0, 0)
    _attributes['unknownE'] = (1, 0, 0)
    _attributes['ballControl'] = (7, 0, 80)
    _attributes['ballWinning'] = (7, 0, 80)
    _attributes['coverage'] = (7, 0, 80)
    _attributes['unknownF'] = (1, 0, 0)
    _attributes['motionArmMovementRunning'] = (3, 1, 0)
    _attributes['motionCornerKick'] = (3, 1, 0)
    _attributes['weakFootAccuracy'] = (2, 1, 1)
    _attributes['weakFootUsage'] = (2, 1, 1)
    _attributes['centreForward'] = (2, 0, 0)
    _attributes['secondStriker'] = (2, 0, 0)
    _attributes['leftWingForward'] = (2, 0, 0)
    _attributes['rightWingForward'] = (2, 0, 0)
    _attributes['attackingMidfielder'] = (2, 0, 0)
    _attributes['defensiveMidfielder'] = (2, 0, 0)
    _attributes['centreMidfielder'] = (2, 0, 0)
    _attributes['leftMidfielder'] = (2, 0, 0)
    _attributes['rightMidfielder'] = (2, 0, 0)
    _attributes['centreBack'] = (2, 0, 0)
    _attributes['leftBack'] = (2, 0, 0)
    _attributes['rightBack'] = (2, 0, 0)
    _attributes['goalkeeper'] = (2, 0, 0)
    _attributes['motionHunchingDribbling'] = (2, 1, 0)
    _attributes['motionHunchingRunning'] = (2, 1, 0)
    _attributes['motionPenaltyKick'] = (2, 1, 0)
    _attributes['placeKicking'] = (7, 0, 80)
    _attributes['speed'] = (7, 0, 80)
    _attributes['age'] = (6, 0, 17)
    _attributes['unknownG'] = (2, 0, 0)
    _attributes['stamina'] = (7, 0, 80)
    _attributes['unknownH'] = (1, 0, 0)
    _attributes['unknownI'] = (4, 0, 0)
    _attributes['cpsTrickster'] = (1, 0, 0)
    _attributes['cpsMazingRun'] = (1, 0, 0)
    _attributes['cpsSpeedingBullet'] = (1, 0, 0)
    _attributes['cpsIncisiveRun'] = (1, 0, 0)
    _attributes['cpsLongBallExpert'] = (1, 0, 0)
    _attributes['cpsEarlyCross'] = (1, 0, 0)
    _attributes['cpsLongRanger'] = (1, 0, 0)
    _attributes['skillScissorsFeint'] = (1, 0, 0)
    _attributes['skillFlipFlap'] = (1, 0, 0)
    _attributes['skillMarseilleTurn'] = (1, 0, 0)
    _attributes['skillSombrero'] = (1, 0, 0)
    _attributes['skillCutBehindAndTurn'] = (1, 0, 0)
    _attributes['skillScotchMove'] = (1, 0, 0)
    _attributes['skillHeading'] = (1, 0, 0)
    _attributes['skillLongRangeDrive'] = (1, 0, 0)
    _attributes['skillKnuckleShot'] = (1, 0, 0)
    _attributes['skillAcrobaticFinishing'] = (1, 0, 0)
    _attributes['skillHeelTrick'] = (1, 0, 0)
    _attributes['skillFirstTimeShot'] = (1, 0, 0)
    _attributes['skillOneTouchPass'] = (1, 0, 0)
    _attributes['skillWeightedPass'] = (1, 0, 0)
    _attributes['skillPinpointCrossing'] = (1, 0, 0)
    _attributes['skillOutsideCurler'] = (1, 0, 0)
    _attributes['skillRabona'] = (1, 0, 0)
    _attributes['skillLowLoftedPass'] = (1, 0, 0)
    _attributes['skillLowPuntTrajectory'] = (1, 0, 0)
    _attributes['skillLongThrow'] = (1, 0, 0)
    _attributes['skillGkLongThrow'] = (1, 0, 0)
    _attributes['skillMalicia'] = (1, 0, 0)
    _attributes['skillManMarking'] = (1, 0, 0)
    _attributes['skillTrackback'] = (1, 0, 0)
    _attributes['skillAcrobaticClear'] = (1, 0, 0)
    _attributes['skillCaptaincy'] = (1, 0, 0)
    _attributes['skillSuperSub'] = (1, 0, 0)
    _attributes['skillFightingSpirit'] = (1, 0, 0)
    
    @property
    def playingStyle(self):
        return self._playingStyle
        
    @playingStyle.setter
    def playingStyle(self, value):
        self._playingStyle = value
    
    @property
    def playingStyleMenuId(self):
        return self._playingStyle.menuId
        
    @playingStyleMenuId.setter
    def playingStyleMenuId(self, value):
        self._playingStyle = PlayingStyle.fromMenuId(value)
    
    @property
    def registeredPosition(self):
        return self._registeredPosition
        
    @registeredPosition.setter
    def registeredPosition(self, value):
        self._registeredPosition = value
    
    @property
    def registeredPositionMenuId(self):
        return self._registeredPosition.menuId
        
    @registeredPositionMenuId.setter
    def registeredPositionMenuId(self, value):
        self._registeredPosition = RegisteredPosition.fromMenuId(value)
    
    @property
    def strongerFoot(self):
        return self._strongerFoot
    
    @strongerFoot.setter
    def strongerFoot(self, value):
        self._strongerFoot = value
    
    @property
    def strongerFootMenuId(self):
        return self._strongerFoot.menuId
    
    @strongerFootMenuId.setter
    def strongerFootMenuId(self, value):
        self._strongerFoot = StrongerFoot.fromMenuId(value)
    
    @property
    def playerName(self):
        return self._playerName
    
    @playerName.setter
    def playerName(self, value):
        self._playerName = value[:45]

    @property
    def printName(self):
        return self._printName
    
    @printName.setter
    def printName(self, value):
        self._printName = value[:15]
    
    def setDefaultValues(self):
        super().setDefaultValues()
        self._playerName = 'Placeholder'
        self._printName = ''
        self._playingStyle = PlayingStyle.NONE
        self._registeredPosition = RegisteredPosition.CF
        self._strongerFoot = StrongerFoot.RIGHT_FOOT

    def fromBytearray(self, data): #TODO: check size beforehand
        paddedData = data[:0x32] + bytearray([0]*2) + data[0x32:]
        data = self._struct.unpack(paddedData)
        
        self._playerId = data[0]
        self._commentaryName = data[1]
        self._unknownA = data[2]
        self._nationalityRegion = data[3]
        self._height = data[4]
        self._weight = data[5]
        self._motionGoalCelebration1 = data[6]
        self._motionGoalCelebration2 = data[7]
        self._attackingProwess = data[8] & 0b1111111
        self._defensiveProwess = data[8] >> 7 & 0b1111111
        self._goalkeeping = data[8] >> 14 & 0b1111111
        self._dribbling = data[8] >> 21 & 0b1111111
        self._motionFreeKick = data[8] >> 28 & 0b1111
        self._finishing = data[9] & 0b1111111
        self._lowPass = data[9] >> 7 & 0b1111111
        self._loftedPass = data[9] >> 14 & 0b1111111
        self._header = data[9] >> 21 & 0b1111111
        self._form = data[9] >> 28 & 0b111
        self._editedCreatedPlayer = data[9] >> 31 & 0b1
        self._swerve = data[10] & 0b1111111
        self._catching = data[10] >> 7 & 0b1111111
        self._clearing = data[10] >> 14 & 0b1111111
        self._reflexes = data[10] >> 21 & 0b1111111
        self._injuryResistance = data[10] >> 28 & 0b11
        self._unknownC = data[10] >> 30 & 0b11
        self._bodyBalance = data[11] & 0b1111111
        self._kickingPower = data[11] >> 7 & 0b1111111
        self._explosivePower = data[11] >> 14 & 0b1111111
        self._jump = data[11] >> 21 & 0b1111111
        self._motionArmMovementDribbling = data[11] >> 28 & 0b111
        self._unknownD = data[11] >> 31 & 0b1
        self._registeredPosition = RegisteredPosition.fromGameId(data[12]
        & 0b1111)
        self._unknownE = data[12] >> 4 & 0b1
        self._playingStyle = PlayingStyle.fromGameId(data[12] >> 5 & 0b11111)
        self._ballControl = data[12] >> 10 & 0b1111111
        self._ballWinning = data[12] >> 17 & 0b1111111
        self._coverage = data[12] >> 24 & 0b1111111
        self._unknownF = data[12] >> 31 & 0b1
        self._motionArmMovementRunning = data[13] & 0b111
        self._motionCornerKick = data[13] >> 3 & 0b111
        self._weakFootAccuracy = data[13] >> 6 & 0b11
        self._weakFootUsage = data[14] & 0b11
        playablePosition = data[14] >> 2 & 0x3FFFFFF
        self._centreForward = playablePosition & 3
        self._secondStriker = (playablePosition & 12) >> 2
        self._leftWingForward = (playablePosition & 48) >> 4
        self._rightWingForward = (playablePosition & 192) >> 6 
        self._attackingMidfielder = (playablePosition & 768) >> 8
        self._defensiveMidfielder = (playablePosition & 3072) >> 10
        self._centreMidfielder = (playablePosition & 12288) >> 12
        self._leftMidfielder = (playablePosition & 49152) >> 14
        self._rightMidfielder = (playablePosition & 196608) >> 16
        self._centreBack = (playablePosition & 786432) >> 18
        self._leftBack = (playablePosition & 3145728) >> 20
        self._rightBack = (playablePosition & 12582912) >> 22
        self._goalkeeper = (playablePosition & 50331648) >> 24
        self._motionHunchingDribbling = data[14] >> 28 & 0b11
        self._motionHunchingRunning = data[14] >> 30 & 0b11
        self._motionPenaltyKick = data[15] & 0b11
        self._placeKicking = data[15] >> 2 & 0b1111111
        self._speed = data[15] >> 9 & 0b1111111
        self._age = data[16] & 0b111111
        self._unknownG = data[16] >> 6 & 0b11
        self._stamina = data[17] & 0b1111111
        self._unknownH = data[17] >> 7 & 0b1
        self._unknownI = data[17] >> 8 & 0b1111
        self._strongerFoot = StrongerFoot.fromGameId(data[17] >> 12 & 0b1)
        comPlayingStyle = data[17] >> 13 & 0b1111111 #TODO: verify order
        self._cpsTrickster = comPlayingStyle & 1
        self._cpsMazingRun = (comPlayingStyle & 2) >> 1
        self._cpsSpeedingBullet = (comPlayingStyle & 4) >> 2
        self._cpsIncisiveRun = (comPlayingStyle & 8) >> 3
        self._cpsLongBallExpert = (comPlayingStyle & 16) >> 4
        self._cpsEarlyCross = (comPlayingStyle & 32) >> 5
        self._cpsLongRanger = (comPlayingStyle & 64) >> 6
        playerSkills = data[17] >> 20 & 0xFFFFFFF #TODO: verify order
        self._skillScissorsFeint = playerSkills & 1
        self._skillFlipFlap = (playerSkills & 2) >> 1
        self._skillMarseilleTurn = (playerSkills & 4) >> 2
        self._skillSombrero = (playerSkills & 8) >> 3
        self._skillCutBehindAndTurn = (playerSkills & 16) >> 4
        self._skillScotchMove = (playerSkills & 32) >> 5
        self._skillHeading = (playerSkills & 64) >> 6
        self._skillLongRangeDrive = (playerSkills & 128) >> 7
        self._skillKnuckleShot = (playerSkills & 256) >> 8
        self._skillAcrobaticFinishing = (playerSkills & 512) >> 9
        self._skillHeelTrick = (playerSkills & 1028) >> 10
        self._skillFirstTimeShot = (playerSkills & 2048) >> 11
        self._skillOneTouchPass = (playerSkills & 4096) >> 12
        self._skillWeightedPass = (playerSkills & 8192) >> 13
        self._skillPinpointCrossing = (playerSkills & 16384) >> 14
        self._skillOutsideCurler = (playerSkills & 32768) >> 15
        self._skillRabona = (playerSkills & 65536) >> 16
        self._skillLowLoftedPass = (playerSkills & 131072) >> 17
        self._skillLowPuntTrajectory = (playerSkills & 262144) >> 18
        self._skillLongThrow = (playerSkills & 524288) >> 19
        self._skillGkLongThrow = (playerSkills & 1048576) >> 20
        self._skillMalicia = (playerSkills & 2097152) >> 21
        self._skillManMarking = (playerSkills & 4194304) >> 22
        self._skillTrackback = (playerSkills & 8388608) >> 23
        self._skillAcrobaticClear = (playerSkills & 16777216) >> 24
        self._skillCaptaincy = (playerSkills & 33554432) >> 25
        self._skillSuperSub = (playerSkills & 67108864) >> 26
        self._skillFightingSpirit = (playerSkills & 134217728) >> 27
        self._playerName = data[18].decode('utf-8') #TODO: verify encoding
        self._printName = data[19].decode('utf-8') #TODO: verify encoding
        self._playerName = self._playerName[:self._playerName.find('\0')]
        self._printName = self._printName[:self._printName.find('\0')]
    
    def toBytearray(self):
        playablePosition = self._centreForward
        playablePosition |= self._secondStriker << 2
        playablePosition |= self._leftWingForward << 4
        playablePosition |= self._rightWingForward << 6
        playablePosition |= self._attackingMidfielder << 8
        playablePosition |= self._defensiveMidfielder << 10
        playablePosition |= self._centreMidfielder << 12
        playablePosition |= self._leftMidfielder << 14
        playablePosition |= self._rightMidfielder << 16
        playablePosition |= self._centreBack << 18
        playablePosition |= self._leftBack << 20
        playablePosition |= self._rightBack << 22
        playablePosition |= self._goalkeeper << 24
        comPlayingStyle = self._cpsTrickster #TODO: verify order
        comPlayingStyle |= self._cpsMazingRun << 1
        comPlayingStyle |= self._cpsSpeedingBullet << 2
        comPlayingStyle |= self._cpsIncisiveRun << 3
        comPlayingStyle |= self._cpsLongBallExpert << 4
        comPlayingStyle |= self._cpsEarlyCross << 5
        comPlayingStyle |= self._cpsLongRanger << 6
        playerSkills = self._skillScissorsFeint #TODO: verify order
        playerSkills |= self._skillFlipFlap << 1
        playerSkills |= self._skillMarseilleTurn << 2
        playerSkills |= self._skillSombrero << 3
        playerSkills |= self._skillCutBehindAndTurn << 4
        playerSkills |= self._skillScotchMove << 5
        playerSkills |= self._skillHeading << 6
        playerSkills |= self._skillLongRangeDrive << 7
        playerSkills |= self._skillKnuckleShot << 8
        playerSkills |= self._skillAcrobaticFinishing << 9
        playerSkills |= self._skillHeelTrick << 10
        playerSkills |= self._skillFirstTimeShot << 11
        playerSkills |= self._skillOneTouchPass << 12
        playerSkills |= self._skillWeightedPass << 13
        playerSkills |= self._skillPinpointCrossing << 14
        playerSkills |= self._skillOutsideCurler << 15
        playerSkills |= self._skillRabona << 16
        playerSkills |= self._skillLowLoftedPass << 17
        playerSkills |= self._skillLowPuntTrajectory << 18
        playerSkills |= self._skillLongThrow << 19
        playerSkills |= self._skillGkLongThrow << 20
        playerSkills |= self._skillMalicia << 21
        playerSkills |= self._skillManMarking << 22
        playerSkills |= self._skillTrackback << 23
        playerSkills |= self._skillAcrobaticClear << 24
        playerSkills |= self._skillCaptaincy << 25
        playerSkills |= self._skillSuperSub << 26
        playerSkills |= self._skillFightingSpirit << 27
        data = []
        data.append(self._playerId)
        data.append(self._commentaryName)
        data.append(self._unknownA)
        data.append(self._nationalityRegion)
        data.append(self._height)
        data.append(self._weight)
        data.append(self._motionGoalCelebration1)
        data.append(self._motionGoalCelebration2)
        value = self._attackingProwess
        value |= self._defensiveProwess << 7
        value |= self._goalkeeping << 14
        value |= self._dribbling << 21
        value |= self._motionFreeKick << 28
        data.append(value)
        value = self._finishing
        value |= self._lowPass << 7
        value |= self._loftedPass << 14
        value |= self._header << 21
        value |= self._form << 28
        value |= self._editedCreatedPlayer << 31
        data.append(value)
        value = self._swerve
        value |= self._catching << 7
        value |= self._clearing << 14
        value |= self._reflexes << 21
        value |= self._injuryResistance << 28
        value |= self._unknownC << 30
        data.append(value)
        value = self._bodyBalance
        value |= self._kickingPower << 7
        value |= self._explosivePower << 14
        value |= self._jump << 21
        value |= self._motionArmMovementDribbling << 28
        value |= self._unknownD << 31
        data.append(value)
        value = self._registeredPosition.gameId
        value |= self._unknownE << 4
        value |= self._playingStyle.gameId << 5
        value |= self._ballControl << 10
        value |= self._ballWinning << 17
        value |= self._coverage << 24
        value |= self._unknownF << 31
        data.append(value)
        value = self._motionArmMovementRunning
        value |= self._motionCornerKick << 3
        value |= self._weakFootAccuracy << 6
        data.append(value)
        value = self._weakFootUsage
        value |= playablePosition << 2
        value |= self._motionHunchingDribbling << 28
        value |= self._motionHunchingRunning << 30
        data.append(value)
        value = self._motionPenaltyKick
        value |= self._placeKicking << 2
        value |= self._speed << 9
        data.append(value)
        value = self._age
        value |= self._unknownG << 6
        data.append(value)
        value = self._stamina
        value |= self._unknownH << 7
        value |= self._unknownI << 8
        value |= self._strongerFoot.gameId << 12
        value |= comPlayingStyle << 13
        value |= playerSkills << 20
        data.append(value)
        data.append(bytes(self._playerName, 'utf-8')) #TODO: verify
        data.append(bytes(self._printName, 'utf-8')) #TODO: verify
        ba = bytearray(self._struct.pack(*data))
        return ba[:0x32] + ba[0x34:]

class AppearanceEntry(StoredDataStructure): #TODO: complete, use enums
    _struct = struct.Struct("<iIiBBBBBBBBBBB22sB18sB7s")
    _attributes = {}
    _attributes['player'] = (32, 0, -1) #TODO: None is not handled well
    _attributes['editedFaceSettings'] = (1, 0, 0)
    _attributes['editedHairstyleSettings'] = (1, 0, 0)
    _attributes['editedPhysiqueSettings'] = (1, 0, 0)
    _attributes['editedStripStyleSettings'] = (1, 0, 0)
    _attributes['boots'] = (14, 0, 23)
    _attributes['goalkeeperGloves'] = (10, 0, 10)
    _attributes['unknownB'] = (4, 0, 0) #TODO: verify default
    _attributes['baseCopyPlayer'] = (32, 0, 0) #TODO: actually unknown default
    _attributes['neckLength'] = (32, -7, 7)
    _attributes['neckSize'] = (32, -7, 7)
    _attributes['shoulderHeight'] = (32, -7, 7)
    _attributes['shoulderWidth'] = (32, -7, 7)
    _attributes['chestMeasurement'] = (32, -7, 7)
    _attributes['waistSize'] = (32, -7, 7)
    _attributes['armSize'] = (32, -7, 7)
    _attributes['armLength'] = (32, -7, 7)
    _attributes['thighSize'] = (32, -7, 7)
    _attributes['calfSize'] = (32, -7, 7)
    _attributes['legLength'] = (32, -7, 7)
    _attributes['headLength'] = (32, -7, 7)
    _attributes['headWidth'] = (32, -7, 7)
    _attributes['headDepth'] = (32, -7, 7)
    _attributes['wristTapeColorLeft'] = (3, 0, 0)
    _attributes['wristTapeColorRight'] = (3, 0, 0)
    _attributes['wristTapeStyle'] = (2, 0, 0)
    _attributes['sleeveSeasonStyle'] = (2, 0, 0)
    _attributes['longSleevedInners'] = (2, 0, 0)
    _attributes['sockLength'] = (2, 0, 0)
    _attributes['undershorts'] = (2, 0, 0)
    _attributes['shirttail'] = (1, 0, 0)
    _attributes['ankleTaping'] = (1, 0, 0)
    _attributes['playerGloves'] = (1, 0, 0)
    _attributes['playerGlovesColor'] = (3, 0, 0) #TODO: enum
    _attributes['unknownD'] = (4, 0, 0) #TODO: verify default
    _attributes['unknownE'] = (22*8, 0, 0) #TODO: verify default
    _attributes['unknownF'] = (5, 0, 0) #TODO: verify default
    _attributes['unknownG'] = (18*8, 0, 0) #TODO: verify default
    _attributes['unknownH'] = (4, 0, 0) #TODO: verify default
    _attributes['unknownI'] = (7*8, 0, 0) #TODO: verify default
    
    @property
    def spectaclesFrameColor(self):
        return self._spectaclesFrameColor
    
    @spectaclesFrameColor.setter
    def spectaclesFrameColor(self, value):
        self._spectaclesFrameColor = spectaclesFrameColor
    
    @property
    def spectaclesFrameColorMenuId(self):
        return self._spectaclesFrameColor.menuId
    
    @spectaclesFrameColorMenuId.setter
    def spectaclesFrameColorMenuId(self, value):
        self._spectaclesFrameColor = SpectaclesFrameColor.fromMenuId(value)
    
    @property
    def spectacles(self):
        return self._spectacles
    
    @spectacles.setter
    def spectacles(self, value):
        self._spectacles = value
    
    @property
    def spectaclesMenuId(self):
        return self._spectacles.menuId
    
    @spectaclesMenuId.setter
    def spectaclesMenuId(self, value):
        self._spectacles = Spectacles.fromMenuId(value)
        
    @property
    def skinColor(self):
        return self._skinColor
    
    @skinColor.setter
    def spectacles(self, value):
        self._skinColor = value
    
    @property
    def skinColorMenuId(self):
        return self._skinColor.menuId
    
    @skinColorMenuId.setter
    def skinColorMenuId(self, value):
        self._skinColor = SkinColor.fromMenuId(value)
    
    @property
    def irisColor(self):
        return self._irisColor
    
    @irisColor.setter
    def irisColor(self, value):
        self._irisColor = value
    
    @property
    def irisColorMenuId(self):
        return self._irisColor.menuId
    
    @irisColorMenuId.setter
    def irisColorMenuId(self, value):
        self._irisColor = IrisColor.fromMenuId(value)
    
    def setDefaultValues(self):
        super().setDefaultValues()
        self._baseCopyPlayer = self._player
        self._spectaclesFrameColor = SpectaclesFrameColor.WHITE #TODO: verify
        self._spectacles = Spectacles.NONE
        self._playerGlovesColor = PlayerGlovesColor.WHITE
        self._skinColor = SkinColor.LIGHT
        self._irisColor = IrisColor.DARK_BROWN
    
    def fromBytearray(self, data): #TODO: check size beforehand
        data = self._struct.unpack(data)
        self._player = data[0]
        self._editedFaceSettings = data[1] & 1
        self._editedHairstyleSettings = data[1] >> 1 & 1
        self._editedPhysiqueSettings = data[1] >> 2 & 1
        self._editedStripStyleSettings = data[1] >> 3 & 1
        self._boots = data[1] >> 4 & 0b11111111111111
        self._goalkeeperGloves = data[1] >> 18 & 0b1111111111
        self._unknownB = data[1] >> 28 & 0b1111
        self._baseCopyPlayer = data[2]
        self._neckLength = data[3] & 0b1111
        self._neckSize = data[3] >> 4 & 0b1111
        self._shoulderHeight = data[4] & 0b1111
        self._shoulderWidth = data[4] >> 4 & 0b1111
        self._chestMeasurement = data[5] & 0b1111
        self._waistSize = data[5] >> 4 & 0b1111
        self._armSize = data[6] & 0b1111
        self._armLength = data[6] >> 4 & 0b1111
        self._thighSize = data[7] & 0b1111
        self._calfSize = data[7] >> 4 & 0b1111
        self._legLength = data[8] & 0b1111
        self._headLength = data[8] >> 4 & 0b1111
        self._headWidth = data[9] & 0b1111
        self._headDepth = data[9] >> 4 & 0b1111
        # 8 bit (wirst tape) -> B
        self._wristTapeColorLeft = data[10] & 0b111
        self._wristTapeColorRight = data[10] >> 3 & 0b111
        self._wristTapeStyle = data[10] >> 6 & 0b11
        # 8 bit (spectacles frame color, specs, sleeve season style) -> B
        self._spectaclesFrameColor = SpectaclesFrameColor.fromGameId(data[11]
        & 0b111)
        self._spectacles = Spectacles.fromGameId(data[11] >> 3 & 0b111)
        self._sleeveSeasonStyle = data[11] >> 6 & 0b11
        # 8 bit (long sleeved inners - ankle taping) -> B
        self._longSleevedInners = data[12] & 0b11
        self._sockLength = data[12] >> 2 & 0b11
        self._undershorts = data[12] >> 4 & 0b11
        self._shirttail = data[12] >> 6 & 1
        self._ankleTaping = data[12] >> 7 & 1
        # 8 bit (player gloves - unknown D) -> B
        self._playerGloves = data[13] & 1
        self._playerGlovesColor = data[13] >> 1 & 0b111
        self._unknownD = data[13] >> 4 & 0b1111
        # 22 bytes unknown E -> ?????
        self._unknownE = data[14]
        # 8 bit (skin color - unknown F) -> B
        self._skinColor = SkinColor.fromGameId(data[15] & 0b111)
        self._unknownF = data[15] >> 3 & 0b11111
        # 18 bytes unknown G -> ??????
        self._unknownG = data[16]
        # 8 bit (iris color - unknown H) -> B
        self._irisColor = IrisColor.fromGameId(data[17] & 0b1111)
        self._unknownH = data[17] >> 4 & 0b1111
        # 7 bytes unknown I -> ??????
        self._unknownI = data[18]
    
    def toBytearray(self):
        data = []
        data.append(self._player)
        value = self._editedFaceSettings
        value |= self._editedHairstyleSettings << 1
        value |= self._editedPhysiqueSettings << 2
        value |= self._editedStripStyleSettings << 3
        value |= self._boots << 4
        value |= self._goalkeeperGloves << 18
        value |= self._unknownB << 28
        data.append(value)
        data.append(self._baseCopyPlayer)
        value = self._neckLength
        value |= self._neckSize << 4
        data.append(value)
        value = self._shoulderHeight
        value |= self._shoulderWidth << 4
        data.append(value)
        value = self._chestMeasurement
        value |= self._waistSize << 4
        data.append(value)
        value = self._armSize
        value |= self._armLength << 4
        data.append(value)
        value = self._thighSize
        value |= self._calfSize << 4
        data.append(value)
        value = self._legLength
        value |= self._headLength << 4
        data.append(value)
        value = self._headWidth
        value |= self._headDepth << 4
        data.append(value)
        value = self._wristTapeColorLeft
        value |= self._wristTapeColorRight << 3
        value |= self._wristTapeStyle << 6
        data.append(value)
        value = self._spectaclesFrameColor.gameId
        value |= self._spectacles.gameId << 3
        value |= self._sleeveSeasonStyle << 6
        data.append(value)
        value = self._longSleevedInners
        value |= self._sockLength << 2
        value |= self._undershorts << 4
        value |= self._shirttail << 6
        value |= self._ankleTaping << 7
        data.append(value)
        value = self._playerGloves
        value |= self._playerGlovesColor << 1
        value |= self._unknownD << 4
        data.append(value)
        data.append(self._unknownE)
        value = self._skinColor.gameId
        value |= self._unknownF << 3
        data.append(value)
        data.append(self._unknownG)
        value = self._irisColor.gameId
        value |= self._unknownH << 4
        data.append(value)
        data.append(self._unknownI)
        return bytearray(self._struct.pack(*data))
        

def _testToBytearray(testedClass, inputFileName, outputFileName=None):
    print(testedClass.__name__ + ': comparing input with toBytearray output')
    print('Reading from input ' + inputFileName)
    passed = True
    file = open(inputFileName, 'rb')
    input = bytearray(file.read())
    file.close()
    instance = testedClass(input)
    output = instance.toBytearray()
    if (outputFileName != None):
        print('Writing output to ' + outputFileName)
        with open(outputFileName, 'wb') as out:
            out.write(output)
    if (len(input) != len(output)):
        print('Input length:', len(input))
        print('Output length:', len(output))
        print('Output length does not match input length!')
        return False
    mismatches = 0
    for i in range(len(input)):
        if (input[i] != output[i]):
            passed = False
            mismatches += 1
            if (mismatches <= 20):
                print('Byte ', i, ' does NOT match!')
    if (mismatches > 20):
        print('(and ' + (mismatches - 20) + ' more)')
    if (passed):
        print('Success!\n')
    else:
        print('Fail!\n')
    return passed

if __name__ == "__main__":
    import os
    dir = os.path.dirname(os.path.realpath(__file__)) + '/test/'
    allPass = True
    allPass &= _testToBytearray(PlayerEntry, dir + 'player_entry_test')
    allPass &= _testToBytearray(AppearanceEntry, dir + 'appearance_entry_test')
    allPass &= _testToBytearray(EditData, dir + 'edit.dat', dir + 'data.dat')
    print("\nTest results:")
    if (allPass):
        print("ALL OK!")
    else:
        print("FAIL!")
