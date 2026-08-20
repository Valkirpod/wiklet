import json
from pathlib import Path

from src.slugify import unique_slug
from src.entry import Entry

class Collection:
    def __init__(self, path: Path):
        self.path = path
        data = self._load()
        self.name = data.get("name", self.path.stem)
        self.content = data.get("content", "")
        self.entries = []
        self.valid = True

        self._load_entries()
    
    def _load(self):
        collection_path = self.path / "collection.json"

        if collection_path.exists():
            with open(collection_path, "r") as f:
                return json.load(f)
        
        raise FileNotFoundError(f"{collection_path} is not a valid collection.")

    @classmethod
    def create(cls, path: Path, name: str):
        folder_name = unique_slug(name, path)

        (path / folder_name).mkdir(exist_ok=True)
        collection_json = path / folder_name / "collection.json"
        data = {"name": name, "content": "# Hello World!"}

        with open(collection_json, "w") as f:
            json.dump(data, f, indent=2)
        
        return cls(path / folder_name)
    
    def _save(self):
        data = {
            "name": self.name,
            "content": self.content
        }
        with open(self.path / "collection.json", "w") as f:
            json.dump(data, f, indent=2)

    def _set_name(self, name: str):
        self.name = name
        self._save()

    def _load_entries(self):
        self.entries = []
        entries_dir = self.path / "entries"

        if not entries_dir.exists():
            return

        for file in entries_dir.glob("*.json"):
            try:
                self.entries.append(Entry(file))
            except Exception:
                pass

    def add_entry(self, entry):
        self.entries.append(entry)

    def remove_entry(self, entry: Entry):
        self.entries = [e for e in self.entries if str(e.path) != str(entry.path)]

class InvalidCollection:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.content = f"The collection '{self.name}' is invalid."
        self.valid = False