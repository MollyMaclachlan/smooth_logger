from enum import Enum

class Categories(Enum):
    DISABLED = 0  # do not print to console or save to log file
    ENABLED = 1   # print to console but do not save to log file
    MAXIMUM = 2   # print to console and save to log file