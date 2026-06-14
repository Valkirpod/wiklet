from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame, QPushButton, QScrollArea, QVBoxLayout, QMenuBar, QFileDialog
from PySide6.QtCore import Qt

from src.app_state import AppState

class MainWindow(QMainWindow):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.state.collections_changed.connect(self._refresh_sidebar)

        self.setWindowTitle("wiklet")
        self.resize(1280, 720)

        menu = QMenuBar()
        file_menu = menu.addMenu("File")
        open_action = file_menu.addAction("Open Collection")
        open_action.triggered.connect(self._open_collection)
        new_action = file_menu.addAction("New Collection")
        # new_action.triggered.connect(self._new_collection)

        self.setMenuBar(menu)

        # QMainWindow cannot have layout itself, need central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # horizontal layout, non fixed sizes will take up remaining space
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = self._build_sidebar()
        layout.addWidget(self.sidebar)

        self.content = QFrame()
        self.content.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.content)

    def _build_sidebar(self):
        scroll = QScrollArea()
        scroll.setFixedWidth(220)
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
        
        for collection in self.state.collections:
            btn = QPushButton(collection.name)
            btn.setFlat(True)
            if not collection.valid:
                btn.setStyleSheet("color: red;")
            self.sidebar_layout.addWidget(btn)
    
    # -- File Actions --

    def _open_collection(self):
        path = QFileDialog.getExistingDirectory(self, "Select Collection Directory")
        if path:
            self.state.add_collection(path)