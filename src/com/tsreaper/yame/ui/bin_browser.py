from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QTextBrowser

# ------------------------------------------------------------------------------
# Binary code browser
# ------------------------------------------------------------------------------
class BinBrowser(QTextBrowser):
    
    def __init__(self, parent = None):
        super(BinBrowser, self).__init__(parent)
        
        self.init_pc = 0
        self.mem = bytearray()
        
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
        return QSize(320, 0)
    
    # --------------------------------------------------------------------------
    # Display binary code
    # --------------------------------------------------------------------------
    def showBin(self, mem, pc = -1):
        self.mem = mem
        
        line_num = 0
        highlighted_line_num = 0
        
        # Set style
        html = \
        '<html><head><style type="text/css">' \
        '.space{ padding: 0 10px 0 10px;}' \
        '.hex{ color: rgb(255, 205, 34); padding: 0 5px 0 5px;}' \
        '.char{ color: rgb(236, 118, 0);}' \
        '.pc{ background-color: rgb(96, 96, 96);}' \
        '</style></head>' \
        '<body><table cellspacing="0"><tbody>'
        
        zero = False
        for i in range(0, len(mem), 4):
            if mem[i] == 0 and mem[i+1] == 0 and mem[i+2] == 0 and mem[i+3] == 0:
                if not zero:
                    line_num += 1
                    html += '<tr>'
                    for t in range(0, 11):
                        html += '<td></td>'
                    html += '</tr>'
                zero = True
            else:
                # Highlight current line if PC points to here
                line_num += 1
                if i == pc:
                    highlighted_line_num = line_num
                    html += '<tr class="pc">'
                else:
                    html += '<tr>'
                
                # Parse invisible characters to '.'
                char_lst = list(map(lambda x: 46 if x < 33 or x > 126 else x, mem[i:i+4]))
                html += \
                    '<td class="addr">%08X</td>' \
                    '<td class="space"> </td>' \
                    '<td class="hex">%02x</td>' \
                    '<td class="hex">%02x</td>' \
                    '<td class="hex">%02x</td>' \
                    '<td class="hex">%02x</td>' \
                    '<td class="space"> </td>' \
                    '<td class="char">&#%d;</td>' \
                    '<td class="char">&#%d;</td>' \
                    '<td class="char">&#%d;</td>' \
                    '<td class="char">&#%d;</td>' \
                    '</tr>' \
                    % (i, *mem[i:i+4], *char_lst)
                zero = False
        html += '</tbody></table></body></html>'
        
        self.setHtml(html)
        
        # Move to highlighted line
        if highlighted_line_num > 0:
            self.moveCursor(QTextCursor.End)
            cursor = QTextCursor(self.document().findBlockByLineNumber(highlighted_line_num*11))
            self.setTextCursor(cursor)
