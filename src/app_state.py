import json
from pathlib import Path
from platformdirs import user_config_dir
from PySide6.QtCore import QObject, Signal

class AppState(QObject):
    recent_projects_changed = Signal()

    @property
    def default_projects_dir(self) -> Path:
        default = Path(user_config_dir(appname="wiklet", appauthor=False)) / "projects"
        default.mkdir(parents=True, exist_ok=True)
        return default

    def __init__(self):
        super().__init__()
        dir = Path(user_config_dir(appname="wiklet", appauthor=False))
        dir.mkdir(parents=True, exist_ok=True)
        self.file_path = dir / "app_state.json"
        self.data = self._load()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {"recent_projects": []}

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_recent_project(self, path: str):
        path = str(Path(path))
        if path in self.data["recent_projects"]:
            self.data["recent_projects"].remove(path)
        self.data["recent_projects"].insert(0, path)
        self.data["recent_projects"] = self.data["recent_projects"]
        self._save()
        self.recent_projects_changed.emit()

    def remove_recent_project(self, path: str):
        path = str(Path(path))
        if path in self.data["recent_projects"]:
            self.data["recent_projects"].remove(path)
            self._save()
            self.recent_projects_changed.emit()