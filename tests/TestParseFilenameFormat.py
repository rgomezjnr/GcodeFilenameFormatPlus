import sys
import unittest

sys.path.append("..")
import ParseFilenameFormat

class TestParseFilenameFormat(unittest.TestCase):
    #def setUp(self):

    def test_dual_extruder_format(self):
        print_settings = {
            'abbr_machine': 'PI3MK3M',
            'base_name': 'paperclip',
            'material_weight': 2,
            'material_length': 85.46,
            'material_cost': '15.10',
            'brand1': 'Ultimaker',
            'material1': 'Black ABS',
            'material_weight1': 1,
            'material_length1': 50.12,
            'material_cost1': '9.50',
            'brand2': 'Ultimaker',
            'material2': 'White Tough PLA',
            'material_weight2': 1,
            'material_length2': 35.34,
            'material_cost2': '5.60'
        }
        filename_format = '[abbr_machine] [base_name] total [material_weight]g [material_length]m $[material_cost] [brand1] [material1] [material_weight1]g [material_length1]m $[material_cost1] [brand2] [material2] [material_weight2]g [material_length2]m $[material_cost2]'
        expected_filename = 'PI3MK3M paperclip total 2g 85.46m $15.10 Ultimaker Black ABS 1g 50.12m $9.50 Ultimaker White Tough PLA 1g 35.34m $5.60'
        filename = ParseFilenameFormat.parseFilenameFormat(print_settings, filename_format)
        self.assertEqual(filename, expected_filename)

    #def tearDown(self):

if __name__ == '__main__':
    unittest.main()
