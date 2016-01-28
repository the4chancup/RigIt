from enum import Enum


class GameDataEnum(Enum): #TODO: move to its own file
    def __init__(self, menuId, gameId=None, description=None, data=None):
        self.menuId = menuId
        if (gameId != None):
            self.gameId = gameId
        else:
            self.gameId = menuId
        if (description != None):
            self.description = description
        else:
            self.description = self.name
        self.data = data #TODO: consider allowing multiple data arguments
    
    def __str__(self):
        return self.description
        
    def __ge__(self, other): # warning: behavior might be changed
        if self.__class__ is other.__class__:
            return self.menuId >= other.menuId
        return NotImplemented
        
    def __gt__(self, other): # warning: behavior might be changed
        if self.__class__ is other.__class__:
            return self.menuId > other.menuId
        return NotImplemented

    def __le__(self, other): # warning: behavior might be changed
        if self.__class__ is other.__class__:
            return self.menuId <= other.menuId
        return NotImplemented

    def __lt__(self, other): # warning: behavior might be changed
        if self.__class__ is other.__class__:
            return self.menuId < other.menuId
        return NotImplemented
    
    @classmethod
    def stringList(cls):
        strings = []
        for _, member in cls.__members__.items():
            strings.append(str(member))
        return strings
        
    @classmethod
    def _fromAttribute(cls, name, value):
        for member in cls.__members__:
            if (getattr(cls.__members__[member], name) == value):
                return cls.__members__[member]
        raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        
    @classmethod
    def fromMenuId(cls, menuId):
        return cls._fromAttribute('menuId', menuId)
        
    @classmethod
    def fromGameId(cls, gameId):
        return cls._fromAttribute('gameId', gameId)
        
    @classmethod
    def fromDescription(cls, description):
        return cls._fromAttribute('description', description)

    @classmethod
    def fromData(cls, data):
        return cls._fromAttribute('data', data)
        
    @classmethod
    def maxGameId(cls):
        if (len(cls.__members__) == 0):
            return None
        val = None
        for member in cls.__members__:
            if (val == None):
                val = cls.__members__[member].gameId
            elif (cls.__members__[member].gameId > val):
                val = cls.__members__[member].gameId
        return val
    
    @classmethod
    def minGameId(cls):
        if (len(cls.__members__) == 0):
            return None
        val = None
        for member in cls.__members__:
            if (val == None):
                val = cls.__members__[member].gameId
            elif (cls.__members__[member].gameId < val):
                val = cls.__members__[member].gameId
        return val

        
class RegisteredPosition(GameDataEnum):
    CF = (0, 12, 'Centre Forward')
    SS = (1, 11, 'Second Striker')
    LFW = (2, 9, 'Left Wing Forward')
    RWF = (3, 10, 'Right Wing Forward')
    AMF = (4, 8, 'Attacking Midfielder')
    LMF = (5, 6, 'Left Midfielder')
    RMF = (6, 7, 'Right Midfielder')
    CMF = (7, 5, 'Centre Midfielder')
    DMF = (8, 4, 'Defensive Midfielder')
    LB = (9, 2, 'Left Back')
    RB = (10, 3, 'Right Back')
    CB = (11, 1, 'Centre Back')
    GK = (12, 0, 'Goalkeeper')


class PlayablePosition(GameDataEnum):
    C = (0,)
    B = (1,)
    A = (2,)
    #S = (3,) #TODO: not sure if supported


class PlayingStyle(GameDataEnum):
    NONE = (0, 0, 'None')
    GOAL_POACHER = (1, 1, 'Goal Poacher')
    DUMMY_RUNNER = (2, 2, 'Dummy Runner')
    FOX_IN_THE_BOX = (3, 3, 'Fox in the Box')
    TARGET_MAN = (4, 13, 'Target Man')
    CREATIVE_PLAYMAKER = (5, 14, 'Creative Playmaker')
    PROFILIC_WINGER = (6, 4, 'Prolific Winger')
    CLASSIC_NO_TEN = (7, 5, 'Classic No. 10')
    HOLE_PLAYER = (8, 6, 'Hole Player')
    BOX_TO_BOX = (9, 7, 'Box to Box')
    THE_DESTROYER = (10, 9, 'The Destroyer')
    ANCHOR_MAN = (11, 8, 'Anchor Man')
    BUILD_UP = (12, 15, 'Build Up')
    EXTRA_FRONTMAN = (13, 10, 'Extra Frontman')
    OFFENSIVE_FULLBACK = (14, 11, 'Offensive Fullback')
    DEFENSIVE_FULLBACK = (15, 12, 'Defensive Fullback')
    OFFENSIVE_GOALKEEPER = (16, 17, 'Offensive Goalkeeper')
    DEFENSIVE_GOALKEEPER = (17, 18, 'Defensive Goalkeeper')
    #UNKNOWN = (19, 16, 'Unknown') #TODO: not sure if supported


class StrongerFoot(GameDataEnum):
    RIGHT_FOOT = (0, 0, 'Right foot')
    LEFT_FOOT = (1, 1, 'Left foot')


class WristTapeColor(GameDataEnum): #TODO: has an unused bit
    WHITE = (0, 1, 'White', 0xFFFFFF) #TODO: verify
    BLACK = (1, 2, 'Black', 0x262626) #TODO: verify
    BEIGE = (2, 3, 'Beige') #TODO: color
    STRIP_COLOR = (3, 0, 'Strip Color') #TODO: perhaps 0xCC00FF


class WristTaping(GameDataEnum):
    OFF = (0, 0, 'Off')
    RIGHT = (1, 1, 'Right')
    LEFT = (2, 2, 'Left')
    BOTH = (3, 3, 'Both')
    

class SpectaclesFrameColor(GameDataEnum): # Apparently identical to GlovesColor
    WHITE = (0, 0, 'White', 0xFFFFFF)
    BLACK = (1, 1, 'Black', 0x262626)
    RED = (2, 2, 'Red', 0xA92024)
    BLUE = (3, 3, 'Blue', 0x004CFF)
    YELLOW = (4, 4, 'Yellow', 0xFFD300)
    GREEN = (5, 5, 'Green', 0x285E30)
    PINK = (6, 6, 'Pink', 0xd3448B)
    TURQUOISE = (7, 7, 'Turquoise', 0x5CBBD1)


class Spectacles(GameDataEnum):
    NONE = (0, 0, 'None')
    RECTANGLE_RIMLESS = (1, 1, 'Rectangle (rimless)')
    RECTANGLE_HALF_FRAME = (2, 2, 'Rectangle (half frame)')
    RECTANGLE_FULL_FRAME = (3, 3, 'Rectangle (full frame)')
    OVAL_RIMLESS = (4, 4, 'Oval (rimless)')
    OVAL_HALF_FRAME = (5, 5, 'Oval (half frame)')
    OVAL_FULL_FRAME = (6, 6, 'Oval (full frame)')
    ROUND_FULL_FRAME = (7, 7, 'Round (full frame)')


class Sleeves(GameDataEnum):
    SHORT = (0, 1, 'Short')
    LONG = (1, 2, 'Long')
    SEASONAL = (2, 0, 'Seasonal')


class LongSleevedInners(GameDataEnum):
    OFF = (0, 0, 'Off')
    NORMAL = (1, 1, 'Normal')
    TURTLE_NECK = (2, 2, 'Turtle neck')
    #UNKNOWN = (3, 3, 'Unknown') #TODO: not sure if supported


class SockLength(GameDataEnum):
    STANDARD = (0, 0, 'Standard')
    LONG = (1, 1, 'Long')
    SHORT = (2, 2, 'Short')
    #UNKNOWN = (3, 3, 'Unknown') #TODO: not sure if supported


class Undershorts(GameDataEnum):
    OFF_OFF = (0, 0, 'Summer: Off / Winter: Off')
    OFF_LONG = (1, 2, 'Summer: Off / Winter: Long')
    SHORT_SHORT = (2, 1, 'Summer: Short / Winter: Short')
    SHORT_LONG = (3, 3, 'Summer: Short / Winter: Long')


class Shirttail(GameDataEnum):
    UNTUCKED = (0, 1, 'Untucked')
    TUCKED_IN = (1, 0, 'Tucked in')


class PlayerGlovesColor(GameDataEnum):
    WHITE = (0, 0, 'White', 0xFFFFFF)
    BLACK = (1, 1, 'Black', 0x262626)
    RED = (2, 2, 'Red', 0xA92024)
    BLUE = (3, 3, 'Blue', 0x004CFF)
    YELLOW = (4, 4, 'Yellow', 0xFFD300)
    GREEN = (5, 5, 'Green', 0x285E30)
    PINK = (6, 6, 'Pink', 0xd3448B)
    TURQUOISE = (7, 7, 'Turquoise', 0x5CBBD1)


class SkinColor(GameDataEnum):
    LIGHT = (0, 1, 'Light', 0xFFD1B3)
    FAIR = (1, 2, 'Fair', 0xDFB391)
    MEDIUM = (2, 3, 'Medium', 0xC19572)
    OLIVE = (3, 4, 'Olive', 0xA37658)
    BROWN = (4, 5, 'Brown', 0x845C40)
    BLACK = (5, 6, 'Black', 0x64442C)
    TRANSPARENT = (6, 0, 'Transparent', 0xCC00FF)
    CUSTOM = (7, 7, 'Custom', 0xFFFFFF)


class IrisColor(GameDataEnum):
    BLACK = (0, 0, 'Black', 0x120600)
    DARK_BROWN = (1, 1, 'Dark brown', 0x361000)
    BROWN = (2, 2, 'Brown', 0x723C12)
    SADDLE_BROWN = (3, 3, 'Saddle brown', 0xA14800)
    MIDNIGHT_BLUE = (4, 4, 'Midnight blue', 0x121C2A) #TODO: proper name
    CHARCOAL = (5, 5, 'Charcoal', 0x2E3C40)
    GRAY = (6, 6, 'Gray', 0x788084)
    BLUE = (7, 7, 'Blue', 0x3E7899)
    SIENNA  = (8, 8, 'Sienna', 0xAF5A18)
    GREEN = (9, 9, 'Green', 0x5C8436)
    PURPLE = (10, 10, 'Purple', 0x9378AB)
    #TODO: not sure if more colors are supported


if (__name__ == '__main__'):
    pass
