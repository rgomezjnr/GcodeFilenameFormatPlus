// LGPLv3

import UM 1.2 as UM
import QtQuick 2.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.1

UM.Dialog
{
    id: base
    title: "Gcode Filename Format - Help"
    width: 800 * screenScaleFactor
    height: 610 * screenScaleFactor
    minimumWidth: 700 * screenScaleFactor

    ScrollView {
        width: parent.width
        height: parent.height

        Text
        {
            onLinkActivated: Qt.openUrlExternally(link)

            text:
                "<h1>Example</h1>
                <p>PI3MK3M_paperclip Generic PLA lw 0.4mm lh 0.2mm if 20% ext1 200C bed 60C.gcode</p>
                <br>
                <h1>Default filename format</h1>
                <p>[base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]%<br>
                ext1 [material_print_temperature]C bed [material_bed_temperature]C</p>
                <br>
                <h1>Usage</h1>
                <ol>
                    <li>Specify filename format using Extensions -> Gcode Filename Format -> Edit Format</li>
                    <br>
                    <br>
                    <img src=\"images/edit-format-dialog.png\"/>
                    <br>
                    <li>Slice object</li>
                    <li>Select Save Gcode button (instead of default Save to File button)</li>
                    <br>
                    <br>
                    <img src=\"images/save-gcode-button.png\"/>
                    <br>
                    <li>Futher modify formatted filename as desired in the save dialog</li>
                    <li>Select Save</li>
                </ol>
                <br>
                <p>Besides .gcode, the plugin will also work with other file types such as .3mf and .stl. Simply select from the<br>
                available file types in the save dialog.</p>
                <br>
                <h1>Format options</h1>
                <ul>
                    <li>base_name - the initial output filename from the object name and Cura's \"Add machine prefix to job name\" setting</li>
                    <li>job_name - same as base_name</li>
                    <li>printer_name - printer manufacturer and model</li>
                    <li>profile_name - name of the profile used for slicing e.g. Normal, Fine, Draft</li>
                    <li>cura_version - the Semantic version of Cura e.g. 4.4.0</li>
                    <li>object_count - number of objects on the build plate</li>
                    <li>layer_height - layer height/thickness, vertical resolution (mm)</li>
                    <li>machine_nozzle_size - nozzle diameter e.g. 0.2 mm, 0.4 mm, 0.6 mm</li>
                    <li>line_width - line/nozzle width e.g. 0.2 mm, 0.4 mm, 0.6 mm</li>
                    <li>wall thickness - thickness of shell walls (mm)</li>
                    <li>infill_sparse_density - infill percentage (%)</li>
                    <li>infill_pattern - infill pattern e.g grid, lines, triangles</li>
                    <li>top_bottom_pattern - pattern of the top and bottom layers e.g. lines, concentric, zig zag</li>
                    <li>brand - the brand of the filament e.g. Generic, Prusa, MatterHackers, eSun, etc.</li>
                    <li>material - material type e.g. PLA, PETG, ABS, etc.</li>
                    <li>material_diameter - filament size e.g. 1.75 mm, 3 mm</li>
                    <li>material_print_temperature - material/nozzle temperature (°C)</li>
                    <li>material_bed_temperature - build plate temperature (°C)</li>
                    <li>material_flow - extruded material flow rate (%)</li>
                    <li>speed_print - print speed (mm/s)</li>
                    <li>retraction_combing - combing mode</li>
                    <li>magic_spiralize - spiralize outer contour, vase mode</li>
                    <li>print_time - total print time in HHMMSS</li>
                    <li>print_time_days - print time in days</li>
                    <li>print_time_hours - print time in hours</li>
                    <li>print_time_hours_all - print_time_days * 24 + print_time_hours</li>
                    <li>print_time_minutes - print time in minutes</li>
                    <li>print_time_seconds - print time in seconds</li>
                    <li>material_weight - printed material weight (g)</li>
                    <li>material_length - printed material length (m)</li>
                    <li>material_cost - printed material cost</li>
                </ul>
                <br>
                <p>For the full list please refer to <a href=\"https://github.com/Ultimaker/Cura/blob/master/resources/i18n/fdmprinter.def.json.pot\">fdmprinter.def.json.pot</a></p>
                <br>"
        }
    }

    rightButtons: Button
    {
        text: "Close"
        iconName: "dialog-close"
        onClicked:
        {
            base.visible = false;
        }
    }
}
