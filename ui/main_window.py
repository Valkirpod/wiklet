from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame, QPushButton, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("wiklet")
        self.resize(1280, 720)

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

        # Hardcoded fake collections for now
        collections = ["Characters", "Factions", "Locations", "Techniques", "Languages", "Races", "Groups", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample", "Sample"]
        for name in collections:
            btn = QPushButton(name)
            btn.setFlat(True)
            self.sidebar_layout.addWidget(btn)

        scroll.setWidget(inner)
        return scroll