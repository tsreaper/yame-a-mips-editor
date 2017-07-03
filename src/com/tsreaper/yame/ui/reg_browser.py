from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextBrowser

from com.tsreaper.yame.constant.register_list import *

# ------------------------------------------------------------------------------
# Register value browser
# ------------------------------------------------------------------------------
class RegBrowser(QTextBrowser):
    
    def __init__(self, parent = None):
        super(RegBrowser, self).__init__(parent)
        
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
        return QSize(220, 0)
    
    # --------------------------------------------------------------------------
    # Display register value
    # --------------------------------------------------------------------------
    def showReg(self, reg):
        # Set style
        html = \
        '<html><head><style type="text/css">' \
        '.space{ padding: 0 10px 0 10px;}' \
        '.hex{ color: rgb(255, 205, 34); padding: 0 5px 0 5px;}' \
        '</style></head>' \
        '<body><table cellspacing="0"><tbody>'
        
        reg_list = list(map(lambda r: r[1:], REGISTER_LIST)) + ['pc', 'hi', 'lo']
        
        for i in range(0, len(reg_list)):
            if i == 32:
                html += '<tr></tr>'
            
            html += \
                '<tr>' \
                '<td class="name">%s</td>' \
                '<td class="space"> </td>' \
                '<td class="hex">%02x</td>' \
                '<td class="hex">%02x</td>' \
                '<td class="hex">%02x</td>' \
                '<td class="hex">%02x</td>' \
                '</tr>' \
                % (reg_list[i], reg[i]>>24, (reg[i]>>16) & 0xFF, (reg[i]>>8) & 0xFF, reg[i] & 0xFF)
        
        html += '</tbody></table></body></html>'
        
        self.setHtml(html)
