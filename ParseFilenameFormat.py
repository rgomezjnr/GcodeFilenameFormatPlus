import re

# Substitute print setting values in filename format
def parseFilenameFormat(print_settings, filename_format):
    for setting, value in print_settings.items():
        filename_format = filename_format.replace("[" + setting + "]", str(value))

    filename = re.sub('[^A-Za-z0-9.,_\-%°$£€#\[\]\(\)\|\+\'\" ]+', '', filename_format)

    return filename
