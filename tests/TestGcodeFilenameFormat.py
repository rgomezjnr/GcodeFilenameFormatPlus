import unittest
from GcodeFilenameFormatPlus import GcodeFilenameFormatPlus
#import GcodeFilenameFormatPlus
#from ../ import GcodeFilenameFormatPlus
#target = __import__("../GcodeFilenameFormatPlus.py")

class TestGcodeFilenameFormatPlus(unittest.TestCase):

    def test_getPrintSettings(self):
        # Normal profile print settings, Generic PLA
        input = {'layer_height': 0.15,
                'infill_spare_density': 10,
                'default_material_print_temperature': 200,
                'material_bed_temperature': 60}

        #print_settings = getPrintSettings()
        print_settings = target.getPrintSettings()

        # assert that machine manager called to obtain global stack for retrieving print settings
        # assert that print settings match test input
        self.assertDictEqual(input, print_settings)
        # assert that print_settings type is dict
        self.assertIsInstance(print_settings, dict)
        # assert that print settings is not empty
        self.assertIsNotNone(print_settings)

    #def test_getModifiedPrintSettings():

    #def test_getDefaultPrintSettings():

    #def test_logPrintSettings():
        # assert that Logger.log called

    #def test_addPrintSettingsToFilename():
        # assert that return object is string

if __name__ == '__main__':
    unittest.main()
