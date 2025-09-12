import importlib.resources as res
from typing import ClassVar

from dynaconf import Dynaconf, Validator, loaders

PACKAGE_ROOT = res.files("swcapi")
PROJECT_ROOT = PACKAGE_ROOT.parent
CONFIG_ROOT = PROJECT_ROOT / "config"



class Config(Dynaconf):
    updatable: ClassVar = ["apikey"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self.updatable:
            self._write_config(name, value)

    def _write_config(self, name, value):
        if not getattr(self, "SETTINGS_FILE_FOR_DYNACONF", []) or getattr(self, "ROOT_PATH_FOR_DYNACONF") is None:
            return
        # Store the updated value in the first of the settings files
        file = self.ROOT_PATH_FOR_DYNACONF / self.SETTINGS_FILE_FOR_DYNACONF[0]
        loaders.write(str(file), {name: value}, merge=True)

settings = Config(
    root_path=CONFIG_ROOT,
    load_dotenv=True,
    merge_enabled=True,
    envvar_prefix="",
    settings_files=[".secrets.toml", "settings.toml"],
)
