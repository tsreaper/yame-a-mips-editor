from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon, QTextCursor
from PyQt5.QtWidgets import QWidget, QMainWindow, QAction, QDockWidget, QVBoxLayout
from com.tsreaper.yame.ui.message_browser import MessageBrowser
from com.tsreaper.yame.ui.reg_browser import RegBrowser
from com.tsreaper.yame.ui.bin_browser import BinBrowser
from com.tsreaper.yame.ui.terminal_browser import TerminalBrowser
from com.tsreaper.yame.ui.terminal_input import TerminalInput

import com.tsreaper.yame.simulate.simulator as simulator
from com.tsreaper.yame.simulate.simulation_info_exception import SimulationInfoException
import com.tsreaper.yame.constant.config as config

def parseHtml(s):
    s = s.replace('&', '&amp;')
    s = s.replace(' ', '&nbsp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    s = s.replace('\'', '&apos;')
    s = s.replace('\n', '<br/>')
    return s

class SimulatorWindow(QMainWindow):

    def __init__(self, parent = None):
        super(SimulatorWindow, self).__init__(parent)

        self.initWindow()

    def initWindow(self):
        self.setupToolBar()
        self.setupDockable()
        self.setupTerminal()
        self.setWindowTitle('模拟')

    def setupToolBar(self):
        self.toolBar = self.addToolBar('Control')
        self.toolBar.setIconSize(QSize(48, 48))

        self.resetAction = QAction(
            QIcon('icons/reset.png'), '初始化(F9)', self,
            shortcut = QKeySequence('F9'), statusTip = '初始化(F9)',
            triggered = self.resetSimulator
        )
        self.toolBar.addAction(self.resetAction)

        self.stepAction = QAction(
            QIcon('icons/step.png'), '单步(F10)', self,
            shortcut = QKeySequence('F10'), statusTip = '单步(F10)',
            triggered = self.stepSimulator
        )
        self.toolBar.addAction(self.stepAction)

        self.runAction = QAction(
            QIcon('icons/run.png'), '运行(F11)', self,
            shortcut = QKeySequence('F11'), statusTip = '运行(F11)',
            triggered = self.runSimulator
        )
        self.toolBar.addAction(self.runAction)

    def setupDockable(self):
        self.msgBrowser = MessageBrowser()
        self.bottomDock = QDockWidget('信息', self)
        self.bottomDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.bottomDock.setWidget(self.msgBrowser)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottomDock)
        self.bottomDock.hide()

        self.regBrowser = RegBrowser()
        self.leftDock = QDockWidget('寄存器', self)
        self.leftDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.leftDock.setWidget(self.regBrowser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.leftDock)

        self.binBrowser = BinBrowser()
        self.rightDock = QDockWidget('内存', self)
        self.rightDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.rightDock.setWidget(self.binBrowser)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rightDock)

    def setupTerminal(self):
        self.terminal = TerminalBrowser()
        self.lineInput = TerminalInput()
        self.lineInput.returnPressed.connect(self.updateInput)

        layout = QVBoxLayout()
        layout.addWidget(self.terminal)
        layout.addWidget(self.lineInput)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def updateBrowser(self):
        self.regBrowser.showReg(simulator.reg + [simulator.pc, simulator.hi, simulator.lo])
        self.binBrowser.showBin(simulator.mem, simulator.pc)

        self.terminal.insertHtml(parseHtml(simulator.get_output()))
        self.terminal.moveCursor(QTextCursor.End)

    def updateInput(self):
        simulator.input_data.extend(self.lineInput.text().split())

        self.terminal.insertHtml('<font color="#93C763">' + parseHtml(self.lineInput.text()) + '</font>')
        self.terminal.moveCursor(QTextCursor.End)
        self.lineInput.clear()

        if self.state == 'STEP':
            self.stepSimulator()
        elif self.state == 'RUN':
            self.runSimulator()

    def setWidgetEnabled(self):
        self.stepAction.setEnabled(not simulator.program_end and self.state == 'IDLE')
        self.runAction.setEnabled(not simulator.program_end and self.state == 'IDLE')

        if self.state != 'IDLE':
            self.lineInput.setEnabled(True)
            self.lineInput.setFocus()
        else:
            self.lineInput.setEnabled(False)

    def loadSimulator(self, mem, init_pc):
        if init_pc < 0:
            simulator.load(mem, config.TEXT_ADDR_LOWER)
            self.resetSimulator()
            self.bottomDock.show()
            self.msgBrowser.append('<font color="#FFCD22">[WARNING] Can not find "main" label. Program counter will be set to the lower bound of text segment instead.</font>')
        else:
            simulator.load(mem, init_pc)
            self.resetSimulator()

    def resetSimulator(self):
        simulator.reset()
        self.state = 'IDLE'

        self.bottomDock.hide()
        self.terminal.clear()
        self.lineInput.clear()
        self.msgBrowser.clear()

        self.updateBrowser()
        self.setWidgetEnabled()

    def stepSimulator(self):
        self.state = 'STEP'

        self.msgBrowser.clear()
        self.bottomDock.show()
        self.msgBrowser.append('Simulating...')

        try:
            simulator.step()
        except SimulationInfoException as e:
            self.msgBrowser.append('[INFO] %s' % (str(e)))
        except Exception as e:
            self.msgBrowser.append('<font color="red">[EXCEPTION] %s</font>' % (str(e)))
            self.msgBrowser.append('Simulation terminated.')
            self.state = 'IDLE'
        else:
            self.msgBrowser.append('Simulation terminated.')
            self.state = 'IDLE'

        self.updateBrowser()
        self.setWidgetEnabled()

    def runSimulator(self):
        self.state = 'RUN'

        self.msgBrowser.clear()
        self.bottomDock.show()
        self.msgBrowser.append('Simulating...')

        try:
            simulator.run()
        except SimulationInfoException as e:
            self.msgBrowser.append('[INFO] %s' % (str(e)))
        except Exception as e:
            self.msgBrowser.append('<font color="red">[EXCEPTION] %s</font>' % (str(e)))
            self.msgBrowser.append('Simulation terminated.')
            self.state = 'IDLE'
        else:
            self.msgBrowser.append('Simulation terminated.')
            self.state = 'IDLE'

        self.updateBrowser()
        self.setWidgetEnabled()
