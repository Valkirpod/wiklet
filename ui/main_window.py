from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame, QPushButton, QScrollArea, QVBoxLayout, QMenuBar, QInputDialog, QFileDialog, QMenu, QMessageBox
from PySide6.QtCore import Qt, QUrl

from pathlib import Path

from src.app_state import AppState
from src.project_manager import ProjectManager

from ui.welcome_view import WelcomeView
from ui.project_view import ProjectView

from PySide6.QtGui import QDesktopServices

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.project = ProjectManager()
        self.project.collections_changed.connect(self._on_collections_changed)

        menu = QMenuBar()
        self.setMenuBar(menu)

        # project

        file_menu = menu.addMenu("Project")
        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(self._new_project)
        open_action = file_menu.addAction("Open Project")
        open_action.triggered.connect(self._open_project)

        self.recent_menu = QMenu("Recent Projects", self)
        file_menu.addMenu(self.recent_menu)
        self.app_state.recent_projects_changed.connect(self._rebuild_recent_menu)
        self._rebuild_recent_menu()

        file_menu.addSeparator()
        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(self._save_project)
        save_as_action = file_menu.addAction("Save Project As")
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addSeparator()
        open_action = file_menu.addAction("Open Default Projects Directory")
        open_action.triggered.connect(self._open_default_projects_directory)

        # collection

        self.edit_menu = menu.addMenu("Edit")
        self.edit_menu.setEnabled(False)
        self.edit_menu.addAction("New Collection", lambda: self.centralWidget()._new_collection() if isinstance(self.centralWidget(), ProjectView) else None)

        # 

        self._show_welcome()
    
    def _show_welcome(self):
        view = WelcomeView(self)
        view.new_project_requested.connect(self._new_project)
        view.open_project_requested.connect(self._open_project)
        self.setCentralWidget(view)

    def _show_project(self):
        self.edit_menu.setEnabled(True)

        view = ProjectView(self.project)
        self.setCentralWidget(view)
    
    def _on_collections_changed(self):
        if isinstance(self.centralWidget(), ProjectView) and self.project.is_open:
            self.centralWidget()._refresh_sidebar()
    
    def _new_project(self):
        parent_folder = QFileDialog.getExistingDirectory(
            self, "Choose location for new project",
            str(self.app_state.default_projects_dir)
        )
        if not parent_folder:
            return
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if not ok or not name:
            return

        project_folder = self.project.create_new(Path(parent_folder), name)
        self.app_state.add_recent_project(str(project_folder))
        self.setWindowTitle(f"wiklet - {name}")

        self._show_project()
    
    def _open_project(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Open Project",
            str(self.app_state.default_projects_dir)
        )
        if not folder:
            return
        try:
            self.project.open(folder)
            self.setWindowTitle(f"wiklet - {self.project.project_name}")
            self._show_project()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _rebuild_recent_menu(self):
        self.recent_menu.clear()
        recents = self.app_state.data.get("recent_projects", [])
        if not recents:
            empty_action = self.recent_menu.addAction("(No recent projects)")
            empty_action.setEnabled(False)
            return
        for path in recents:
            label = Path(path).name  # just show folder name, not full path
            action = self.recent_menu.addAction(label)
            action.triggered.connect(lambda checked=False, p=path: self._open_recent_project(p))

    def _open_recent_project(self, path):
        try:
            self.project.open(path)
            self.app_state.add_recent_project(path)
            self.setWindowTitle(f"wiklet - {self.project.project_name}")
            self._show_project()
        except FileNotFoundError:
            result = QMessageBox.question(
                self,
                "Project Not Found",
                f"The project at:\n{path}\n\ncould not be found. It may have been "
                f"moved or deleted.\n\nRemove it from Recent Projects?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if result == QMessageBox.Yes:
                self.app_state.remove_recent_project(path)

    def _save_project(self):
        if self.project.is_open:
            self.project.save()
    
    def _save_project_as(self):
        if not self.project.is_open:
            return

        parent_folder = QFileDialog.getExistingDirectory(
            self, "Choose location for new project",
            str(self.app_state.default_projects_dir)
        )
        if not parent_folder:
            return
        name, ok = QInputDialog.getText(self, "Save Project As", "Project name:")
        if not ok or not name:
            return

        project_folder = self.project.save_as(Path(parent_folder), name)
        self.app_state.add_recent_project(str(project_folder))
        self.setWindowTitle(f"wiklet - {name}")
        
    def _open_default_projects_directory(self):
        path = self.app_state.default_projects_dir
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
