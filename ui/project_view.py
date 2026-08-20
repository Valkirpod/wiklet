from PySide6.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QVBoxLayout, QMenu, QMessageBox, QInputDialog, QDockWidget, QMainWindow
from PySide6.QtCore import Qt
from pathlib import Path
from src.project_manager import ProjectManager
from src.collection import Collection
from src.entry import Entry
import shutil

class ProjectView(QWidget):
    def __init__(self, project: ProjectManager, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_collection = None

        layout = QHBoxLayout(self)
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

        # docks
        
        self.dock_area = QMainWindow(self)
        self.dock_area.setWindowFlags(Qt.WindowType.Widget)

        self.content = QTextEdit()
        self.content.setFrameShape(QTextEdit.Shape.StyledPanel)
        self.dock_area.setCentralWidget(self.content)

        self.entrybar = QScrollArea()
        self.entrybar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._build_entrybar()  

        self.entry_dock = QDockWidget("Entries", self.dock_area)
        self.entry_dock.setWidget(self.entrybar)
        self.dock_area.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.entry_dock)

        layout.addWidget(self.dock_area, 6)

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
            btn.clicked.connect(lambda checked=False, c=collection: self._on_collection_selected(c))

    def _toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_btn.setText(">")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("<")
        self.sidebar_visible = not self.sidebar_visible

    def _build_entrybar(self):
        container = QWidget()
        self.entry_layout = QVBoxLayout(container)
        self.entry_layout.setContentsMargins(4, 4, 4, 4)
        self.entry_layout.setSpacing(2)
        self.entry_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.new_entry_btn = QPushButton("+ New Entry")
        self.new_entry_btn.clicked.connect(self._new_entry)
        self.entry_layout.addWidget(self.new_entry_btn)

        self.entrybar.setWidget(container)
        self.entrybar.setWidgetResizable(True)

        self._refresh_entrybar()

    def _refresh_entrybar(self):
        if self.current_collection is None:
            return

        while self.entry_layout.count() > 1:
            item = self.entry_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        for entry in self.current_collection.entries:
            btn = QPushButton()
            btn.setFlat(True)

            btn.setText(btn.fontMetrics().elidedText(entry.name, Qt.TextElideMode.ElideRight, 190))
            btn.setToolTip(entry.name)
            self.entry_layout.addWidget(btn)

            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, b=btn, e=entry: self._show_entry_menu(pos, b, e)
            )
    
    # -- Collection Actions --

    def _show_collection_menu(self, pos, btn, collection):
        menu = QMenu(self)
        menu.addAction("New Collection", self._new_collection)
        menu.addAction("Remove", lambda: self._confirm_remove(collection))
        menu.exec(btn.mapToGlobal(pos))

    def _new_collection(self):
        name, ok = QInputDialog.getText(self, "New Collection", "Collection name:")
        if not ok or not name.strip():
            return
        collection = Collection.create(Path(self.project.project_path), name.strip())
        self.project.add_collection(collection)

    def _confirm_remove(self, collection):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Remove Collection")
        dialog.setText(f"Delete '{collection.name}'? This cannot be undone.")
        delete_btn = dialog.addButton("Delete", QMessageBox.ButtonRole.DestructiveRole)
        dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked == delete_btn:
            shutil.rmtree(collection.path, ignore_errors=True)
            self.project.remove_collection(collection)

    def _on_collection_selected(self, collection):
        self.current_collection = collection
        self.content.setMarkdown(collection.content)

        self._refresh_entrybar()
        
    # -- Entry Actions --
    
    def _show_entry_menu(self, pos, btn, entry):
        menu = QMenu(self)
        menu.addAction("New Entry", self._new_entry)
        menu.addAction("Remove", lambda: self._remove_entry(entry))
        menu.exec(btn.mapToGlobal(pos))
    
    def _new_entry(self):
        if self.current_collection is None:
            return

        name, ok = QInputDialog.getText(self, "New Entry", "Entry name:")
        if not ok or not name.strip():
            return
        entry = Entry.create(self.current_collection.path, name.strip())

        self.current_collection.add_entry(entry)
        self._refresh_entrybar()

    def _remove_entry(self, entry):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Remove Entry")
        dialog.setText(f"Delete '{entry.name}'? This cannot be undone.")
        delete_btn = dialog.addButton("Delete", QMessageBox.ButtonRole.DestructiveRole)
        dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked == delete_btn:
            entry.path.unlink(missing_ok=True)
            print(entry.path)
            self.current_collection.remove_entry(entry)
            self._refresh_entrybar()