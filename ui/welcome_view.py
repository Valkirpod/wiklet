from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QFont, QColor

class WelcomeView(QWidget):
    new_project_requested = Signal()
    open_project_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # background
        self.original_pixmap = QPixmap("assets/welcome_bg.jpg")
        if self.original_pixmap.isNull():
            print("ERROR: Could not load background image!")
        
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.setPixmap(self.original_pixmap)

        opacity_effect = QGraphicsOpacityEffect(self.bg_label)
        opacity_effect.setOpacity(0.05)
        self.bg_label.setGraphicsEffect(opacity_effect)

        # content
        self.content = QWidget(self)
        layout = QVBoxLayout(self.content)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Title
        title = QLabel("Create or open a project to begin.")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        layout.addSpacing(30)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(30)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        new_btn = self._make_big_button("New Project", "#4CAF50")
        new_btn.clicked.connect(self.new_project_requested)
        btn_row.addWidget(new_btn)

        open_btn = self._make_big_button("Open Project", "#2196F3")
        open_btn.clicked.connect(self.open_project_requested)
        btn_row.addWidget(open_btn)

        layout.addLayout(btn_row)

    def resizeEvent(self, event):
            size = self.width()

            self.bg_label.setFixedSize(size, size)

            y = (self.height() - size) // 2
            self.bg_label.move(0, y)

            self.content.setGeometry(0, 0, self.width(), self.height())

            super().resizeEvent(event)

    def _make_big_button(self, text: str, color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(QSize(125, 125))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        hover_color = QColor(color).lighter(160).name()
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(20, 20, 20, 255);
                color: white;
                border: 2px solid {color};
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: black;
            }}
        """)
        return btn