# LGPLv3

import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Application import Application
from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Message import Message
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice import OutputDeviceError
from UM.i18n import i18nCatalog
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from typing import cast

catalog = i18nCatalog("uranium")

class GcodeFilenameFormatDevicePlugin(OutputDevicePlugin): #We need to be an OutputDevicePlugin for the plug-in system.
    ##  Called upon launch.
    #
    #   You can use this to make a connection to the device or service, and
    #   register the output device to be displayed to the user.
    def start(self):
        self.getOutputDeviceManager().addOutputDevice(GcodeFilenameFormat()) #Since this class is also an output device, we can just register ourselves.
        #You could also add more than one output devices here.
        #For instance, you could listen to incoming connections and add an output device when a new device is discovered on the LAN.

    ##  Called upon closing.
    #
    #   You can use this to break the connection with the device or service, and
    #   you should unregister the output device to be displayed to the user.
    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("gcode_filename_format") #Remove all devices that were added. In this case it's only one.

##  Implements an OutputDevice that supports saving to arbitrary local files.
class GcodeFilenameFormat(OutputDevice): #We need an actual device to do the writing.
    def __init__(self):
        super().__init__("gcode_filename_format")

        Application.getInstance().getPreferences().addPreference("gcode_filename_format/last_used_type", "")
        Application.getInstance().getPreferences().addPreference("gcode_filename_format/dialog_save_path", "")

        self.setName(catalog.i18nc("@item:inmenu", "Gcode Filename Format")) #Human-readable name (you may want to internationalise this). Gets put in messages and such.
        self.setShortDescription(catalog.i18nc("@action:button Preceded by 'Ready to'.", "Save Gcode")) #This is put on the save button.
        self.setDescription(catalog.i18nc("@info:tooltip", "Save Gcode"))
        self.setIconName("save")


        self._writing = False


    ##  Request the specified nodes to be written to a file.
    #
    #   \param nodes A collection of scene nodes that should be written to the
    #   file.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param limit_mimetypes Should we limit the available MIME types to the
    #   MIME types available to the currently active machine?
    #   \param kwargs Keyword arguments.
    def requestWrite(self, nodes, file_name = None, limit_mimetypes = None, file_handler = None, **kwargs):
        if self._writing:
            raise OutputDeviceError.DeviceBusyError()

        application = cast(CuraApplication, Application.getInstance())
        machine_manager = application.getMachineManager()
        global_stack = machine_manager.activeMachine

        first_extruder_stack = ExtruderManager.getInstance().getActiveExtruderStacks()[0]

        # Get all current settings in a dictionary
        print_setting = self.getPrintSettings(global_stack, first_extruder_stack)

        # Get list of modified print settings using SliceInfoPlugin
        slice_info = application._plugin_registry.getPluginObject("SliceInfoPlugin")
        modified_print_settings = slice_info._getUserModifiedSettingKeys()

        Logger.log("d", "modified_print_settings = %s", modified_print_settings)

        machine_id = global_stack.definition.getId()
        manufacturer = global_stack.definition.getMetaDataEntry("manufacturer", "")
        Logger.log("d", "machine_id = %s", machine_id)
        Logger.log("d", "manufacturer = %s", manufacturer)

        # Set up and display file dialog
        dialog = QFileDialog()

        dialog.setWindowTitle(catalog.i18nc("@title:window", "Save to File"))
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        # Ensure platform never ask for overwrite confirmation since we do this ourselves
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

        # Find the first available preferred mime type
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
                file_name += self.filenameTackOn(print_setting)
                if file_name:
                    file_name += "." + item["extension"]

        # CURA-6411: This code needs to be before dialog.selectFile and the filters, because otherwise in macOS (for some reason) the setDirectory call doesn't work.
        stored_directory = Application.getInstance().getPreferences().getValue("gcode_filename_format/dialog_save_path")
        dialog.setDirectory(stored_directory)

        # Add the file name before adding the extension to the dialog
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

        # Get file name from file dialog
        file_name = dialog.selectedFiles()[0]
        Logger.log("d", "Writing to [%s]..." % file_name)

        if os.path.exists(file_name):
            result = QMessageBox.question(None, catalog.i18nc("@title:window", "File Already Exists"), catalog.i18nc("@label Don't translate the XML tag <filename>!", "The file <filename>{0}</filename> already exists. Are you sure you want to overwrite it?").format(file_name))
            if result == QMessageBox.No:
                raise OutputDeviceError.UserCanceledError()

        self.writeStarted.emit(self)

        # Actually writing file
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
            job.setAddToRecentFiles(True)  # The file will be added into the "recent files" list upon success
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


    def getPrintSettings(self, global_stack, first_extruder_stack):
        # Dictionary to hold results
        print_setting = dict()
        print_setting_abbreviations = dict()

        print_setting["material_brand"] = first_extruder_stack.material.getMetaData().get("brand", "")
        print_setting["material_type"] = first_extruder_stack.material.getMetaData().get("material", "")
        print_setting["layer_height"] = global_stack.userChanges.getProperty("layer_height", "value")
        print_setting["infill_sparse_density"] = first_extruder_stack.getProperty("infill_sparse_density", "value")
        print_setting["default_material_print_temperature"] = first_extruder_stack.getProperty("default_material_print_temperature", "value")
        print_setting["material_bed_temperature"] = global_stack.userChanges.getProperty("material_bed_temperature", "value")
        print_setting["infill_pattern"] = global_stack.userChanges.getProperty("infill_pattern", "value")
        print_setting["top_bottom_pattern"] = global_stack.userChanges.getProperty("top_bottom_pattern", "value")
        print_setting["retraction_combing"] = global_stack.userChanges.getProperty("retraction_combing", "value")

        # get default values if user did not change value
        if (print_setting.get("layer_height") is None):
            print_setting["layer_height"] = global_stack.getProperty("layer_height", "value")
        if (print_setting.get("infill_sparse_density") is None):
            print_setting["infill_sparse_density"] = global_stack.extruders.getProperty("infill_sparse_density", "value")
        if (print_setting.get("default_material_print_temperature") is None):
            print_setting["default_material_print_temperature"] = global_stack.extruders.getProperty("default_material_print_temperature", "value")
        if (print_setting.get("material_bed_temperature") is None):
            print_setting["material_bed_temperature"] = global_stack.getProperty("material_bed_temperature", "value")
        if (print_setting.get("infill_pattern") is None):
            print_setting["infill_pattern"] = global_stack.getProperty("infill_pattern", "value")
        if (print_setting.get("top_bottom_pattern") is None):
            print_setting["top_bottom_pattern"] = global_stack.getProperty("top_bottom_pattern", "value")
        if (print_setting.get("retraction_combing") is None):
            print_setting["retraction_combing"] = global_stack.getProperty("retraction_combing", "value")

        Logger.log("d", "material_brand = %s", print_setting.get("material_brand"))
        Logger.log("d", "material_type = %s", print_setting.get("material_type"))
        Logger.log("d", "layer_height = %s", print_setting.get("layer_height"))
        Logger.log("d", "infill_sparse_density = %s", print_setting.get("infill_sparse_density"))
        Logger.log("d", "default_material_print_temperature = %s", print_setting.get("default_material_print_temperature"))
        Logger.log("d", "material_bed_temperature = %s", print_setting.get("material_bed_temperature"))
        Logger.log("d", "infill_pattern = %s", print_setting.get("infill_pattern"))
        Logger.log("d", "top_bottom_pattern = %s", print_setting.get("top_bottom_pattern"))
        Logger.log("d", "retraction_combing = %s", print_setting.get("retraction_combing"))

        print_setting_abbreviations["mtl-brand"] = print_setting["material_brand"]
        print_setting_abbreviations["mtl-type"] = print_setting["material_type"]
        print_setting_abbreviations["lh"] = print_setting["layer_height"]
        print_setting_abbreviations["inf"] = print_setting["infill_sparse_density"]
        print_setting_abbreviations["mtl-temp"] = print_setting["default_material_print_temperature"]
        print_setting_abbreviations["bed-temp"] = print_setting["material_bed_temperature"]
        print_setting_abbreviations["inf-pat"] = print_setting["infill_pattern"]
        print_setting_abbreviations["tb-pat"] = print_setting["top_bottom_pattern"]
        print_setting_abbreviations["comb"] = print_setting["retraction_combing"]

        return print_setting_abbreviations


    # Structure captured print settings into a tack on for file name
    def filenameTackOn(self, print_setting):
        tack_on = ""
        for setting, value in print_setting.items():
            tack_on += " " + setting + " " + str(value)

        return tack_on


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
        except (OSError, PermissionError): #When you don't have the rights to do the final flush or the disk is full.
            message = Message(catalog.i18nc("@info:status", "Something went wrong saving to <filename>{0}</filename>: <message>{1}</message>").format(job.getFileName(), str(job.getError())), title = catalog.i18nc("@info:title", "Error"))
            message.show()
            self.writeError.emit(self)

    def _onMessageActionTriggered(self, message, action):
        if action == "open_folder" and hasattr(message, "_folder"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(message._folder))
