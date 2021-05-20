# AGPLv3

from . import GcodeFilenameFormatPlus

def getMetaData():
    return {}

def register(app):
    return {
        "extension": GcodeFilenameFormatPlus.GcodeFilenameFormatPlus()
    }
