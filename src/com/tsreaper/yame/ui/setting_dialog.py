from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox

import com.tsreaper.yame.constant.config as config

class SettingDialog(QDialog):
    
    def __init__(self, parent = None):
        super(SettingDialog, self).__init__(parent)
        self.initDialog()
    
    def initDialog(self):
        self.memSizeLabel = QLabel('内存大小(字节)')
        self.memSizeValue = QLineEdit()
        self.textLowerLabel = QLabel('代码段下界(字节)')
        self.textLowerValue = QLineEdit()
        self.textUpperLabel = QLabel('代码段上界(字节)')
        self.textUpperValue = QLineEdit()
        self.dataLowerLabel = QLabel('数据段下界(字节)')
        self.dataLowerValue = QLineEdit()
        self.dataUpperLabel = QLabel('数据段上界(字节)')
        self.dataUpperValue = QLineEdit()
        
        self.memSizeValue.setText(str(config.MEM_SIZE))
        self.textLowerValue.setText(str(config.TEXT_ADDR_LOWER))
        self.textUpperValue.setText(str(config.TEXT_ADDR_UPPER))
        self.dataLowerValue.setText(str(config.DATA_ADDR_LOWER))
        self.dataUpperValue.setText(str(config.DATA_ADDR_UPPER))
        
        self.okButton = QPushButton('确认')
        self.cancelButton = QPushButton('取消')
        self.okButton.clicked.connect(self.okClicked)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QGridLayout()
        layout.addWidget(self.memSizeLabel, 0, 0)
        layout.addWidget(self.memSizeValue, 1, 0)
        layout.addWidget(self.textLowerLabel, 2, 0)
        layout.addWidget(self.textLowerValue, 3, 0)
        layout.addWidget(self.textUpperLabel, 2, 1)
        layout.addWidget(self.textUpperValue, 3, 1)
        layout.addWidget(self.dataLowerLabel, 4, 0)
        layout.addWidget(self.dataLowerValue, 5, 0)
        layout.addWidget(self.dataUpperLabel, 4, 1)
        layout.addWidget(self.dataUpperValue, 5, 1)
        layout.addWidget(self.okButton, 6, 0)
        layout.addWidget(self.cancelButton, 6, 1)
        self.setLayout(layout)
        
        self.setWindowTitle('汇编器设置')
    
    def okClicked(self):
        try:
            mem_size = int(self.memSizeValue.text())
            text_addr_lower = int(self.textLowerValue.text())
            text_addr_upper = int(self.textUpperValue.text())
            data_addr_lower = int(self.dataLowerValue.text())
            data_addr_upper = int(self.dataUpperValue.text())
        except:
            QMessageBox.critical(self, '错误', '<p style="font-size: 16px;">只能输入整数！</p>')
            return
        
        if mem_size > config.MAX_MEM_SIZE:
            QMessageBox.critical(self, '错误', '<p style="font-size: 16px;">内存大小超限，至多 1024KB！</p>')
            return
        
        if text_addr_lower >= 0 and text_addr_lower < mem_size and \
        text_addr_upper >= 0 and text_addr_upper < mem_size and \
        data_addr_lower >= 0 and data_addr_lower < mem_size and \
        data_addr_upper >= 0 and data_addr_upper < mem_size and \
        text_addr_lower <= text_addr_upper and data_addr_lower <= data_addr_upper and \
        (text_addr_upper < data_addr_lower or data_addr_upper < text_addr_lower):
            config.MEM_SIZE = mem_size
            config.TEXT_ADDR_LOWER = text_addr_lower
            config.TEXT_ADDR_UPPER = text_addr_upper
            config.DATA_ADDR_LOWER = data_addr_lower
            config.DATA_ADDR_UPPER = data_addr_upper
            self.accept()
        else:
            QMessageBox.critical(self, '错误', '<p style="font-size: 16px;">填入数据非法！请重新检查。</p>')
