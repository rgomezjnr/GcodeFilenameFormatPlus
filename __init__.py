# AGPLv3

from . import GcodeFilenameFormat

def getMetaData():
    return {}

def register(app):
    return {
        "output_device": GcodeFilenameFormat.GcodeFilenameFormatDevicePlugin(),
        "extension": GcodeFilenameFormat.GcodeFilenameFormat()
    }
