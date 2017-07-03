import sys
from PyQt5.QtWidgets import QApplication
from com.tsreaper.yame.ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.resize(960, 640)
window.show()
sys.exit(app.exec_())
