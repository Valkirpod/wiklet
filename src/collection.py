import json
from pathlib import Path
import re

class Collection:
    def __init__(self, path: Path):
        self.path = path
        data = self._load()
        self.name = data.get("name", self.path.stem)
        self.content = data.get("content", "")
        self.valid = True
    
    def _load(self):
        collection_path = self.path / "collection.json"

        if collection_path.exists():
            with open(collection_path, "r") as f:
                return json.load(f)
        
        raise FileNotFoundError(f"{collection_path} is not a valid collection.")

    @classmethod
    def create(cls, path: Path, name: str):
        folder_name = name.lower().replace(" ", "-")
        folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)

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

class InvalidCollection:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.content = f"The collection '{self.name}' is invalid."
        self.valid = False