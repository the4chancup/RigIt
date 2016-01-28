from pes16enums import *
import math
import inspect


class Attr:
    _offsetCounter = 0 # makes class not sideeffect-free, which is a bit ugly
    
    def __init__(self, dataType, length, text=None, default=None):
        self.dataType = dataType
        self.offset = self._offsetCounter
        self.text = text
        if (length <= 0):
            raise ValueError('length must be > 0')
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
            self.valueOffset = False # whether True/False is switched
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
        self.__class__._offsetCounter += self.length
        
    @classmethod
    def resetOffset(cls):
        cls._offsetCounter = 0
        
    @classmethod
    def getOffset(cls):
        return cls._offsetCounter
        
    def readFromBytearray(self, data, byteorder='little'):
        startByte = self.offset // 8
        if (self.dataType == bool):
            return (data[startByte] >> (self.offset % 8)) & 1
        elif (self.dataType == str):
            endByte = startByte + self.length // 8
            val = data[startByte:endByte].decode('utf-8') #TODO: utf-8?
            return val[:val.find('\0')]
        else: # type is int or extension of GameDataEnum
            endByte = (self.offset + self.length - 1) // 8
            if (startByte == endByte): # endianness does not matter
                mask = 0b11111111 >> (8 - self.length)
                val = (data[startByte] >> (self.offset % 8)) & mask
            else: # endianness matters
                subData = data[startByte:endByte + 1]
                val = int.from_bytes(subData, byteorder)
                val >>= self.offset % 8
                val &= (1 << self.length) - 1
            if (self.dataType == int):
                return val
            else: # type is extension of GameDataEnum
                return self.dataType.fromGameId(val)
    
    def writeToBytearray(self, data, value, byteorder='little'):
        startByte = self.offset // 8
        if (self.dataType == bool):
            offset = self.offset % 8
            data[startByte] ^= (-value ^ data[startByte]) & (1 << offset)
        elif (self.dataType == str):
            value += '\0' * (self.length // 8 - len(value))
            endByte = startByte + self.length // 8
            data[startByte:endByte] = bytearray(value, 'utf-8') #TODO: utf-8?
        else: # type is int or extension of GameDataEnum
            if (self.dataType != int): # type is extension of GameDataEnum
                value = value.gameId
            endByte = (self.offset + self.length - 1) // 8
            if (startByte == endByte): # endianness does not matter
                offset = self.offset % 8
                mask = ~(((1 << self.length) - 1) << offset)
                data[startByte] &= mask
                data[startByte] |= (value << offset) & 0b11111111
            else: # endianness matters
                subData = data[startByte:endByte + 1]
                val = int.from_bytes(subData, byteorder)
                offset = self.offset % 8 
                mask = ~(((1 << self.length) - 1) << offset)
                val &= mask
                limitMask = (1 << ((endByte - startByte + 1) * 8)) - 1
                val |= (value << offset) & limitMask
                ba = val.to_bytes(len(subData), byteorder)
                data[startByte:endByte + 1] = ba


    def _stuff(self, length, offset, byte, value):
        mask = ~(((1 << length) - 1) << (offset % 8))
        byte &= mask
        byte |= (value << (offset % 8)) & 0b11111111
        return byte


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
            try:
                return getattr(self, '_' + name) + attr.valueOffset
            except TypeError:
                return getattr(self, '_' + name) #TODO: raise an exception?
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
                    newValue = old[:attr.minValue - len(newValue)] + newValue
            else: # type is extension of GameDataEnum
                newValue = value #TODO: problematic if illegal enum
            setattr(self, '_' + name, newValue)
    
    def unpackData(self):
        if (self._unpacked):
            return
        for name in self._attr:
            setattr(self, '_' + name,
            self._attr[name].readFromBytearray(self._data))
        self._data = None
        self._unpacked = True
          
    def printAttributes(self, sort=True):
        if (sort):
            for name in sorted(self._attr.keys()):
                val = getattr(self, name)
                if (val == None):
                    val = 'None'
                print(name, ' = ', val)
        else:
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
    
    def toBytearray(self, ba=None):
        if (not self._unpacked):
            self.unpackData() #TODO: this might not be wanted
        if (ba == None):
            ba = bytearray([0] * self.dataStructureLength())
        elif (len(ba) != self.dataStructureLength()):
            raise ValueError('Expected bytearray of length ' +
            str(self.dataStructureLength()) + ', got ' + str(len(data)))
        for name in self._attr:
            self._attr[name].writeToBytearray(ba, getattr(self, '_' + name))
        return ba
    
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
    _attr['editedCreatedPlayer'] = Attr(bool, 1, 'Edited/Created player', True)
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


class AppearanceEntry(StoredDataStructure): #TODO: complete, use enums
    Attr.resetOffset()
    _attr = {}
    _attr['player'] = Attr(int, 32, 'Player')
    _attr['editedFaceSettings'] = Attr(bool, 1, 'Edited Face Settings', False)
    _attr['editedHairstyleSettings'] = Attr(bool, 1,
    'Edited Hairstyle Settings', False)
    _attr['editedPhysiqueSettings'] = Attr(bool, 1,
    'Edited Physique Settings', False)
    _attr['editedStripStyleSettings'] = Attr(bool, 1,
    'Edited Strip Style Settings', False)
    _attr['boots'] = Attr(int, 14, 'Boots ID', 23)
    _attr['goalkeeperGloves'] = Attr(int, 10, 'GK gloves ID', 10)
    _attr['unknownB'] = Attr(int, 4, 'Unknown B', 0) #TODO: verify default
    _attr['baseCopyPlayer'] = Attr(int, 32, 'Base Copy Player ID')
    _attr['neckLength'] = Attr(int, 4, 'Neck Length', 7)
    _attr['neckLength'].valueOffset = -7
    _attr['neckSize'] = Attr(int, 4, 'Neck Size', 7)
    _attr['neckSize'].valueOffset = -7
    _attr['shoulderHeight'] = Attr(int, 4, 'Shoulder Height', 7)
    _attr['shoulderHeight'].valueOffset = -7
    _attr['shoulderWidth'] = Attr(int, 4, 'Shoulder Width', 7)
    _attr['shoulderWidth'].valueOffset = -7
    _attr['chestMeasurement'] = Attr(int, 4, 'Chest Measurement', 7)
    _attr['chestMeasurement'].valueOffset = -7
    _attr['waistSize'] = Attr(int, 4, 'Waist Size', 7)
    _attr['waistSize'].valueOffset = -7
    _attr['armSize'] = Attr(int, 4, 'Arm Size', 7)
    _attr['armSize'].valueOffset = -7
    _attr['armLength'] = Attr(int, 4, 'Arm Length', 7)
    _attr['armLength'].valueOffset = -7
    _attr['thighSize'] = Attr(int, 4, 'Thigh Size', 7)
    _attr['thighSize'].valueOffset = -7
    _attr['calfSize'] = Attr(int, 4, 'Calf Size', 7)
    _attr['calfSize'].valueOffset = -7
    _attr['legLength'] = Attr(int, 4, 'Leg Length', 7)
    _attr['legLength'].valueOffset = -7
    _attr['headLength'] = Attr(int, 4, 'Head Length', 7)
    _attr['headLength'].valueOffset = -7
    _attr['headWidth'] = Attr(int, 4, 'Head Width', 7)
    _attr['headWidth'].valueOffset = -7
    _attr['headDepth'] = Attr(int, 4, 'Head Depth', 7)
    _attr['headDepth'].valueOffset = -7
    _attr['wristTapeColorLeft'] = Attr(WristTapeColor, 3,
    'Wrist Tape Color (Left)', WristTapeColor.WHITE)
    _attr['wristTapeColorRight'] = Attr(WristTapeColor, 3,
    'Wrist Tape Coor (Right)', WristTapeColor.WHITE)
    _attr['wristTaping'] = Attr(WristTaping, 2, 'Wrist Taping',
    WristTaping.OFF)
    _attr['sleeves'] = Attr(Sleeves, 2, 'Sleeves', Sleeves.SHORT) #TODO: def.?
    _attr['longSleevedInners'] = Attr(LongSleevedInners, 2,
    'Long-Sleeved Innsers', LongSleevedInners.OFF)
    _attr['sockLength'] = Attr(SockLength, 2, 'Sock Length',
    SockLength.STANDARD)
    _attr['undershorts'] = Attr(Undershorts, 2, 'Undershorts',
    Undershorts.OFF_OFF)
    _attr['shirttail'] = Attr(Shirttail, 1, 'Shirttail', Shirttail.UNTUCKED)
    _attr['ankleTaping'] = Attr(bool, 1, 'Ankle Taping', False)
    _attr['playerGloves'] = Attr(bool, 1, 'Player Gloves', False)
    _attr['playerGlovesColor'] = Attr(PlayerGlovesColor, 3, 'Player Gloves Color',
    PlayerGlovesColor.WHITE)
    _attr['unknownD'] = Attr(int, 4, 'Unknown D', 0) #TODO: verify default
    _attr['unknownE'] = Attr(int, 22*8, 'Unknown E', 0) #TODO: verify default
    _attr['skinColor'] = Attr(SkinColor, 4, 'Skin Color', SkinColor.LIGHT)
    _attr['unknownF'] = Attr(int, 5, 'Unknown F', 0) #TODO: verify default
    _attr['unknownG'] = Attr(int, 18*8, 'Unknown G', 0) #TODO: verify default
    _attr['irisColor'] = Attr(IrisColor, 4, 'Iris Color', IrisColor.DARK_BROWN)
    _attr['unknownH'] = Attr(int, 4, 'Unknown H', 0) #TODO: verify default
    _attr['unknownI'] = Attr(int, 7*8, 'Unknown I', 0) #TODO: verify default


def _testToBytearray(testedClass, inputFileName, outputFileName=None):
    import copy
    print(testedClass.__name__ + ': comparing input with toBytearray output')
    print('Reading from input ' + inputFileName)
    passed = True
    file = open(inputFileName, 'rb')
    input = bytearray(file.read())
    file.close()
    instance = testedClass(input)
    output = instance.toBytearray(copy.copy(input))
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
        print('(and ' + str(mismatches - 20) + ' more)')
    if (passed):
        print('Success!\n')
    else:
        print('Fail!\n')
    return passed

    
if __name__ == '__main__':
    player = PlayerEntry()
    player.printAttributes()
    print(len(player))
    print(PlayerEntry.dataStructureLength())
    print(player.goalkeeper)
    #player.goalkeeper = PlayablePosition.A
    print(player.goalkeeper)
    
    import os
    dir = os.path.dirname(os.path.realpath(__file__)) + '/test/'
    allPass = True
    allPass &= _testToBytearray(PlayerEntry, dir + 'player_entry_test')
    allPass &= _testToBytearray(AppearanceEntry, dir + 'appearance_entry_test')
    #allPass &= _testToBytearray(EditData, dir + 'edit.dat', dir + 'data.dat')
    print('\nTest results:')
    if (allPass):
        print('ALL OK!')
    else:
        print('FAIL!')
    #file = open(dir + 'player_entry_test', 'rb')
    #input = bytearray(file.read())
    #file.close()
    #player = PlayerEntry(input)
    #player.setDefaultValues()
    #player.fromBytearray(input, True)
    #player.printAttributes()
    
    
