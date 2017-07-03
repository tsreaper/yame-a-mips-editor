from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat

from com.tsreaper.yame.constant.instruction_template import *
from com.tsreaper.yame.constant.register_list import *
import com.tsreaper.yame.assemble.pseudo as pseudo

# ------------------------------------------------------------------------------
# Mips highlighter
# ------------------------------------------------------------------------------
class MipsHighlighter(QSyntaxHighlighter):
    
    def __init__(self, parent = None):
        super(MipsHighlighter, self).__init__(parent)
        
        # Set highlight rules
        self.highlightingRules = []
        
        # Symbols
        sym = '@~\!\^&\*\(\)\-\+\=\|;<\,>/'
        symFormat = QTextCharFormat()
        symFormat.setForeground(QColor(232, 226, 183))
        
        self.highlightingRules.append((QRegExp('[' + sym + ']'), symFormat))
        
        # Immediates
        immFormat = QTextCharFormat()
        immFormat.setForeground(QColor(255, 205, 34))
        
        self.highlightingRules.append((QRegExp(r'\b[0-9]\w*\b'), immFormat))
        
        # Text instruction highlight format
        textInsFormat = QTextCharFormat()
        textInsFormat.setForeground(QColor(147, 199, 99))
        
        textInsPatterns = []
        for i in R_INSTRUCTIONS.keys():
            textInsPatterns.append(r'\b' + i + r'\b')
        for i in I_INSTRUCTIONS.keys():
            textInsPatterns.append(r'\b' + i + r'\b')
        for i in J_INSTRUCTIONS.keys():
            textInsPatterns.append(r'\b' + i + r'\b')
        
        for pattern in textInsPatterns:
            self.highlightingRules.append((QRegExp(pattern), textInsFormat))
        
        # Data instruction highlight format
        dataInsFormat = QTextCharFormat()
        dataInsFormat.setForeground(QColor(160, 130, 189))
        
        dataInsPatterns = [r'\.text\b', r'\.data\b']
        for i in DATA_INSTRUCTIONS.keys():
            dataInsPatterns.append(i.replace('.', r'\.') + r'\b')
        
        for pattern in dataInsPatterns:
            self.highlightingRules.append((QRegExp(pattern), dataInsFormat))
        
        # pseudo instructions
        pseudoInsFormat = QTextCharFormat()
        pseudoInsFormat.setForeground(QColor(0, 128, 192))
        
        pseudoInsPatterns = []
        for i in pseudo.pseudo_dict.keys():
            pseudoInsPatterns.append(r'\b' + i + r'\b')
        
        for pattern in pseudoInsPatterns:
            self.highlightingRules.append((QRegExp(pattern), pseudoInsFormat))
        
        # Parameters for pseudo instructions
        pseudoParamFormat = QTextCharFormat()
        pseudoParamFormat.setForeground(QColor(103, 140, 177))
        
        qreg = QRegExp(r'\[[0-9]+\]')
        qreg.setMinimal(True)
        self.highlightingRules.append((qreg, pseudoParamFormat))
        
        # Register highlight format
        regFormat = QTextCharFormat()
        regFormat.setForeground(QColor(103, 140, 177))
        
        regPatterns = []
        for r in REGISTER_LIST:
            regPatterns.append(r.replace('$', r'\$') + r'\b')
        for r in REGISTER_NUM_LIST:
            regPatterns.append(r.replace('$', r'\$') + r'\b')
        
        for pattern in regPatterns:
            self.highlightingRules.append((QRegExp(pattern), regFormat))
        
        # Strings
        strFormat = QTextCharFormat()
        strFormat.setForeground(QColor(236, 118, 0))
        
        qreg = QRegExp('".*"')
        qreg.setMinimal(True)
        self.highlightingRules.append((qreg, strFormat))
        qreg = QRegExp('\'.*\'')
        qreg.setMinimal(True)
        self.highlightingRules.append((qreg, strFormat))
        
        # Comments
        comFormat = QTextCharFormat()
        comFormat.setForeground(QColor(102, 116, 123))
        
        self.highlightingRules.append((QRegExp('(#.*)|(//.*)'), comFormat))
        qreg = QRegExp('(/\*.*\*/)')
        qreg.setMinimal(True)
        self.highlightingRules.append((qreg, comFormat))
    
    # --------------------------------------------------------------------------
    # Simple highlight method, ignoring multiple lines of comments
    # --------------------------------------------------------------------------
    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
