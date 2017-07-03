from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QFont, QColor, QPainter, QTextFormat
from PyQt5.QtWidgets import QWidget, QTextEdit, QPlainTextEdit

class LineNumberArea(QWidget):
    
    def __init__(self, parent):
        super(LineNumberArea, self).__init__(parent)
        self.editor = parent
    
    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class MipsEditor(QPlainTextEdit):
    
    def __init__(self, parent = None):
        super(MipsEditor, self).__init__(parent)
        
        font = QFont('Consolas', 11)
        font.setFixedPitch(True)
        
        self.setFont(font)
        self.setStyleSheet(
            'background-color: rgb(41, 49, 52);' \
            'color: rgb(224, 226, 228);'
        )
        
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        self.lineNumberArea = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
    
    def lineNumberAreaWidth(self):
        digits = 0
        count = max(1, self.blockCount())
        while count > 0:
            count = count//10
            digits += 1
        return self.fontMetrics().width('9') * digits + 15
    
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )
    
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(63, 75, 78))
        
        font = QFont('Consolas', 11)
        font.setFixedPitch(True)
        
        painter.setFont(font)
        painter.setPen(QColor(129, 150, 154))
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.drawText(
                    0, top, self.lineNumberArea.width(), height,
                    Qt.AlignCenter, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
    
    def highlightCurrentLine(self):
        extraSelections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(47, 57, 60)
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)
    