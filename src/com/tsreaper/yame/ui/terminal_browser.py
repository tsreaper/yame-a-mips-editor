from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextBrowser

# ------------------------------------------------------------------------------
# Terminal of the simulator
# ------------------------------------------------------------------------------
class TerminalBrowser(QTextBrowser):
    
    def __init__(self, parent = None):
        super(TerminalBrowser, self).__init__(parent)
        
        # Set layout
        font = QFont('Consolas', 11)
        font.setFixedPitch(True)
        
        self.setFont(font)
        self.setStyleSheet(
            'background-color: rgb(41, 49, 52);' \
            'color: rgb(224, 226, 228);'
        )
    
    # --------------------------------------------------------------------------
    # Set size of the widget
    # --------------------------------------------------------------------------
    def sizeHint(self):
        return QSize(480, 480)
