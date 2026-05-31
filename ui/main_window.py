from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame

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
        
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.content = QFrame()
        self.content.setFrameShape(QFrame.Shape.StyledPanel)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content)