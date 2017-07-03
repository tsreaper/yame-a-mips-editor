from PyQt5.QtWidgets import QDialog, QListWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox
from com.tsreaper.yame.ui.mips_editor import MipsEditor
from com.tsreaper.yame.ui.mips_highlighter import MipsHighlighter

import com.tsreaper.yame.assemble.pseudo as pseudo
from com.tsreaper.yame.constant.instruction_template import *

class PseudoDialog(QDialog):
    
    def __init__(self, parent = None):
        super(PseudoDialog, self).__init__(parent)
        self.initDialog()
    
    def initDialog(self):
        self.setWindowTitle('伪指令')
        
        self.addButton = QPushButton('添加')
        self.addButton.clicked.connect(self.addItem)
        self.delButton = QPushButton('删除')
        self.delButton.setEnabled(False)
        self.delButton.clicked.connect(self.delItem)
        self.saveButton = QPushButton('保存')
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self.saveItem)
        
        self.pseudoNameLabel = QLabel('伪指令名')
        self.pseudoNameValue = QLineEdit()
        self.pseudoNameValue.setEnabled(False)
        self.operandNumberLabel = QLabel('操作数数量')
        self.operandNumberValue = QLineEdit()
        self.operandNumberValue.setEnabled(False)
        self.realInsLabel = QLabel('真指令')
        self.realInsValue = MipsEditor()
        self.realInsValue.setEnabled(False)
        self.highlighter = MipsHighlighter(self.realInsValue.document())
        
        self.pseudoList = QListWidget(self)
        for op in pseudo.pseudo_dict.keys():
            self.pseudoList.addItem(op)
        self.pseudoList.currentItemChanged.connect(self.changeItem)
        self.updateList('')
        
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.delButton)
        buttonLayout.addWidget(self.saveButton)
        
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(self.pseudoList)
        upperLayout.addLayout(buttonLayout)
        
        lowerLayout = QVBoxLayout()
        lowerLayout.addWidget(self.pseudoNameLabel)
        lowerLayout.addWidget(self.pseudoNameValue)
        lowerLayout.addWidget(self.operandNumberLabel)
        lowerLayout.addWidget(self.operandNumberValue)
        lowerLayout.addWidget(self.realInsLabel)
        lowerLayout.addWidget(self.realInsValue)
        
        layout = QVBoxLayout()
        layout.addLayout(upperLayout)
        layout.addLayout(lowerLayout)
        self.setLayout(layout)
    
    def updateList(self, itemName):
        self.pseudoList.sortItems()
        
        for i in range(0, self.pseudoList.count()):
            if self.pseudoList.item(i).text() == itemName:
                self.pseudoList.setCurrentRow(i)
                return
        
        self.pseudoList.setCurrentRow(0)
    
    def addItem(self):
        id = 0
        while ('pseudo' + str(id)) in pseudo.pseudo_dict.keys():
            id += 1
        
        ins = 'pseudo' + str(id)
        pseudo.pseudo_dict[ins] = [0, '']
        self.pseudoList.addItem(ins)
        self.updateList(ins)
    
    def delItem(self):
        ins = self.pseudoList.currentItem().text()
        pseudo.pseudo_dict.pop(ins)
        self.pseudoList.takeItem(self.pseudoList.currentRow())
        self.updateList('')
    
    def saveItem(self):
        ins = self.pseudoList.currentItem().text()
        new_ins = self.pseudoNameValue.text()
        try:
            opNum = int(self.operandNumberValue.text())
        except:
            opNum = 0
        real = self.realInsValue.toPlainText()
        
        if new_ins == '':
            QMessageBox.critical(self, '错误', '<p style="font-size: 16px;">伪指令名不能为空！</p>')
            return
        elif ins != new_ins and (
            new_ins in pseudo.pseudo_dict.keys() or
            new_ins in R_INSTRUCTIONS.keys() or
            new_ins in I_INSTRUCTIONS.keys() or
            new_ins in J_INSTRUCTIONS.keys()
        ):
            QMessageBox.critical(self, '错误', '<p style="font-size: 16px;">伪指令名与已有指令或伪指令重复！</p>')
            return
        
        pseudo.pseudo_dict.pop(ins)
        self.pseudoList.takeItem(self.pseudoList.currentRow())
        pseudo.pseudo_dict[new_ins] = [opNum, ';'.join(real.split('\n'))]
        self.pseudoList.addItem(new_ins)
        self.updateList(new_ins)
    
    def changeItem(self):
        if self.pseudoList.currentItem() == None:
            self.pseudoNameValue.clear()
            self.operandNumberValue.clear()
            self.realInsValue.clear()
            
            self.pseudoNameValue.setEnabled(False)
            self.operandNumberValue.setEnabled(False)
            self.realInsValue.setEnabled(False)
            self.delButton.setEnabled(False)
            self.saveButton.setEnabled(False)
        else:
            ins = self.pseudoList.currentItem().text()
            
            self.pseudoNameValue.setText(ins)
            self.operandNumberValue.setText(str(pseudo.pseudo_dict[ins][0]))
            self.realInsValue.setPlainText('\n'.join(pseudo.pseudo_dict[ins][1].split(';')))
            
            self.pseudoNameValue.setEnabled(True)
            self.operandNumberValue.setEnabled(True)
            self.realInsValue.setEnabled(True)
            self.delButton.setEnabled(True)
            self.saveButton.setEnabled(True)
