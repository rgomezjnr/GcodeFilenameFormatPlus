# LGPLv3

import os
import re

from typing import cast

from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Extension import Extension
from UM.Application import Application
from UM.Qt.Duration import DurationFormat
from UM.PluginRegistry import PluginRegistry

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

catalog = i18nCatalog("cura")

DEFAULT_FILENAME_FORMAT = "[base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C"

class GcodeFilenameFormat(Extension, QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        Application.getInstance().getPreferences().addPreference("gcode_filename_format/filename_format", DEFAULT_FILENAME_FORMAT)

        self.setMenuName("Gcode Filename Format")
        self.addMenuItem("Edit Format", self.editFormat)
        self.format_window = None
        self.addMenuItem("Help", self.help)
        self.help_window = None

        self._application = CuraApplication.getInstance()
        self._print_information = None

        self._application.engineCreatedSignal.connect(self._onEngineCreated)

    def editFormat(self):
        if not self.format_window:
            self.format_window = self._createDialogue()
        self.format_window.show()

    def _createDialogue(self):
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "Format.qml")
        component = Application.getInstance().createQmlComponent(qml_file_path)

        return component

    def help(self):
        if not self.help_window:
            self.help_window = self._createHelpDialog()
        self.help_window.show()

    def _createHelpDialog(self):
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "Help.qml")
        component = Application.getInstance().createQmlComponent(qml_file_path)

        return component

    def _onEngineCreated(self) -> None:
        self._print_information = self._application.getPrintInformation()
        self._print_information.currentPrintTimeChanged.connect(self._triggerJobNameUpdate)
        self._print_information.materialWeightsChanged.connect(self._triggerJobNameUpdate)
        self._print_information.jobNameChanged.connect(self._onJobNameChanged)

        self._global_stack = None
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        self._onMachineChanged()

    def _onJobNameChanged(self) -> None:
        if self._print_information._is_user_specified_job_name:
            job_name = self._print_information._job_name
            if job_name == catalog.i18nc("@text Print job name", "Untitled"):
                return

            self._print_information._is_user_specified_job_name = False

    def _onMachineChanged(self) -> None:
        if self._global_stack:
            self._global_stack.containersChanged.disconnect(self._triggerJobNameUpdate)
            self._global_stack.metaDataChanged.disconnect(self._triggerJobNameUpdate)

        self._global_stack = CuraApplication.getInstance().getGlobalContainerStack()

        if self._global_stack:
            self._global_stack.containersChanged.connect(self._triggerJobNameUpdate)
            self._global_stack.metaDataChanged.connect(self._triggerJobNameUpdate)

    def _triggerJobNameUpdate(self, *args, **kwargs) -> None:
        self._print_information._job_name = ""      # Fixes filename clobbering from repeated calls

        application = cast(CuraApplication, Application.getInstance())
        machine_manager = application.getMachineManager()
        global_stack = machine_manager.activeMachine
        print_information = application.getPrintInformation()

        file_name = print_information.jobName
        filename_format = Application.getInstance().getPreferences().getValue("gcode_filename_format/filename_format")

        file_name = self.parseFilenameFormat(filename_format, file_name, application, global_stack)
        file_name = print_information._abbr_machine + "_" + print_information.baseName + file_name
        Logger.log("d", "parsed file_name = %s", file_name)

        self._print_information._job_name = file_name

    # Perform lookup and replacement of print setting values in filename format
    def parseFilenameFormat(self, filename_format, file_name, application, global_stack):
        first_extruder_stack = ExtruderManager.getInstance().getActiveExtruderStacks()[0]
        print_information = application.getPrintInformation()
        print_settings = dict()

        job_name = print_information.jobName
        printer_name = global_stack.getName()
        print_time = print_information.currentPrintTime.getDisplayString(DurationFormat.Format.ISO8601)
        print_time_days = print_information.currentPrintTime.days
        print_time_hours = print_information.currentPrintTime.hours
        print_time_hours_all = print_time_days * 24 + print_time_hours
        print_time_minutes = print_information.currentPrintTime.minutes
        print_time_seconds = print_information.currentPrintTime.seconds
        material_weight = print_information.materialWeights
        material_length = print_information.materialLengths
        material_cost = print_information.materialCosts

        tokens = re.split(r'\W+', filename_format)      # TODO: split on brackets only

        for t in tokens:
            stack1 = first_extruder_stack.material.getMetaData().get(t, "")
            stack2 = global_stack.userChanges.getProperty(t, "value")
            stack3 = first_extruder_stack.getProperty(t, "value")

            if stack1 is not None and stack1 is not "":
                print_settings[t] = stack1
            elif stack2 is not None and stack2 is not "":
                print_settings[t] = stack2
            elif stack3 is not None and stack3 is not "":
                print_settings[t] = stack3
            else:
                print_settings[t] = None

        print_settings["base_name"] = file_name
        print_settings["job_name"] = job_name
        print_settings["printer_name"] = printer_name
        print_settings["print_time"] = print_time
        print_settings["print_time_days"] = print_time_days
        print_settings["print_time_hours"] = print_time_hours
        print_settings["print_time_hours_all"] = print_time_hours_all
        print_settings["print_time_minutes"] = print_time_minutes
        print_settings["print_time_seconds"] = print_time_seconds
        #print_settings["material_weight"] = int(material_weight[0])
        #print_settings["material_length"] = round(float(material_length[0]), 1)
        #print_settings["material_cost"] = round(float(material_cost[0]), 2)

        for setting, value in print_settings.items():
            Logger.log("d", "print_settings[%s] = %s", setting, value)

        for setting, value in print_settings.items():
            filename_format = filename_format.replace("[" + setting + "]", str(value))

        filename_format = re.sub('[^A-Za-z0-9._\-%°$£€ ]+', '', filename_format)
        #Logger.log("d", "filename_format = %s", filename_format)

        return filename_format
