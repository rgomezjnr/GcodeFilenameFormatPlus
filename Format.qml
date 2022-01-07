// AGPLv3

import UM 1.2 as UM
import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Controls 1.4

UM.Dialog
{
    id: base
    title: "Gcode Filename Format Plus - Edit Format"
    width: 600 * screenScaleFactor
    height: 100 * screenScaleFactor
    minimumWidth: 300 * screenScaleFactor
    minimumHeight: 100 * screenScaleFactor

    TextField
    {
        id: textfield
        text: UM.Preferences.getValue("gcode_filename_format_plus/filename_format")
        width: base.width - 15 * screenScaleFactor
    }

    UM.TooltipArea
    {
        width: childrenRect.width
        height: childrenRect.height
        text: "Specify maximum filename character length, not including file extension. Excess characters generated from format will be truncated. Use value 0 to disable limit."

        Label
        {
            text: "Filename length limit"
            y: 35

            SpinBox
            {
                id: spinbox
                x: 125
                y: -4
                value: UM.Preferences.getValue("gcode_filename_format_plus/max_filename_length")
                maximumValue: 255
            }
        }
    }

    leftButtons: Button
    {
        text: "Default"
        iconName: "dialog-default"
        onClicked:
        {
            textfield.text = "[abbr_machine] [base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C"
            spinbox.value = 80
        }
    }

    rightButtons: Button
    {
        text: "Close"
        iconName: "dialog-close"
        onClicked:
        {
            base.visible = false;
            UM.Preferences.setValue("gcode_filename_format_plus/filename_format", textfield.text)
            UM.Preferences.setValue("gcode_filename_format_plus/max_filename_length", spinbox.value)
        }
    }
}
