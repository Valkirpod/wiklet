import json
from pathlib import Path
from platformdirs import user_config_dir

class AppState:
    def __init__(self):
        dir = Path(user_config_dir(appname="wiklet", appauthor=False))
        dir.mkdir(parents=True, exist_ok=True)
        self.file_path = dir / "app_state.json"
        print(f"App state file path: {self.file_path}")
        self.data = self._load()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as f:
                return json.load(f)
        
        return {"recent_collections": []}

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_recent_collections(self):
        return self.data["recent_collections"]

    def add_collection(self, path: str):
        if path not in self.data["recent_collections"]:
            self.data["recent_collections"].append(path)
            self._save()

    def remove_collection(self, path: str):
        self.data["recent_collections"].remove(path)
        self._save()
    

# test code
if __name__ == "__main__":
    state = AppState()
    print(state.get_recent_collections())
    state.add_collection("C:/test/characters")
    print(state.get_recent_collections())