from pathlib import Path
import shutil
import yaml


def resolve_under(base_dir: Path, path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


class Config:
    def __init__(
        self,
        config_path: str = "config.yaml",
        default_path: str = "config.default.yaml",
        base_dir: Path | None = None,
    ):

        self.base_dir = Path(base_dir).resolve() if base_dir is not None else Path.cwd()
        config_file = resolve_under(self.base_dir, config_path)
        default_file = resolve_under(self.base_dir, default_path)

        self.created_from_default = False

        if not config_file.exists():
            if not default_file.exists():
                raise FileNotFoundError(f"Default configuration file not found: {default_file}")

            shutil.copy(default_file, config_file)
            self.created_from_default = True


        with open(config_file, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

        if not self.data:
            raise ValueError(f"Configuration file is empty: {config_file}")

        
        required = (
            ("librehardwaremonitor", "url"),
            ("exporter", "scrape_interval_seconds"),
            ("exporter", "output_dir"),
            ("exporter", "output_file"),
        )

        for section, key in required:
            section_data = self.data.get(section) if isinstance(self.data, dict) else None

            if not isinstance(section_data, dict) or section_data.get(key) is None:
                raise ValueError(f"Missing required config key: {section}.{key}")
