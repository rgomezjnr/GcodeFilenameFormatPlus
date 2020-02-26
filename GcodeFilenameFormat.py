# LGPLv3

import os
import sys
import re

from typing import cast

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtQml import QQmlComponent, QQmlContext
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Logger import Logger
from UM.Message import Message
from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.Mesh.MeshWriter import MeshWriter
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.OutputDevice import OutputDeviceError
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

catalog = i18nCatalog("uranium")

DEFAULT_FILENAME_FORMAT = "[base_name] [brand] [material] lw [line_width]mm lh [layer_height]mm if [infill_sparse_density]% ext1 [material_print_temperature]C bed [material_bed_temperature]C"

class GcodeFilenameFormatDevicePlugin(OutputDevicePlugin):
    def start(self):
        self.getOutputDeviceManager().addOutputDevice(GcodeFilenameFormat())

    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("gcode_filename_format")

# Inherit from OutputDevice class for writing filename format to file, and from Extension class to provide interface for setting filename format
class GcodeFilenameFormat(OutputDevice, Extension):
    def __init__(self):
        super().__init__("gcode_filename_format")

        Application.getInstance().getPreferences().addPreference("gcode_filename_format/last_used_type", "")
        Application.getInstance().getPreferences().addPreference("gcode_filename_format/dialog_save_path", "")
        Application.getInstance().getPreferences().addPreference("gcode_filename_format/filename_format", DEFAULT_FILENAME_FORMAT)

        self.setName(catalog.i18nc("@item:inmenu", "Gcode Filename Format"))
        self.setShortDescription(catalog.i18nc("@action:button Preceded by 'Ready to'.", "Save Gcode"))
        self.setDescription(catalog.i18nc("@info:tooltip", "Save Gcode"))
        self.setIconName("save")

        self._writing = False

        self.setMenuName("Gcode Filename Format")
        self.addMenuItem("Edit Format", self.editFormat)
        self.format_window = None

    def requestWrite(self, nodes, file_name = None, limit_mimetypes = None, file_handler = None, **kwargs):
        application = cast(CuraApplication, Application.getInstance())
        machine_manager = application.getMachineManager()
        global_stack = machine_manager.activeMachine

        filename_format = Application.getInstance().getPreferences().getValue("gcode_filename_format/filename_format")

        Logger.log("d", "filename_format = %s", filename_format)

        if filename_format is "":
            filename_format = DEFAULT_FILENAME_FORMAT

        if self._writing:
            raise OutputDeviceError.DeviceBusyError()

        self.getModifiedPrintSettings(application, global_stack)

        dialog = QFileDialog()

        dialog.setWindowTitle(catalog.i18nc("@title:window", "Save to File"))
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        dialog.setOption(QFileDialog.DontConfirmOverwrite)

        if sys.platform == "linux" and "KDE_FULL_SESSION" in os.environ:
            dialog.setOption(QFileDialog.DontUseNativeDialog)

        filters = []
        mime_types = []
        selected_filter = None

        if "preferred_mimetypes" in kwargs and kwargs["preferred_mimetypes"] is not None:
            preferred_mimetypes = kwargs["preferred_mimetypes"]
        else:
            preferred_mimetypes = Application.getInstance().getPreferences().getValue("gcode_filename_format/last_used_type")
        preferred_mimetype_list = preferred_mimetypes.split(";")

        if not file_handler:
            file_handler = Application.getInstance().getMeshFileHandler()

        file_types = file_handler.getSupportedFileTypesWrite()

        file_types.sort(key = lambda k: k["description"])
        if limit_mimetypes:
            file_types = list(filter(lambda i: i["mime_type"] in limit_mimetypes, file_types))

        file_types = [ft for ft in file_types if not ft["hide_in_file_dialog"]]

        if len(file_types) == 0:
            Logger.log("e", "There are no file types available to write with!")
            raise OutputDeviceError.WriteRequestFailedError(catalog.i18nc("@info:warning", "There are no file types available to write with!"))

        preferred_mimetype = None
        for mime_type in preferred_mimetype_list:
            if any(ft["mime_type"] == mime_type for ft in file_types):
                preferred_mimetype = mime_type
                break

        for item in file_types:
            type_filter = "{0} (*.{1})".format(item["description"], item["extension"])
            filters.append(type_filter)
            mime_types.append(item["mime_type"])
            if preferred_mimetype == item["mime_type"]:
                selected_filter = type_filter
                file_name = self.parseFilenameFormat(filename_format, file_name, application, global_stack)
                #file_name += self.filenameTackOn(print_setting)
                if file_name:
                    file_name += "." + item["extension"]

        stored_directory = Application.getInstance().getPreferences().getValue("gcode_filename_format/dialog_save_path")
        dialog.setDirectory(stored_directory)

        if file_name is not None:
            dialog.selectFile(file_name)

        dialog.setNameFilters(filters)
        if selected_filter is not None:
            dialog.selectNameFilter(selected_filter)

        if not dialog.exec_():
            raise OutputDeviceError.UserCanceledError()

        save_path = dialog.directory().absolutePath()
        Application.getInstance().getPreferences().setValue("gcode_filename_format/dialog_save_path", save_path)

        selected_type = file_types[filters.index(dialog.selectedNameFilter())]
        Application.getInstance().getPreferences().setValue("gcode_filename_format/last_used_type", selected_type["mime_type"])

        file_name = dialog.selectedFiles()[0]
        Logger.log("d", "Writing to [%s]..." % file_name)

        if os.path.exists(file_name):
            result = QMessageBox.question(None, catalog.i18nc("@title:window", "File Already Exists"), catalog.i18nc("@label Don't translate the XML tag <filename>!", "The file <filename>{0}</filename> already exists. Are you sure you want to overwrite it?").format(file_name))
            if result == QMessageBox.No:
                raise OutputDeviceError.UserCanceledError()

        self.writeStarted.emit(self)

        if file_handler:
            file_writer = file_handler.getWriter(selected_type["id"])
        else:
            file_writer = Application.getInstance().getMeshFileHandler().getWriter(selected_type["id"])

        try:
            mode = selected_type["mode"]
            if mode == MeshWriter.OutputMode.TextMode:
                Logger.log("d", "Writing to Local File %s in text mode", file_name)
                stream = open(file_name, "wt", encoding = "utf-8")
            elif mode == MeshWriter.OutputMode.BinaryMode:
                Logger.log("d", "Writing to Local File %s in binary mode", file_name)
                stream = open(file_name, "wb")
            else:
                Logger.log("e", "Unrecognised OutputMode.")
                return None

            job = WriteFileJob(file_writer, stream, nodes, mode)
            job.setFileName(file_name)
            job.setAddToRecentFiles(True)
            job.progress.connect(self._onJobProgress)
            job.finished.connect(self._onWriteJobFinished)

            message = Message(catalog.i18nc("@info:progress Don't translate the XML tags <filename>!", "Saving to <filename>{0}</filename>").format(file_name),
                              0, False, -1 , catalog.i18nc("@info:title", "Saving"))
            message.show()

            job.setMessage(message)
            self._writing = True
            job.start()
        except PermissionError as e:
            Logger.log("e", "Permission denied when trying to write to %s: %s", file_name, str(e))
            raise OutputDeviceError.PermissionDeniedError(catalog.i18nc("@info:status Don't translate the XML tags <filename>!", "Permission denied when trying to save <filename>{0}</filename>").format(file_name)) from e
        except OSError as e:
            Logger.log("e", "Operating system would not let us write to %s: %s", file_name, str(e))
            raise OutputDeviceError.WriteRequestFailedError(catalog.i18nc("@info:status Don't translate the XML tags <filename> or <message>!", "Could not save to <filename>{0}</filename>: <message>{1}</message>").format()) from e

    # Structure captured print settings into a tack on for file name
    def filenameTackOn(self, print_setting):
        tack_on = ""
        for setting, value in print_setting.items():
            tack_on += " " + setting + " " + str(value)

        return tack_on

    # Perform lookup and replacement of print setting values in filename format
    def parseFilenameFormat(self, filename_format, file_name, application, global_stack):
        first_extruder_stack = ExtruderManager.getInstance().getActiveExtruderStacks()[0]

        print_settings = dict()

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

        for setting, value in print_settings.items():
            filename_format = filename_format.replace("[" + setting + "]", str(value))

        Logger.log("d", "filename_format = %s", filename_format)

        return filename_format

    def _onJobProgress(self, job, progress):
        self.writeProgress.emit(self, progress)

    def _onWriteJobFinished(self, job):
        self._writing = False
        self.writeFinished.emit(self)
        if job.getResult():
            self.writeSuccess.emit(self)
            message = Message(catalog.i18nc("@info:status Don't translate the XML tags <filename>!", "Saved to <filename>{0}</filename>").format(job.getFileName()), title = catalog.i18nc("@info:title", "File Saved"))
            message.addAction("open_folder", catalog.i18nc("@action:button", "Open Folder"), "open-folder", catalog.i18nc("@info:tooltip", "Open the folder containing the file"))
            message._folder = os.path.dirname(job.getFileName())
            message.actionTriggered.connect(self._onMessageActionTriggered)
            message.show()
        else:
            message = Message(catalog.i18nc("@info:status Don't translate the XML tags <filename> or <message>!", "Could not save to <filename>{0}</filename>: <message>{1}</message>").format(job.getFileName(), str(job.getError())), lifetime = 0, title = catalog.i18nc("@info:title", "Warning"))
            message.show()
            self.writeError.emit(self)

        try:
            job.getStream().close()
        except (OSError, PermissionError):
            message = Message(catalog.i18nc("@info:status", "Something went wrong saving to <filename>{0}</filename>: <message>{1}</message>").format(job.getFileName(), str(job.getError())), title = catalog.i18nc("@info:title", "Error"))
            message.show()
            self.writeError.emit(self)

    def _onMessageActionTriggered(self, message, action):
        if action == "open_folder" and hasattr(message, "_folder"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(message._folder))

    def editFormat(self):
        if not self.format_window:
            self.format_window = self._createDialogue()
        self.format_window.show()

    def _createDialogue(self):
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "Format.qml")
        component = Application.getInstance().createQmlComponent(qml_file_path)

        return component

    # Get list of modified print settings using SliceInfoPlugin
    def getModifiedPrintSettings(self, application, global_stack):
        slice_info = application._plugin_registry.getPluginObject("SliceInfoPlugin")
        modified_print_settings = slice_info._getUserModifiedSettingKeys()

        machine_id = global_stack.definition.getId()
        manufacturer = global_stack.definition.getMetaDataEntry("manufacturer", "")
