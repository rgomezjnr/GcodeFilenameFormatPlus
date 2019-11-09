//Copyright (c) 2018 Ultimaker B.V.
//This example is released under the terms of the AGPLv3 or higher.

import UM 1.1 as UM //This allows you to use all of Uranium's built-in QML items.
import QtQuick 2.2 //This allows you to use QtQuick's built-in QML items.
import QtQuick.Controls 1.1

UM.Dialog //Creates a modal window that pops up above the interface.
{
    id: base

    width: 150 * screenScaleFactor
    height: 50 * screenScaleFactor
    minimumWidth: 150 * screenScaleFactor
    minimumHeight: 50 * screenScaleFactor

    Label //Creates a bit of text.
    {
        //This aligns the text to the top-left corner of the dialogue window.
        anchors.top: base.top //Reference the dialogue window by its ID: "base".
        anchors.topMargin: 10 * screenScaleFactor
        anchors.left: base.left
        anchors.leftMargin: 10 * screenScaleFactor

        text: "Edit Format"
    }
}
