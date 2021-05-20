# Gcode Filename Format Plus

Cura plugin that adds print settings in G-code filenames, now with multi-extruder and OctoPrint support

Default filename format:

    [abbr_machine] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C

Example filename output:

    PI3MK3M paperclip Generic PLA lw 0.4mm lh 0.2mm if 20% ext1 200C bed 60C.gcode

## Requirements
Cura 4.4 or later

## Installation
### Preferred method
Install plugin from [Ultimaker Marketplace](https://marketplace.ultimaker.com/app/cura/plugins/rgomezjnr/GcodeFilenameFormatPlus)

### Alternatively
1. Clone repository (or [download repository .zip](https://github.com/rgomezjnr/GcodeFilenameFormatPlus/archive/master.zip))
```
git clone https://github.com/rgomezjnr/GcodeFilenameFormatPlus.git
```
2. Move GcodeFilenameFormatPlus folder to Cura plugins folder
- Windows: C:\Users\\%USERNAME%\AppData\Roaming\cura\4.4\plugins
- Mac: $User/Library/Application\ Support/Cura/4.4/plugins
- Linux: $HOME/.local/share/cura/4.4/plugins
3. Launch Cura

## Usage
1. Specify filename format using Extensions -> Gcode Filename Format Plus -> Edit Format

    ![Edit Format Dialog](images/edit-format-dialog.png)

2. Slice object
3. Select Save to Disk button, or File -> Export, or send job to printer

Besides .gcode, the plugin also works with other file types such as .3mf and .stl. Simply select from the available file types in the save dialog. Additionally, GFF+ will pass the custom job name to an OctoPrint server when using the [OctoPrint Connection](https://marketplace.ultimaker.com/app/cura/plugins/fieldofview/OctoPrintPlugin) plugin.

## Format options

- base_name - object/model name
- job_name - same as base_name
- abbr_machine - abbreviated printer machine name
- printer_name - printer manufacturer and model
- profile_name - name of the profile used for slicing e.g. Normal, Fine, Draft
- cura_version - the Semantic version of Cura e.g. 4.4.0
- object_count - number of objects on the build plate
- layer_height - layer height/thickness, vertical resolution (mm)
- machine_nozzle_size - nozzle diameter e.g. 0.2 mm, 0.4 mm, 0.6 mm
- line_width - line/nozzle width e.g. 0.2 mm, 0.4 mm, 0.6 mm
- wall_thickness - thickness of shell walls (mm)
- infill_sparse_density - infill percentage (%)
- infill_pattern - infill pattern e.g grid, lines, triangles
- top_bottom_pattern - pattern of the top and bottom layers e.g. lines, concentric, zig zag
- brand - the brand of the filament e.g. Generic, Prusa, MatterHackers, eSun, etc.
- material - material type e.g. PLA, PETG, ABS, etc.
- material_diameter - filament size e.g. 1.75 mm, 3 mm
- material_print_temperature - material/nozzle temperature (°C)
- material_bed_temperature - build plate temperature (°C)
- material_flow - extruded material flow rate (%)
- material_weight - printed material weight (g)
- material_length - printed material length (m)
- material_cost - printed material cost
- color_name - material color
- speed_print - print speed (mm/s)
- retraction_combing - combing mode
- magic_spiralize - spiralize outer contour, vase mode
- print_time - total print time in HHMMSS
- print_time_days - print time in days
- print_time_hours - print time in hours
- print_time_hours_all - print_time_days * 24 + print_time_hours
- print_time_minutes - print time in minutes
- print_time_seconds - print time in seconds
- date - current date in YYYY-MM-DD
- time - current time in HH-MM
- datetime - current time in YYYY-MM-DDTHHMMSS
- year - current year in YYYY
- month - current month in MM
- day - current day in DD
- hour - current hour in HH
- minute - current minute in MM

For the full list please refer to [fdmprinter.def.json.pot](https://github.com/Ultimaker/Cura/blob/master/resources/i18n/fdmprinter.def.json.pot)

### Multiple extruder options
For printers with multiple extruders, individual extruder settings can be specified by appending the extruder number to the option.

Example filename format:

    [abbr_machine] [base_name] ext1 [brand1] [material1] [material_print_temperature1]C [line_width1]mm ext2 [brand2] [material2] [material_print_temperature2]C [line_width2]mm

Example filename output:

    PI3MK3M paperclip ext1 Ultimaker ABS 255C 0.7mm ext2 Ultimaker Tough PLA 215C 0.35mm.gcode

## Source code
https://github.com/rgomezjnr/GcodeFilenameFormatPlus

## Authors
[Robert Gomez, Jr.](https://github.com/rgomezjnr)

[Michael Chan](https://github.com/mchan016)

[Geoffrey Young](https://github.com/geoffrey-young)

## License
[LGPLv3](https://github.com/rgomezjnr/GcodeFilenameFormat/blob/master/LICENSE)
