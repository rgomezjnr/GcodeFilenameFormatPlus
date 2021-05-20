# LGPLv3

import re
import os.path

from typing import cast

from PyQt5.QtCore import QUrl, Qt, QDate, QDateTime
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtQml import QQmlComponent, QQmlContext
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Extension import Extension
from UM.Application import Application
from UM.Qt.Duration import DurationFormat
from UM.PluginRegistry import PluginRegistry
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Version import Version

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager
from cura.UI.ObjectsModel import ObjectsModel

from GcodeFilenameFormatPlus.ParseFilenameFormat import parseFilenameFormat

catalog = i18nCatalog("cura")

DEFAULT_FILENAME_FORMAT = "[abbr_machine] [base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C"

class GcodeFilenameFormatPlus(Extension, QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        Application.getInstance().getPreferences().addPreference("gcode_filename_format_plus/filename_format", DEFAULT_FILENAME_FORMAT)

        self.setMenuName("Gcode Filename Format Plus")
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
        filename_format = Application.getInstance().getPreferences().getValue("gcode_filename_format_plus/filename_format")
        #print_settings = dict()

        print_settings = self.getPrintSettings(filename_format)
        file_name = parseFilenameFormat(print_settings, filename_format)
        Logger.log("d", "parsed file_name = %s", file_name)

        self._print_information._job_name = file_name

    # Retrieve print setting values from Cura/Uranium
    def getPrintSettings(self, filename_format):
        application = cast(CuraApplication, Application.getInstance())
        print_information = application.getPrintInformation()
        machine_manager = application.getMachineManager()
        global_stack = machine_manager.activeMachine
        first_extruder_stack = ExtruderManager.getInstance().getActiveExtruderStacks()[0]
        active_extruder_stacks = ExtruderManager.getInstance().getActiveExtruderStacks()
        print_settings = dict()
        multi_extruder_settings = dict()

        base_name = print_information.baseName
        abbr_machine = print_information._abbr_machine
        printer_name = global_stack.getName()
        profile_name = machine_manager.activeQualityOrQualityChangesName
        print_time = print_information.currentPrintTime.getDisplayString(DurationFormat.Format.ISO8601)
        print_time_days = print_information.currentPrintTime.days
        print_time_hours = print_information.currentPrintTime.hours
        print_time_hours_all = print_time_days * 24 + print_time_hours
        print_time_minutes = print_information.currentPrintTime.minutes
        print_time_seconds = print_information.currentPrintTime.seconds
        material_weight = print_information.materialWeights
        material_length = print_information.materialLengths
        material_cost = print_information.materialCosts
        date = QDate.currentDate().toString(format=Qt.ISODate)
        time = QDateTime.currentDateTime().toString("HH-mm")
        datetime = QDateTime.currentDateTime().toString(format=Qt.ISODate)
        year =  QDateTime.currentDateTime().toString("yyyy")
        month = QDateTime.currentDateTime().toString("MM")
        day = QDateTime.currentDateTime().toString("dd")
        hour = QDateTime.currentDateTime().toString("HH")
        minute = QDateTime.currentDateTime().toString("mm")
        object_count = self.getObjectCount()
        cura_version = Version(Application.getInstance().getVersion())

        tokens = re.split(r'\W+', filename_format)      # TODO: split on brackets only

        for t in tokens:
            Logger.log("d", "t = %s", t)

            stack1 = first_extruder_stack.material.getMetaData().get(t, "")
            stack2 = global_stack.userChanges.getProperty(t, "value")
            stack3 = first_extruder_stack.getProperty(t, "value")

            if stack1 is not None and stack1 != "":
                if type(stack1) is float:
                    print_settings[t] = round(stack1, 2)
                else:
                    print_settings[t] = stack1
            elif stack2 is not None and stack2 != "":
                if type(stack2) is float:
                    print_settings[t] = round(stack2, 2)
                else:
                    print_settings[t] = stack2
            elif stack3 is not None and stack3 != "":
                if type(stack3) is float:
                    print_settings[t] = round(stack3, 2)
                else:
                    print_settings[t] = stack3
            else:
                print_settings[t] = None

            #user_change_property = global_stack.userChanges.getProperty(t, "value")
            #Logger.log("d", "user_change_property = %s", user_change_property)

            #if user_change_property is not None and user_change_property != "":
            #    print_settings[t] = user_change_property

            for a in active_extruder_stacks:
                extruder_position = a.position
                Logger.log("d", "extruder_position = %s", extruder_position)

                try:
                    Logger.log("d", "t[:-1] = %s", t[:-1])
                    stack1 = a.material.getMetaData().get(t[:-1], "")
                    stack2 = a.getProperty(t[:-1], "value")
                    Logger.log("d", "stack1 = %s", stack1)
                    Logger.log("d", "stack2 = %s", stack2)

                    if stack1 is not None and stack1 != "" and stack1 != 0 and extruder_position + 1 == int(t[-1]):
                        Logger.log("d", "stack1 multi_extruder_settings[%s] = %s", t, stack1)
                        if type(stack1) is float:
                            multi_extruder_settings[t] = round(stack1, 2)
                        else:
                            multi_extruder_settings[t] = stack1
                        multi_extruder_settings[t] = round(stack1, 2)
                    elif stack2 is not None and stack2 != "" and stack2 != 0 and extruder_position + 1 == int(t[-1]):
                        Logger.log("d", "stack2 multi_extruder_settings[%s] = %s", t, stack2)
                        if type(stack2) is float:
                            multi_extruder_settings[t] = round(stack2, 2)
                        else:
                            multi_extruder_settings[t] = stack2
                    #else:
                    #    Logger.log("d", "multi_extruder_settings[%s] = None", t)
                    #    #print_settings[t] = None
                    #    multi_extruder_settings[t] = None
                except TypeError:
                    pass
                except ValueError:
                    pass

        print_settings["base_name"] = base_name
        print_settings["job_name"] = base_name
        print_settings["abbr_machine"] = abbr_machine
        print_settings["printer_name"] = printer_name
        print_settings["profile_name"] = profile_name
        print_settings["print_time"] = print_time
        print_settings["print_time_days"] = print_time_days
        print_settings["print_time_hours"] = print_time_hours
        print_settings["print_time_hours_all"] = print_time_hours_all
        print_settings["print_time_minutes"] = print_time_minutes
        print_settings["print_time_seconds"] = print_time_seconds
        print_settings["date"] = date
        print_settings["time"] = time
        print_settings["datetime"] = datetime
        print_settings["year"] = year
        print_settings["month"] = month
        print_settings["day"] = day
        print_settings["hour"] = hour
        print_settings["minute"] = minute
        print_settings["object_count"] = object_count
        print_settings["cura_version"] = cura_version

        try:
            if len(material_weight) > 1:
                print_settings["material_weight1"] = round(float(material_weight[0]))
                print_settings["material_weight2"] = round(float(material_weight[1]))
                print_settings["material_weight"] = round(float(material_weight[0] + material_weight[1]))
            else:
                print_settings["material_weight"] = round(float(material_weight[0]))
        except IndexError:
            pass

        try:
            if len(material_length) > 1:
                print_settings["material_length1"] = round(float(material_length[0]), 2)
                print_settings["material_length2"] = round(float(material_length[1]), 2)
                print_settings["material_length"] = round(float(material_length[0] + material_length[1]), 2)
            else:
                print_settings["material_length"] = round(float(material_length[0]), 2)
        except IndexError:
            pass

        try:
            if len(material_cost) > 1:
                print_settings["material_cost1"] = round(float(material_cost[0]), 2)
                print_settings["material_cost2"] = round(float(material_cost[1]), 2)
                print_settings["material_cost"] = round(float(material_cost[0] + material_cost[1]), 2)
            else:
                print_settings["material_cost"] = round(float(material_cost[0]), 2)
        except IndexError:
            pass

        print_settings.update(multi_extruder_settings)
        Logger.log("d", "print_settings = %s", print_settings)

        return print_settings

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

    # Get list of modified print settings using SliceInfoPlugin
    def getModifiedPrintSettings(self, application, global_stack):
        slice_info = application._plugin_registry.getPluginObject("SliceInfoPlugin")
        modified_print_settings = slice_info._getUserModifiedSettingKeys()

        machine_id = global_stack.definition.getId()
        manufacturer = global_stack.definition.getMetaDataEntry("manufacturer", "")

    def getObjectCount(self) -> int:
        count = 0

        for node in DepthFirstIterator(Application.getInstance().getController().getScene().getRoot()):
            if not ObjectsModel()._shouldNodeBeHandled(node):
                continue

            count += 1

        return count
