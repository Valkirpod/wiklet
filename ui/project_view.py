from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QPushButton, QScrollArea, QVBoxLayout, QMenu, QMessageBox, QFileDialog, QInputDialog
from PySide6.QtCore import Qt
from pathlib import Path
from src.project_manager import ProjectManager
from src.collection import Collection
import shutil

class ProjectView(QWidget):
    def __init__(self, project: ProjectManager, parent=None):
        super().__init__(parent)
        self.project = project

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

        self.entrybar = QScrollArea()
        self.entrybar.setMinimumWidth(220)
        self.entrybar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.entrybar.setWidgetResizable(True)
        layout.addWidget(self.entrybar, 1)

        self.content = QFrame()
        self.content.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.content, 5)

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

    def _toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_btn.setText(">")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("<")
        self.sidebar_visible = not self.sidebar_visible
    
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