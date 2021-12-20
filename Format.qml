// AGPLv3

import UM 1.2 as UM
import QtQuick 2.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.1

UM.Dialog
{
    id: base
    title: "Gcode Filename Format Plus - Edit Format"
    width: 600 * screenScaleFactor
    height: 70 * screenScaleFactor
    minimumWidth: 300 * screenScaleFactor
    minimumHeight: 70 * screenScaleFactor

    UM.TooltipArea
    {
        width: childrenRect.width
        height: childrenRect.height
        text:
            "<h2>Format options</h2>
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
                    <li>scale - uniform scale of the object (%)</li>
                    <li>scale_x - scale of the object on the x axis (%)</li>
                    <li>scale_y - scale of the object on the y axis (%)</li>
                    <li>scale_z - scale of the object on the z axis (%)</li>
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
                </ul>"

        TextField
        {
            id: textfield
            text: UM.Preferences.getValue("gcode_filename_format_plus/filename_format")
            width: base.width - 15 * screenScaleFactor
        }
    }

    leftButtons: Button
    {
        text: "Default"
        iconName: "dialog-default"
        onClicked: textfield.text = "[abbr_machine] [base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C"
    }

    rightButtons: Button
    {
        text: "Close"
        iconName: "dialog-close"
        onClicked:
        {
            base.visible = false;
            UM.Preferences.setValue("gcode_filename_format_plus/filename_format", textfield.text)
        }
    }
}
