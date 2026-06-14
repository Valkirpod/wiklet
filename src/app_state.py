import json
from pathlib import Path
from platformdirs import user_config_dir
from PySide6.QtCore import QObject, Signal
from src.collection import Collection, InvalidCollection

class AppState(QObject):
    collections_changed = Signal()

    def __init__(self):
        super().__init__()
        dir = Path(user_config_dir(appname="wiklet", appauthor=False))
        dir.mkdir(parents=True, exist_ok=True)
        self.file_path = dir / "app_state.json"
        self.data = self._load()
        self.collections = self._load_collections()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as f:
                return json.load(f)
        
        return {"recent_collections": []}
    
    def _load_collections(self):
        collections = []
        for path in self.data["recent_collections"]:
            try:
                collections.append(Collection(Path(path)))
            except FileNotFoundError:
                collections.append(InvalidCollection(path))
        return collections
    
    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_collection(self, collection: Collection):
        path = str(Path(collection.path))

        if path not in self.data["recent_collections"]:
            self.data["recent_collections"].append(path)
            self._save()
            self.collections.append(collection)
            self.collections_changed.emit()

    def remove_collection(self, path: str):
        self.data["recent_collections"].remove(path)
        self._save()
        self.collections_changed.emit()
    
    @property
    def default_collections_dir(self) -> Path:
        default = Path(user_config_dir(appname="wiklet", appauthor=False)) / "collections"
        default.mkdir(parents=True, exist_ok=True)
        return default