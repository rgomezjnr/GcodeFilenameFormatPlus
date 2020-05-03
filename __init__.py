# AGPLv3

from . import GcodeFilenameFormat

def getMetaData():
    return {}

def register(app):
    return {
        "extension": GcodeFilenameFormat.GcodeFilenameFormat()
    }
