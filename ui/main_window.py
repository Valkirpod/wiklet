from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame, QPushButton, QScrollArea, QVBoxLayout, QMenuBar, QInputDialog, QFileDialog, QMenu, QMessageBox
from PySide6.QtCore import Qt, QUrl

from pathlib import Path

from src import collection
from src.collection import Collection, InvalidCollection
from src.app_state import AppState
from src.project_manager import ProjectManager

from PySide6.QtGui import QDesktopServices

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.project = ProjectManager()
        self.project.collections_changed.connect(self._refresh_sidebar)

        self.setWindowTitle("wiklet")
        self.showMaximized()

        menu = QMenuBar()
        self.setMenuBar(menu)

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

        # QMainWindow cannot have layout itself, need central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # horizontal layout, non fixed sizes will take up remaining space
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = self._build_sidebar()
        layout.addWidget(self.sidebar, 1)

        self.sidebar_visible = True
        self.toggle_btn = QPushButton("<")
        self.toggle_btn.setFixedWidth(32)
        self.toggle_btn.setFixedHeight(64)
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
        layout.addWidget(self.toggle_btn, 0)

        entrybar = QScrollArea()
        entrybar.setMinimumWidth(220)
        entrybar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        entrybar.setWidgetResizable(True)
        layout.addWidget(entrybar, 1)

        self.content = QFrame()
        self.content.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.content, 5)

    
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

        folder_name = name.lower().replace(" ", "_")
        project_folder = Path(parent_folder) / folder_name

        self.project.create_new(str(project_folder), name)
        self.app_state.add_recent_project(str(project_folder))
        self.setWindowTitle(f"iron editor - {name}")
    
    def _open_project(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Open Project",
            str(self.app_state.default_projects_dir)
        )
        if not folder:
            return
        try:
            self.project.open(folder)
            self.setWindowTitle(f"iron editor - {self.project.project_name}")
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
            self.setWindowTitle(f"iron editor - {self.project.project_name}")
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

        folder_name = name.lower().replace(" ", "_")
        project_folder = Path(parent_folder) / folder_name

        self.project.save_as(str(project_folder), name)
        self.app_state.add_recent_project(str(project_folder))
        self.setWindowTitle(f"iron editor - {name}")
        
    def _open_default_projects_directory(self):
        path = self.app_state.default_projects_dir
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _build_sidebar(self):
        scroll = QScrollArea()
        scroll.setMinimumWidth(220)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        inner = QWidget()
        self.sidebar_layout = QVBoxLayout(inner)
        self.sidebar_layout.setContentsMargins(4, 4, 4, 4)
        self.sidebar_layout.setSpacing(1)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._refresh_sidebar()

        scroll.setWidget(inner)
        return scroll
    
    def _refresh_sidebar(self):
        pass
        while self.sidebar_layout.count():
            item = self.sidebar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for collection in self.project.collections:
            btn = QPushButton()
            btn.setFlat(True)
            if not collection.valid:
                btn.setStyleSheet("color: red;")
            
            # Set a fixed length for the text to ensure it does not scale up the button size.
            btn.setText(btn.fontMetrics().elidedText(collection.name, Qt.TextElideMode.ElideRight, 190))
            btn.setToolTip(collection.name)

            self.sidebar_layout.addWidget(btn)

            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, b=btn, c=collection: self._show_collection_menu(pos, b, c)
            )
    
    def _toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_btn.setText(">")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("<")
        self.sidebar_visible = not self.sidebar_visible

    # -- File Actions --

    def _open_collection(self):
        path = QFileDialog.getExistingDirectory(self, "Select Collection Directory")
        if path:
            try:
                collection = Collection(Path(path))
            except FileNotFoundError:
                collection = InvalidCollection(Path(path))
            self.app_state.add_collection(collection)
    
    def _new_collection(self):
        default_dir = self.app_state.default_collections_dir
        path = QFileDialog.getExistingDirectory(self, "Choose save location", str(default_dir))
        if not path:
            return
        
        name, ok = QInputDialog.getText(self, "New Collection", "Collection name:")
        if not ok or not name.strip():
            return
        
        collection_path = Path(path) / name.strip()
        collection_path.mkdir(exist_ok=True)
        collection = Collection.create(collection_path, name.strip())
        self.app_state.add_collection(collection)
    
    def _show_collection_menu(self, pos, btn, collection):
        menu = QMenu(self)
        menu.addAction("Remove", lambda: self._confirm_remove(collection))
        menu.exec(btn.mapToGlobal(pos))
    
    def _confirm_remove(self, collection):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Remove Collection")
        dialog.setText(f"Remove '{collection.name}'?")
        
        remove_btn = dialog.addButton("Remove from list", QMessageBox.ButtonRole.DestructiveRole)
        delete_btn = dialog.addButton("Delete directory", QMessageBox.ButtonRole.DestructiveRole)
        dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        dialog.exec()
        
        clicked = dialog.clickedButton()
        if clicked == remove_btn:
            self.app_state.remove_collection(collection)
        elif clicked == delete_btn:
            pass
            # TODO: delete the folder from disk
