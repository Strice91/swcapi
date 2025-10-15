import importlib.resources as res
from typing import ClassVar

from dynaconf import Dynaconf, Validator, loaders

PACKAGE_ROOT = res.files("swcapi")
PROJECT_ROOT = PACKAGE_ROOT.parent
CONFIG_ROOT = PROJECT_ROOT / "config"


class Config(Dynaconf):
    updatable: ClassVar = {".secrets.toml": ["apikey"], "settings.toml": ["test", "foo"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        """
        Intercepts setting assignment (e.g., config.test = "new_value")
        to find the correct file and write the update.
        """
        super().__setattr__(name, value)

        target_file = None
        for file_path, settings_list in self.updatable.items():
            if name in settings_list:
                target_file = file_path
                break

        if target_file:
            self._write_config(target_file, name, value)

    def _write_config(self, file_name: str, name: str, value):
        """
        Writes a single setting update to the specified file_name.
        """
        if not getattr(self, "SETTINGS_FILE_FOR_DYNACONF", []) or getattr(self, "ROOT_PATH_FOR_DYNACONF") is None:
            print("ERROR: Dynaconf environment variables not set. Cannot write config.")
            return
        # Store the updated value in the according config file
        file = self.ROOT_PATH_FOR_DYNACONF / file_name
        loaders.write(str(file), {name: value}, merge=True)


settings = Config(
    root_path=CONFIG_ROOT,
    load_dotenv=True,
    merge_enabled=True,
    envvar_prefix="",
    settings_files=[".secrets.toml", "settings.toml"],
)
