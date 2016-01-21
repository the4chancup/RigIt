from pes16enums import *
import math
import struct
import inspect


class Attr:
    _offsetCounter = 0 # makes class not sideeffect-free, which is a bit ugly
    
    def __init__(self, dataType, length, text=None, default=None):
        self.dataType = dataType
        self.offset = self._offsetCounter
        self.text = text
        if (default != None and type(default) != self.dataType):
            raise TypeError('Default value must be of the same data type')
        self.defaultValue = default
        if (self.dataType == int):
            self.length = length
            self.minValue = 0
            self.maxValue = math.pow(2, length) - 1
            self.valueOffset = 0
        elif (self.dataType == bool):
            if (length != 1):
                raise ValueError('length of type bool must be 1')
            self.length = 1
            self.minValue = False
            self.maxValue = True
            self.valueOffset = False # whether True/false is switched
        elif (self.dataType == str): # min/max applies to the string length
            if (length % 8 != 0):
                raise ValueError('length of type str must be a multiple of 8')
            self.length = length
            self.minValue = 0
            self.maxValue = length // 8
            self.valueOffset = None
        elif (inspect.isclass(self.dataType) and
        GameDataEnum in self.dataType.__bases__):
            self.length = length
            self.minValue = dataType.minGameId()
            self.maxValue = dataType.maxGameId()
            self.valueOffset = None
        else:
            raise TypeError(__class__.__name__ +
            ' does not support the given type or class')
        self._offsetCounter += self.length
        
    @classmethod
    def resetOffset(cls):
        cls._offsetCounter = 0
        
    @classmethod
    def getOffset(cls):
        return cls._offsetCounter
        
    def readFromLittleEndian(self, data):
        if (self.dataType == bool):
            return (data[self.offset // 8] >> (self.offset % 8)) & 1
        elif (self.dataType == str):
            start = self.offset // 8
            end = start + self.length // 8 + 1
            val = data[start:end].decode('utf-8') #TODO: verify encoding
            return val[:val.find('\0')]
        else: # type is int or extension of GameDataEnum
            startByte = attr.offset // 8
            endByte = (attr.offset + attr.length) // 8
            if (startByte == endByte):
                mask = 0b11111111 >> (8 - attr.length)
                val = (data[startByte] >> (attr.offset % 8)) & mask
            else:
                #hard
                val = 0 #TODO
            if (self.dataType == int):
                return val
            else: # type is extension of GameDataEnum
                return dataType.fromGameId(val)
        
class StoredDataStructure:
    _attr = {}
    _length = None
    
    @classmethod
    def dataStructureLength(cls): # because __len__ can't be a class method
        if (cls._length != None):
            return math.ceil(cls._length / 8)
        cls._length = 0
        for name in cls._attr:
            cls._length += cls._attr[name].length
        return math.ceil(cls._length / 8)
    
    def __len__(self):
        return self.dataStructureLength()
    
    def __init__(self, data=None, unpackData=False):
        self._data = data
        self._unpacked = False
        if (data != None):
            self.fromBytearray(self._data, unpackData)
        else:
            self.setDefaultValues()
    
    def __getattribute__(self, name):
        if (name == '_attr' or name == '_length' or name == '_data' or
        name == '_unpacked' or not name in self._attr): #TODO: fishy solution
            return super().__getattribute__(name)
        attr = self._attr[name]
        if (not self._unpacked):
            self.unpackData()
        if (attr.dataType == int):
            return getattr(self, '_' + name) + attr.valueOffset
        elif (attr.dataType == bool):
            if (attr.valueOffset):
                return not getattr(self, '_' + name)
            return getattr(self, '_' + name)
        else: # all other types
            return getattr(self, '_' + name)
    
    def __setattr__(self, name, value):
        if (not name in self._attr): # no need to check for actual attributes
            super().__setattr__(name, value)
        else:
            attr = self._attr[name]
            if (type(value) != attr.dataType or
            (inspect.isclass(attr.dataType) and
            value.__class__ != attr.dataType)):
                raise TypeError(name + ' only accepts values of its own type')
            if (not self._unpacked):
                self.unpackData()
            if (attr.dataType == int):
                newValue = value - attr.valueOffset
                newValue = max(attr.minValue, min(newValue, attr.maxValue))
            elif (attr.dataType == bool):
                if (attr.valueOffset):
                    newValue = not value
                newValue |= attr.minValue
                newValue &= attr.maxValue
            elif (attr.dataType == str):
                newValue = value[:attr.maxValue]
                if (len(newValue) < attr.minValue):
                    old = getattr(self, '_' + name)
                    newValue = old[:(attr.minValue - len(newValue))] + newValue
            else: # type is extension of GameDataEnum
                newValue = value
            setattr(self, '_' + name, newValue)
    
    def unpackData(self):
        if (self._unpacked):
            return
        for name in self._attr:
            setattr(self, '_' + name,
            self._attr[name].readFromLittleEndian(self._data))
        self._data = None
        self._unpacked = True
          
    def printAttributes(self):
        for attr in self._attr:
            print(self._attr[attr].text, ' = ', getattr(self, '_' + attr))
            
    def fromBytearray(self, data, unpackData=False):
        if (len(data) != self.dataStructureLength()):
            raise ValueError('Expected bytearray of length ' +
            str(self.dataStructureLength()) + ', got ' + str(len(data)))
        self._data = data
        self._unpacked = False
        if (unpackData):
            self.unpackData()
    
    def toBytearray(self):
        pass
        #return data
    
    def setDefaultValues(self):
        for name in self._attr:
            #if (self._attr[name].defaultValue != None) #TODO: do this?
            setattr(self, '_' + name, self._attr[name].defaultValue)
        self._data = None
        self._unpacked = True
    
    def getAttributeText(self, name): #TODO: needed?
        return self._attr[name].text
        

class PlayerEntry(StoredDataStructure):
    Attr.resetOffset()
    _attr = {}
    _attr['playerId'] = Attr(int, 32, 'Player ID')
    _attr['commentaryName'] = Attr(int, 32, 'Commentary ID', -1)
    _attr['unknownA'] = Attr(int, 16, 'Unknown A', 0xFFFF)
    _attr['nationalityRegion'] = Attr(int, 16, 'Nationality/Region', 0x0401)
    _attr['height'] = Attr(int, 8, 'Height', 180)
    _attr['weight'] = Attr(int, 8, 'Weight', 75)
    _attr['motionGoalCelebration1'] = Attr(int, 8, 'Goal Celebration 1', 0)
    _attr['motionGoalCelebration2'] = Attr(int, 8, 'Goal Celebration 1', 0)
    _attr['attackingProwess'] = Attr(int, 7, 'Attacking Prowess', 80)
    _attr['defensiveProwess'] = Attr(int, 7, 'Defensive Prowess', 80)
    _attr['goalkeeping'] = Attr(int, 7, 'Goalkeeping', 80)
    _attr['dribbling'] = Attr(int, 7, 'Dribblig', 80)
    _attr['motionFreeKick'] = Attr(int, 4, 'Free Kick', 0)
    _attr['motionFreeKick'].valueOffset = 1
    _attr['finishing'] = Attr(int, 7, 'Finishing', 80)
    _attr['lowPass'] = Attr(int, 7, 'Low Pass', 80)
    _attr['loftedPass'] = Attr(int, 7, 'Lofted Pass', 80)
    _attr['header'] = Attr(int, 7, 'Header', 80)
    _attr['form'] = Attr(int, 3, 'Form', 3)
    _attr['form'].valueOffset = 1
    _attr['editedCreatedPlayer'] = Attr(bool, 1, 'Edited/created player', True)
    _attr['swerve'] = Attr(int, 7, 'Swerve', 80)
    _attr['catching'] = Attr(int, 7, 'Catching', 80)
    _attr['clearing'] = Attr(int, 7, 'Clearing', 80)
    _attr['reflexes'] = Attr(int, 7, 'Reflexes', 80)
    _attr['injuryResistance'] = Attr(int, 2, 'Injury Resistance', 1)
    _attr['injuryResistance'].valueOffset = 1
    _attr['unknownC'] = Attr(int, 2, 'Unknown C', 0)
    _attr['bodyBalance'] = Attr(int, 7, 'Body Balance', 80)
    _attr['kickingPower'] = Attr(int, 7, 'Kicking Power', 80)
    _attr['explosivePower'] = Attr(int, 7, 'Explosive Power', 80)
    _attr['jump'] = Attr(int, 7, 'Jump', 80)
    _attr['motionArmMovementDribbling'] = Attr(int, 3,
    'Arm Movement (Dribbling)', 0)
    _attr['motionArmMovementDribbling'].valueOffset = 1
    _attr['unknownD'] = Attr(bool, 1, 'Unknown D', False)
    _attr['registeredPosition'] = Attr(RegisteredPosition, 4,
    'Registered Position', RegisteredPosition.CF)
    _attr['unknownE'] = Attr(bool, 1, 'Unknown E', False)
    _attr['playingStyle'] = Attr(PlayingStyle, 5, 'Playing Style',
    PlayingStyle.NONE)
    _attr['ballControl'] = Attr(int, 7, 'Ball Control', 80)
    _attr['ballWinning'] = Attr(int, 7, 'Ball Winning', 80)
    _attr['coverage'] = Attr(int, 7, 'Coverage', 80)
    _attr['unknownF'] = Attr(bool, 1, 'Unknown F', False)
    _attr['motionArmMovementRunning'] = Attr(int, 3,
    'Arm Movement (Running)', 0)
    _attr['motionArmMovementRunning'].valueOffset = 1
    _attr['motionCornerKick'] = Attr(int, 3, 'Corner Kick', 0)
    _attr['motionCornerKick'].valueOffset = 1
    _attr['weakFootAccuracy'] = Attr(int, 2, 'Weak Foot Accuracy', 1)
    _attr['weakFootAccuracy'].valueOffset = 1
    _attr['weakFootUsage'] = Attr(int, 2, 'Weak Foot Usage', 1)
    _attr['weakFootUsage'].valueOffset = 1
    _attr['centreForward'] = Attr(PlayablePosition, 2, 'CF',
    PlayablePosition.C)
    _attr['secondStriker'] = Attr(PlayablePosition, 2, 'SS',
    PlayablePosition.C)
    _attr['leftWingForward'] = Attr(PlayablePosition, 2, 'LFW',
    PlayablePosition.C)
    _attr['rightWingForward'] = Attr(PlayablePosition, 2, 'RWF',
    PlayablePosition.C)
    _attr['attackingMidfielder'] = Attr(PlayablePosition, 2, 'AMF',
    PlayablePosition.C)
    _attr['defensiveMidfielder'] = Attr(PlayablePosition, 2, 'DMF',
    PlayablePosition.C)
    _attr['centreMidfielder'] = Attr(PlayablePosition, 2, 'CMF',
    PlayablePosition.C)
    _attr['leftMidfielder'] = Attr(PlayablePosition, 2, 'LMF',
    PlayablePosition.C)
    _attr['rightMidfielder'] = Attr(PlayablePosition, 2, 'RMF',
    PlayablePosition.C)
    _attr['centreBack'] = Attr(PlayablePosition, 2, 'CB', PlayablePosition.C)
    _attr['leftBack'] = Attr(PlayablePosition, 2, 'LB', PlayablePosition.C)
    _attr['rightBack'] = Attr(PlayablePosition, 2, 'RB', PlayablePosition.C)
    _attr['goalkeeper'] = Attr(PlayablePosition, 2, 'GK', PlayablePosition.C)
    _attr['motionHunchingDribbling'] = Attr(int, 2, 'Hunching (Dribbling)', 0)
    _attr['motionHunchingDribbling'].valueOffset = 1
    _attr['motionHunchingRunning'] = Attr(int, 2, 'Hunching (Running)', 0)
    _attr['motionHunchingRunning'].valueOffset = 1
    _attr['motionPenaltyKick'] = Attr(int, 2, 'Penalty Kick', 0)
    _attr['motionPenaltyKick'].valueOffset = 1
    _attr['placeKicking'] = Attr(int, 7, 'Place Kicking', 80)
    _attr['speed'] = Attr(int, 7, 'Speed', 80)
    _attr['age'] = Attr(int, 6, 'Age', 17)
    _attr['unknownG'] = Attr(int, 2, 'Unknown G', 0)
    _attr['stamina'] = Attr(int, 7, 'Stamina', 80)
    _attr['unknownH'] = Attr(bool, 1, 'Unknown H', False)
    _attr['unknownI'] = Attr(int, 4, 'Unknown I', 0)
    _attr['strongerFoot'] = Attr(StrongerFoot, 1, 'Stronger Foot',
    StrongerFoot.RIGHT_FOOT)
    _attr['cpsTrickster'] = Attr(bool, 1, 'Trickster', False)
    _attr['cpsMazingRun'] = Attr(bool, 1, 'Mazing Run', False)
    _attr['cpsSpeedingBullet'] = Attr(bool, 1, 'Speeding Bullet', False)
    _attr['cpsIncisiveRun'] = Attr(bool, 1, 'Incisive Run', False)
    _attr['cpsLongBallExpert'] = Attr(bool, 1, 'Long Ball Expert', False)
    _attr['cpsEarlyCross'] = Attr(bool, 1, 'Early Cross', False)
    _attr['cpsLongRanger'] = Attr(bool, 1, 'Long Ranger', False)
    _attr['skillScissorsFeint'] = Attr(bool, 1, 'Scissors Feint', False)
    _attr['skillFlipFlap'] = Attr(bool, 1, 'Flip Flap', False)
    _attr['skillMarseilleTurn'] = Attr(bool, 1, 'Marseille Turn', False)
    _attr['skillSombrero'] = Attr(bool, 1, 'Sombrero', False)
    _attr['skillCutBehindAndTurn'] = Attr(bool, 1, 'Cut Behind & Turn', False)
    _attr['skillScotchMove'] = Attr(bool, 1, 'Scotch Move', False)
    _attr['skillHeading'] = Attr(bool, 1, 'Heading', False)
    _attr['skillLongRangeDrive'] = Attr(bool, 1, 'Long Range Drive', False)
    _attr['skillKnuckleShot'] = Attr(bool, 1, 'Knuckle Shot', False)
    _attr['skillAcrobaticFinishing'] = Attr(bool, 1, 'Acrobatic Finishing',
    False)
    _attr['skillHeelTrick'] = Attr(bool, 1, 'Heel Trick', False)
    _attr['skillFirstTimeShot'] = Attr(bool, 1, 'First-time Shot', False)
    _attr['skillOneTouchPass'] = Attr(bool, 1, 'One-touch Pass', False)
    _attr['skillWeightedPass'] = Attr(bool, 1, 'Weighted Pass', False)
    _attr['skillPinpointCrossing'] = Attr(bool, 1, 'Pinpoint Crossing', False)
    _attr['skillOutsideCurler'] = Attr(bool, 1, 'Outside Curler', False)
    _attr['skillRabona'] = Attr(bool, 1, 'Rabona', False)
    _attr['skillLowLoftedPass'] = Attr(bool, 1, 'Low Lofted Pass', False)
    _attr['skillLowPuntTrajectory'] = Attr(bool, 1,
    'Low Punt Trajectory', False)
    _attr['skillLongThrow'] = Attr(bool, 1, 'Long Throw', False)
    _attr['skillGkLongThrow'] = Attr(bool, 1, 'GK Long Throw', False)
    _attr['skillMalicia'] = Attr(bool, 1, 'Malicia', False)
    _attr['skillManMarking'] = Attr(bool, 1, 'Man Marking', False)
    _attr['skillTrackback'] = Attr(bool, 1, 'Trackback', False)
    _attr['skillAcrobaticClear'] = Attr(bool, 1, 'Acrobatic Clear', False)
    _attr['skillCaptaincy'] = Attr(bool, 1, 'Captaincy', False)
    _attr['skillSuperSub'] = Attr(bool, 1, 'Super-sub', False)
    _attr['skillFightingSpirit'] = Attr(bool, 1, 'Fighting Spirit', False)
    _attr['playerName'] = Attr(str, 368, 'Player Name', 'PLACEHOLDER')
    _attr['playerName'].minValue = 1
    _attr['printName'] = Attr(str, 128, 'Print Name', '')


if (__name__ == '__main__'):
    player = PlayerEntry()
    player.printAttributes()
    print(len(player))
    print(PlayerEntry.dataStructureLength())
    print(player.goalkeeper)
    player.goalkeeper = PlayablePosition.A
    print(player.goalkeeper)

