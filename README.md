# Gcode Filename Format

Cura plugin for specifying filename format with print settings

Example:  
PI3MK3M_paperclip Generic PLA lh 0.2mm if 20% ext1 200C bed 60C.gcode

Default filename format:  
[base_name] [brand] [material] lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C

## Reqiurements
Cura 4.4 or later

## Usage
1. Specify filename format using Extensions -> Gcode Filename Format -> Edit Format
2. Slice object
3. Select Save Gcode button (instead of default Save to File button)
4. Futher modify formatted filename as desired in the save dialog
5. Select Save

Besides .gcode, the plugin will also work other file types such as .3mf and .stl. Simply select from the available file types in the save dialog.

## Format options

- base_name - the initial output filename from the object name and Cura's "Add machine prefix to job name" setting
- brand - the brand of the filament e.g. Generic, Prusa, MatterHackers, eSun, etc.
- material - material type e.g. PLA, PETG, ABS, etc.

The following are standard options from Cura. Examples include:

- layer_height - height of each layer (mm)
- infill_sparse_density - infill percentage (%)
- material_print_temperature - material/nozzle temperature (°C)
- material_bed_temperature - build plate temperature (°C)
- material_diameter - filament size e.g. 1.75 mm, 3 mm
- line_width - line/nozzle width e.g. 0.2 mm, 0.4 mm, 0.6 mm
- speed_print - print speed (mm/s)
- magic_spiralize - spiralize outer contour, vase mode

For the full list please refer to [fdmprinter.def.json.pot](https://github.com/Ultimaker/Cura/blob/6091c67dee7b9a4fc7b066e59db2b76572398909/resources/i18n/fdmprinter.def.json.pot)

## Source code
https://github.com/rgomezjnr/GcodeFilenameFormat

## Authors
[Robert Gomez, Jr.](https://github.com/rgomezjnr)

[Michael Chan](https://github.com/mchan016)

## License
[LGPLv3](https://github.com/rgomezjnr/GcodeFilenameFormat/blob/master/LICENSE)