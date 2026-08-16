from pathlib import Path
import shutil
import yaml


class Config:
    def __init__(
        self,
        config_path: str = "config.yaml",
        default_path: str = "config.default.yaml"
    ):

        config_file = Path(config_path)
        default_file = Path(default_path)

        self.created_from_default = False

        if not config_file.exists():
            if not default_file.exists():
                raise FileNotFoundError(f"Default configuration file not found: {default_path}")

            shutil.copy(default_file, config_file)
            self.created_from_default = True


        with open(config_file, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

        if not self.data:
            raise ValueError(f"Configuration file is empty: {config_path}")
