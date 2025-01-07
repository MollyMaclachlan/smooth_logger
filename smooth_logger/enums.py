from enum import Enum

class Categories(Enum):
    DISABLED = 0  # do not print to console or save to log file
    PRINT    = 1  # print to console but do not save to log file
    SAVE     = 2  # save to log file but do not print to console
    MAXIMUM  = 3  # print to console and save to log file
    ENABLED  = 4  # DEPRECATED: print to console but do not save to log file
