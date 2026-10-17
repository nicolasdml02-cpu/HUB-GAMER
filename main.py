import sys
import os
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    # Desativa aceleradores gráficos conflitantes para evitar tela preta ao redimensionar
    os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())