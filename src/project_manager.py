import json
import os
import shutil
from PySide6.QtCore import QObject, Signal
from src.collection import Collection, InvalidCollection
from pathlib import Path

from src.slugify import unique_slug

class ProjectManager(QObject):
    collections_changed = Signal()

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.project_name = None
        self.collections = []

    @property
    def is_open(self):
        return self.project_path is not None

    def create_new(self, parent_path, project_name):
        folder_name = unique_slug(project_name, parent_path)
        folder_path = parent_path / folder_name

        os.makedirs(folder_path, exist_ok=True)
        self.project_path = str(folder_path)
        self.project_name = project_name
        self._write_project_meta()
        self.collections = []
        self.collections_changed.emit()

        return folder_path

    def open(self, folder_path):
        meta_path = os.path.join(folder_path, "wikletproject.json")
        if not os.path.exists(meta_path):
            raise FileNotFoundError("No wikletproject.json found in this folder.")

        with open(meta_path, "r") as f:
            meta = json.load(f)

        self.project_path = folder_path
        self.project_name = meta.get("name", os.path.basename(folder_path))
        self.collections = self._scan_collections()
        self.collections_changed.emit()
    
    def add_collection(self, collection: Collection):
        self.collections.append(collection)
        self.collections_changed.emit()
    
    def remove_collection(self, collection: Collection):
        self.collections = [c for c in self.collections if str(c.path) != str(collection.path)]
        self.collections_changed.emit()
    
    def _scan_collections(self):
        collections = []
        for folder in Path(self.project_path).iterdir():
            if folder.is_dir():
                try:
                    collections.append(Collection(folder))
                except FileNotFoundError:
                    collections.append(InvalidCollection(folder))
        return collections

    def save(self):
        self._write_project_meta()
    
    def save_as(self, new_folder_path, new_project_name):
        if not self.is_open:
            raise RuntimeError("No project is currently open to save.")

        old_path = self.project_path  # capture before it gets overwritten

        self.create_new(new_folder_path, new_project_name)
        shutil.copytree(old_path, new_folder_path, dirs_exist_ok=True)

    def _write_project_meta(self):
        with open(self._path("wikletproject.json"), "w") as f:
            json.dump({"name": self.project_name}, f, indent=4)

    def _path(self, filename):
        return os.path.join(self.project_path, filename)