# coding:utf-8
from enum import Enum

from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator)


class Config(QConfig):
    """ Config of application """
    
    # size of color block
    BLOCK_W = 106
    BLOCK_H = 52
    
    # folders
    outputFolder = ConfigItem(
        "Folders", "Output", "app/output", FolderValidator())

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2023
AUTHOR = "Jiajun Dong"
VERSION = "v0.1.0"
HELP_URL = "https://github.com/Djj646/NewColorTool/blob/main/ColorTool.md"
REPO_URL = "https://github.com/Djj646/NewColorTool"
EXAMPLE_URL = "https://github.com/Djj646/NewColorTool/blob/main/Examples.md"
SAISOMETHING_URL = "https://github.com/Djj646/NewColorTool/blob/main/SaySomething.md"
FEEDBACK_URL = "https://github.com/Djj646/NewColorTool/issues"
RELEASE_URL = "https://github.com/Djj646/NewColorTool/releases/latest"


cfg = Config()
qconfig.load('app/config/config.json', cfg)