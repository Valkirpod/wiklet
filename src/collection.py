import json
from pathlib import Path

class Collection:
    def __init__(self, path: Path):
        self.path = path
        data = self._load()
        self.name = data.get("name", self.path.stem)
    
    def _load(self):
        #TODO: confirmation to load necessary data and folders if it isn't a collection yet.

        collection_path = self.path / "collection.json"

        if collection_path.exists():
            with open(collection_path, "r") as f:
                return json.load(f)
        
        raise FileNotFoundError(f"{collection_path} is not a valid collection.")
    
    def _save(self):
        data = {
            "name": self.name
        }
        with open(self.collection_path, "w") as f:
            json.dump(data, f, indent=2)

    def _set_name(self, name: str):
        self.name = name
        self._save()