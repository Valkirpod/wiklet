import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from src.app_state import AppState

def main():
    app = QApplication(sys.argv)
    
    state = AppState()
    window = MainWindow(state)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()