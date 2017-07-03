import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox, QDockWidget
from com.tsreaper.yame.ui.mips_editor import MipsEditor
from com.tsreaper.yame.ui.mips_highlighter import MipsHighlighter
from com.tsreaper.yame.ui.message_browser import MessageBrowser
from com.tsreaper.yame.ui.bin_browser import BinBrowser
from com.tsreaper.yame.ui.simulator_window import SimulatorWindow
from com.tsreaper.yame.ui.setting_dialog import SettingDialog
from com.tsreaper.yame.ui.pseudo_dialog import PseudoDialog

import com.tsreaper.yame.assemble.assembler as assembler
import com.tsreaper.yame.assemble.pseudo as pseudo
import com.tsreaper.yame.disassemble.disassembler as disassembler
import com.tsreaper.yame.simulate.simulator as simulator
import com.tsreaper.yame.constant.config as config
import com.tsreaper.yame.io.coe_file as coe_file
import com.tsreaper.yame.io.bin_file as bin_file
import com.tsreaper.yame.constant.config as config

# ------------------------------------------------------------------------------
# YAME's main window
# ------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        
        self.initAssembler()
        self.initWindow()
    
    # --------------------------------------------------------------------------
    # Initialize assembler
    # --------------------------------------------------------------------------
    def initAssembler(self):
        # Load config and pseudo instructions
        pseudo.load_pseudo(config.CONFIG_FILE)
        config.load_config(config.CONFIG_FILE)
    
    # --------------------------------------------------------------------------
    # Initialize main window
    # --------------------------------------------------------------------------
    def initWindow(self):
        self.currentFile = ''
        self.dirty = False
        
        self.setupFileMenu()
        self.setupSettingMenu()
        self.setupAssembleMenu()
        self.setupHelpMenu()
        self.setupEditor()
        self.setupDockable()
        
        self.setCentralWidget(self.editor)
        self.setWindowTitle('Untitled - YAME')
        self.setWindowIcon(QIcon('icons/yame.png'))
        
        self.simulatorWindow = SimulatorWindow(self)
    
    # --------------------------------------------------------------------------
    # Set when text in the editor is modified
    # --------------------------------------------------------------------------
    def setDirty(self):
        self.dirty = True
        self.updateStatus()
    
    # --------------------------------------------------------------------------
    # Clear dirty state
    # --------------------------------------------------------------------------
    def clearDirty(self):
        self.dirty = False
        self.updateStatus()
    
    # --------------------------------------------------------------------------
    # Check if text in the editor is modified
    # --------------------------------------------------------------------------
    def isDirty(self):
        return self.dirty and (self.currentFile or self.editor.toPlainText())
    
    # --------------------------------------------------------------------------
    # YAME's main window
    # --------------------------------------------------------------------------
    def updateStatus(self):
        title = '* ' if self.isDirty() else ''
        if self.currentFile:
            title += self.currentFile
        else:
            title += 'Untitled'
        title += ' - YAME'
        self.setWindowTitle(title)
    
    # --------------------------------------------------------------------------
    # Confirm message box
    # --------------------------------------------------------------------------
    def okToContinue(self):
        if self.isDirty():
            reply = QMessageBox.question(
                self, 'YAME - 尚未保存的修改',
                '<p align="center" style="font-size: 16px;">存在尚未保存的修改，是否保存？</p>',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.saveFile()
        return True
    
    # --------------------------------------------------------------------------
    # Quit the app
    # --------------------------------------------------------------------------
    def closeEvent(self, event):
        if self.okToContinue():
            # Save config and pseudo instructions
            pseudo.save_pseudo(config.CONFIG_FILE)
            config.save_config(config.CONFIG_FILE)
            
            event.accept()
        else:
            event.ignore()
    
    # --------------------------------------------------------------------------
    # Assemble text to machine code
    # --------------------------------------------------------------------------
    def assemble(self):
        self.msgBrowser.clear()
        self.bottomDock.show()
        
        self.msgBrowser.append('Assembling...')
        try:
            mem, init_pc = assembler.assemble(self.editor.toPlainText())
        except Exception as e:
            # Move editor to the corresponding line
            regex_res = re.search('Line ([0-9]+?):', str(e))
            if regex_res != None:
                line_num = int(regex_res.group(1))
                self.editor.moveCursor(QTextCursor.End)
                cursor = QTextCursor(self.editor.document().findBlockByLineNumber(line_num-1))
                self.editor.setTextCursor(cursor)
            
            self.msgBrowser.append('<font color="red">[ERROR] %s</font>' % (str(e)))
            self.msgBrowser.append('Assembling procedure terminated.')
            return False
        else:
            self.msgBrowser.append('Assembling procedure finished.')
            self.binBrowser.init_pc = init_pc
            self.binBrowser.showBin(mem)
            self.rightDock.show()
            return True
    
    # --------------------------------------------------------------------------
    # Disassemble machine code to text
    # --------------------------------------------------------------------------
    def disassemble(self):
        if not self.okToContinue():
            return False
        
        self.msgBrowser.clear()
        self.bottomDock.show()
        self.rightDock.show()
        
        self.msgBrowser.append('Disassembling...')
        try:
            text = disassembler.disassemble(self.binBrowser.mem)
        except Exception as e:
            self.msgBrowser.append('<font color="red">[ERROR] %s</font>' % (str(e)))
            self.msgBrowser.append('Disassembling procedure terminated.')
            return False
        else:
            self.msgBrowser.append('Disassembling procedure finished.')
            self.currentFile = ''
            self.editor.setPlainText(text)
            return True
    
    # --------------------------------------------------------------------------
    # Simulate MIPS instructions
    # --------------------------------------------------------------------------
    def simulate(self):
        if not self.assemble():
            return False
        
        self.simulatorWindow.loadSimulator(self.binBrowser.mem, self.binBrowser.init_pc)
        self.simulatorWindow.show()
        return True
    
    # --------------------------------------------------------------------------
    # Pesudo instructions management
    # --------------------------------------------------------------------------
    def pseudoIns(self):
        pseudoDialog = PseudoDialog(self)
        pseudoDialog.exec_()
        
        # Update highlighter
        self.highlighter = MipsHighlighter(self.editor.document())
    
    # --------------------------------------------------------------------------
    # Setting memory size, text segment address, etc.
    # --------------------------------------------------------------------------
    def setting(self):
        settingDialog = SettingDialog(self)
        settingDialog.exec_()
    
    # --------------------------------------------------------------------------
    # About message box
    # --------------------------------------------------------------------------
    def about(self):
        QMessageBox.about(
            self, '关于 YAME',
            '<p style="font-size: 16px;">YAME: A MIPS Editor</p>'\
            '<p style="font-size: 16px;">Made by TsReaper</p>'\
            '<p style="font-size: 16px;">YAME 是一个简单的 MIPS 编辑器 / 汇编器 / 反汇编器 / 模拟器。</p>'
            '<p style="font-size: 16px;">工程 github 页面：<a href="https://github.com/TsReaper/YAME-A-MIPS-Editor">https://github.com/TsReaper/YAME-A-MIPS-Editor</a></p>'
        )
    
    # --------------------------------------------------------------------------
    # Clear editor
    # --------------------------------------------------------------------------
    def newFile(self):
        if not self.okToContinue():
            return False
        
        self.editor.clear()
        self.currentFile = ''
        self.clearDirty()
        return True
    
    # --------------------------------------------------------------------------
    # Open a file in the disk
    # --------------------------------------------------------------------------
    def openFile(self):
        if not self.okToContinue():
            return False
        
        path, _ = QFileDialog.getOpenFileName(
            self, '打开', '', '汇编文件 (*.asm)'
        )
        
        if path:
            try:
                # Try to use gbk decoder
                file = open(path, 'r')
                self.editor.setPlainText(file.read())
            except:
                # Try to use utf-8 decoder
                file.close()
                file = open(path, 'r', encoding = 'utf-8')
                self.editor.setPlainText(file.read())
            file.close()
            
            self.currentFile = path
            self.clearDirty()
            return True
        
        return False
    
    # --------------------------------------------------------------------------
    # Save current text
    # --------------------------------------------------------------------------
    def saveFile(self):
        if not self.currentFile:
            return self.saveAnotherFile()
        
        file = open(self.currentFile, 'w')
        file.write(self.editor.toPlainText())
        file.close()
        
        self.clearDirty()
        return True
    
    # --------------------------------------------------------------------------
    # Save copy of current text
    # --------------------------------------------------------------------------
    def saveAnotherFile(self):
        path, _ = QFileDialog.getSaveFileName(
            self, '另存为', self.currentFile if self.currentFile else '', '汇编文件 (*.asm)'
        )
        
        if path:
            file = open(path, 'w')
            file.write(self.editor.toPlainText())
            file.close()
            
            self.currentFile = path
            self.clearDirty()
            return True
        
        return False
    
    # --------------------------------------------------------------------------
    # Import coe or bin file
    # --------------------------------------------------------------------------
    def importFile(self):
        self.newFile()
        
        path, _ = QFileDialog.getOpenFileName(
            self, '导入', '', 'COE文件 (*.coe);;二进制文件 (*.bin)'
        )
        
        try:
            if path.split('.')[-1] == 'coe':
                mem = coe_file.read(path)
            elif path.split('.')[-1] == 'bin':
                mem = bin_file.read(path)
            else:
                return False
        except Exception as e:
            self.msgBrowser.clear()
            self.bottomDock.show()
            self.msgBrowser.append('<font color="red">[ERROR] %s</font>' % (str(e)))
            return False
        
        self.rightDock.show()
        self.binBrowser.showBin(mem)
        
        return self.disassemble()
    
    # --------------------------------------------------------------------------
    # Export coe or bin file
    # --------------------------------------------------------------------------
    def exportFile(self):
        if not self.assemble():
            return False
        
        path, _ = QFileDialog.getSaveFileName(
            self, '导出', '', 'COE文件 (*.coe);;二进制文件 (*.bin)'
        )
        
        if path.split('.')[-1] == 'coe':
            coe_file.write(path, self.binBrowser.mem)
            return True
        if path.split('.')[-1] == 'bin':
            bin_file.write(path, self.binBrowser.mem)
            return True
        
        return False
    
    # --------------------------------------------------------------------------
    # Setup file menu
    # --------------------------------------------------------------------------
    def setupFileMenu(self):
        fileMenu = QMenu('文件(&F)', self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction('新建(&N)', self.newFile, 'Ctrl+N')
        fileMenu.addAction('打开(&O)...', self.openFile, 'Ctrl+O')
        fileMenu.addAction('保存(&S)', self.saveFile, 'Ctrl+S')
        fileMenu.addAction('另存为(&A)...', self.saveAnotherFile, 'Ctrl+Alt+S')
        fileMenu.addAction('导入(&I)...', self.importFile, 'Ctrl+I')
        fileMenu.addAction('导出(&E)...', self.exportFile, 'Ctrl+E')
        fileMenu.addAction('退出(&X)', self.close, 'Alt+F4')
    
    # --------------------------------------------------------------------------
    # Setup setting menu
    # --------------------------------------------------------------------------
    def setupSettingMenu(self):
        settingMenu = QMenu('设置(&S)', self)
        self.menuBar().addMenu(settingMenu)
        
        settingMenu.addAction('汇编器设置', self.setting, 'F6')
        settingMenu.addAction('伪指令', self.pseudoIns, 'F7')
    
    # --------------------------------------------------------------------------
    # Setup assemble menu
    # --------------------------------------------------------------------------
    def setupAssembleMenu(self):
        assembleMenu = QMenu('汇编(&A)', self)
        self.menuBar().addMenu(assembleMenu)
        
        assembleMenu.addAction('汇编(&A)', self.assemble, 'F9')
        assembleMenu.addAction('反汇编(&D)', self.disassemble, 'F10')
        assembleMenu.addAction('模拟(&S)', self.simulate, 'F11')
    
    # --------------------------------------------------------------------------
    # Setup help menu
    # --------------------------------------------------------------------------
    def setupHelpMenu(self):
        helpMenu = QMenu("帮助(&H)", self)
        self.menuBar().addMenu(helpMenu)
        
        helpMenu.addAction('关于(&A)', self.about)
    
    # --------------------------------------------------------------------------
    # Setup mips editor
    # --------------------------------------------------------------------------
    def setupEditor(self):
        self.editor = MipsEditor()
        self.editor.textChanged.connect(self.setDirty)
        self.highlighter = MipsHighlighter(self.editor.document())
    
    # --------------------------------------------------------------------------
    # Setup dockable widgets
    # --------------------------------------------------------------------------
    def setupDockable(self):
        self.msgBrowser = MessageBrowser()
        self.bottomDock = QDockWidget('信息', self)
        self.bottomDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.bottomDock.setWidget(self.msgBrowser)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottomDock)
        self.bottomDock.hide()
        
        self.binBrowser = BinBrowser()
        self.rightDock = QDockWidget('机器码', self)
        self.rightDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.rightDock.setWidget(self.binBrowser)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rightDock)
        self.rightDock.hide()
