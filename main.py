# python applicazioni\Tools\GitMap_Control\main.py

import sys
from PyQt6.QtWidgets import QApplication
from git_map_core.main_window import MappaSistemaWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MappaSistemaWindow()
    window.show()
    sys.exit(app.exec())

