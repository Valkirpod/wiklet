import json
from pathlib import Path

from src.slugify import unique_slug

class Entry:
    def __init__(self, path: Path):
        self.path = path
        data = self._load()
        self.name = data.get("name", self.path.stem)
        self.content = data.get("content", "")

    def _load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        raise FileNotFoundError(f"{self.path} is not a valid entry.")

    def _save(self):
        with open(self.path, "w") as f:
            json.dump({"name": self.name, "content": self.content}, f, indent=2)

    @classmethod
    def create(cls, collection_path: Path, name: str):
        entries_dir = collection_path / "entries"
        entries_dir.mkdir(exist_ok=True)

        file_name = unique_slug(name, entries_dir)
        
        entry_path = entries_dir / f"{file_name}.json"
        with open(entry_path, "w") as f:
            json.dump({"name": name, "content": ""}, f, indent=2)
        
        return cls(entry_path)