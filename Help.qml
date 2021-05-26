// LGPLv3

import UM 1.2 as UM
import QtQuick 2.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.3

UM.Dialog
{
    id: base
    title: "Gcode Filename Format Plus - Help"
    width: 700 * screenScaleFactor
    height: 675 * screenScaleFactor
    minimumWidth: 700 * screenScaleFactor

    ScrollView {
        width: parent.width
        height: parent.height
        horizontalScrollBarPolicy: Qt.ScrollBarAlwaysOff

        Text
        {
            onLinkActivated: Qt.openUrlExternally(link)

            text:
                "<h1>Default filename format:</h1>
                <p>[abbr_machine] [base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]%<br>
                ext1 [material_print_temperature]C bed [material_bed_temperature]C</p>
                <br>
                <h1>Example filename output:</h1>
                <p>PI3MK3M paperclip Generic PLA lw 0.4mm lh 0.2mm if 20% ext1 200C bed 60C.gcode</p>
                <br>
                <h1>Usage</h1>
                <ol>
                    <li>Specify filename format using Extensions -> Gcode Filename Format Plus -> Edit Format</li>
                    <br>
                    <br>
                    <img src=\"images/edit-format-dialog.png\"/>
                    <br>
                    <li>Slice object</li>
                    <li>Select Save to Disk button, or File -> Export, or send job to printer</li>
                </ol>
                <br>
                <p>Besides .gcode, the plugin also works with other file types such as .3mf and .stl. Simply select from the<br>
                available file types in the save dialog. Additionally, GFF+ will pass the custom job name to an OctoPrint server<br>
                when using the <a href=\"https://marketplace.ultimaker.com/app/cura/plugins/fieldofview/OctoPrintPlugin\">OctoPrint Connection</a> plugin.</p>
                <br>
                <h1>Format options</h1>
                <ul>
                    <li>base_name - the initial output filename from the object name and Cura's \"Add machine prefix to job name\" setting</li>
                    <li>job_name - same as base_name</li>
                    <li>abbr_machine - abbreviated printer machine name</li>
                    <li>printer_name - printer manufacturer and model</li>
                    <li>profile_name - name of the profile used for slicing e.g. Normal, Fine, Draft</li>
                    <li>cura_version - the Semantic version of Cura e.g. 4.4.0</li>
                    <li>object_count - number of objects on the build plate</li>
                    <li>layer_height - layer height/thickness, vertical resolution (mm)</li>
                    <li>machine_nozzle_size - nozzle diameter e.g. 0.2 mm, 0.4 mm, 0.6 mm</li>
                    <li>line_width - line/nozzle width e.g. 0.2 mm, 0.4 mm, 0.6 mm</li>
                    <li>wall_thickness - thickness of shell walls (mm)</li>
                    <li>infill_sparse_density - infill percentage (%)</li>
                    <li>infill_pattern - infill pattern e.g grid, lines, triangles</li>
                    <li>top_bottom_pattern - pattern of the top and bottom layers e.g. lines, concentric, zig zag</li>
                    <li>brand - the brand of the filament e.g. Generic, Prusa, MatterHackers, eSun, etc.</li>
                    <li>material - material type e.g. PLA, PETG, ABS, etc.</li>
                    <li>material_diameter - filament size e.g. 1.75 mm, 3 mm</li>
                    <li>material_print_temperature - material/nozzle temperature (°C)</li>
                    <li>material_bed_temperature - build plate temperature (°C)</li>
                    <li>material_flow - extruded material flow rate (%)</li>
                    <li>material_weight - printed material weight (g)</li>
                    <li>material_length - printed material length (m)</li>
                    <li>material_cost - printed material cost</li>
                    <li>color_name - material color</li>
                    <li>speed_print - print speed (mm/s)</li>
                    <li>retraction_combing - combing mode</li>
                    <li>magic_spiralize - spiralize outer contour, vase mode</li>
                    <li>print_time - total print time in HHMMSS</li>
                    <li>print_time_days - print time in days</li>
                    <li>print_time_hours - print time in hours</li>
                    <li>print_time_hours_all - print_time_days * 24 + print_time_hours</li>
                    <li>print_time_minutes - print time in minutes</li>
                    <li>print_time_seconds - print time in seconds</li>
                    <li>date - current date in YYYY-MM-DD</li>
                    <li>time - current time in HH-MM</li>
                    <li>datetime - current time in YYYY-MM-DDTHHMMSS</li>
                    <li>year - current year in YYYY</li>
                    <li>month - current month in MM</li>
                    <li>day - current day in DD</li>
                    <li>hour - current hour in HH</li>
                    <li>minute - current minute in MM</li>
                </ul>
                <br>
                <p>For the full list please refer to <a href=\"https://github.com/Ultimaker/Cura/blob/master/resources/i18n/fdmprinter.def.json.pot\">fdmprinter.def.json.pot</a></p>
                <br>
                <h2>Multiple extruder options</h2>
                <p>For printers with multiple extruders, individual extruder settings can be specified by appending<br>
                the extruder number to the option.</p>
                <br>
                <p>Example filename format:</p>
                <br>
                <p>[abbr_machine] [base_name] ext1 [brand1] [material1] [material_print_temperature1]C [line_width1]mm<br>
                ext2 [brand2] [material2] [material_print_temperature2]C [line_width2]mm</p>
                <br>
                <p>Example filename output:</p>
                <br>
                <p>PI3MK3M paperclip ext1 Ultimaker ABS 255C 0.7mm ext2 Ultimaker Tough PLA 215C 0.35mm.gcode</p>
                <br>
                <h1>Support</h1>
                <p>If you find an issue or have any feedback please submit an issue on <a href=\"https://github.com/rgomezjnr/GcodeFilenameFormatPlus/issues\">GitHub</a>.</p>
                <br>
                <p>If you would like to show your support donations are greatly appeciated via:</p>
                <ul>
                    <li><a href=\"https://github.com/sponsors/rgomezjnr\">GitHub Sponsors</a></li>
                    <li><a href=\"https://paypal.me/rgomezjnr\">PayPal</a></li>
                    <li><a href=\"bitcoin:bc1qh46qmztl77d9dl8f6ezswvqdqxcaurrqegca2p\">Bitcoin</a> bc1qh46qmztl77d9dl8f6ezswvqdqxcaurrqegca2p</li>
                    <li><a href=\"ethereum:0xAB443e578c9eA629088e26A9009e44Ed40f68678\">Ethereum</a> 0xAB443e578c9eA629088e26A9009e44Ed40f68678</li>
                </ul>
                <br>
                <h1>Authors</h1>
                <ul>
                    <li><a href=\"https://github.com/rgomezjnr\">Robert Gomez, Jr</a></li>
                    <li><a href=\"https://github.com/mchan016\">Michael Chan</a></li>
                    <li><a href=\"https://github.com/geoffrey-young\">Geoffrey Young</a></li>
                </ul>
                <br>
                <h1>Source code</h1>
                <a href=\"https://github.com/rgomezjnr/GcodeFilenameFormatPlus\">https://github.com/rgomezjnr/GcodeFilenameFormatPlus</a>
                <br>
                <h1>License</h1>
                <a href=\"https://github.com/rgomezjnr/GcodeFilenameFormat/blob/master/LICENSE\">LGPLv3</a>"
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
