// AGPLv3

import UM 1.2 as UM
import QtQuick 2.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.1

UM.Dialog
{
    id: base
    title: "Gcode Filename Format"
    width: 600 * screenScaleFactor
    height: 90 * screenScaleFactor
    minimumWidth: 300 * screenScaleFactor
    minimumHeight: 90 * screenScaleFactor

    Label
    {
        id: label
        text: "Edit Format"
        anchors.top: base.top
        anchors.topMargin: 10 * screenScaleFactor
        anchors.left: base.left
        anchors.leftMargin: 10 * screenScaleFactor
    }

    TextField
    {
        id: textfield
        text: UM.Preferences.getValue("gcode_filename_format/filename_format")
        anchors.top: label.bottom
        anchors.topMargin: 5 * screenScaleFactor
        width: base.width - 15 * screenScaleFactor
    }

    leftButtons: Button
    {
        text: "Default"
        iconName: "dialog-default"
        onClicked: textfield.text = "[base_name] [brand] [material] lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]F bed [material_bed_temperature]F"
    }

    rightButtons: Button
    {
        text: "Close"
        iconName: "dialog-close"
        onClicked:
        {
            base.visible = false;
            UM.Preferences.setValue("gcode_filename_format/filename_format", textfield.text)
        }
    }
}
