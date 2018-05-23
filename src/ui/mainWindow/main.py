from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QAction

from src.business.configuration.configSystem import ConfigSystem
from src.controller.camera import Camera
from src.ui.filterWindow.main import Main as filters
from src.ui.imageSettingsWindow.main import Main as imag_menu
from src.ui.CCDWindow.main import Main as CCD_menu
from src.ui.ephemerisShooterWindow.main import Main as eph
from src.ui.allSettingsWindow.main import Main as all_settings
from src.ui.mainWindow.mainWindow import MainWindow
from src.ui.mainWindow.status import Status
from src.ui.projectSettingsWindow.main import MainWindow as sw
from src.ui.systemSettingsWindow.main import MainWindow as mw
from src.ui.testWindow.MainWindow2 import MainWindow2 as conts

import sys

class Main(QtWidgets.QMainWindow):
    """
    classe de criacao da interface
    """
    def __init__(self):
        super(Main, self).__init__()
        Status(self)
        # Init Layouts
        if sys.platform.startswith("win"):
            import ctypes
            user32 = ctypes.windll.user32
            self.screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        else:
            import subprocess
            output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
            self.screensize = output.split()[0].split(b'x')
            self.screensize[0] = str(self.screensize[0], "utf-8")
            self.screensize[1] = str(self.screensize[1], "utf-8")
            self.screensize[0] = int(self.screensize[0])
            self.screensize[1] = int(self.screensize[1])
        self.init_widgets()
        self.init_user_interface()
        self.createActions()

        if self.cam.is_connected:
            self.connectAction.setEnabled(False)
            self.disconnectAction.setEnabled(True)
            self.automaticAction.setEnabled(False)
            self.manualAction.setEnabled(False)
            self.stopAction.setEnabled(True)
        else:
            self.connectAction.setEnabled(True)
            self.disconnectAction.setEnabled(False)
            self.automaticAction.setEnabled(False)
            self.manualAction.setEnabled(False)
            self.stopAction.setEnabled(False)

        self.createToolBars()

    def init_user_interface(self):
        self.cont = conts(self)
        self.ephem = eph(self)
        self.a = sw(self)
        self.b = mw(self)
        self.imag = imag_menu(self)
        self.CCD_menu = CCD_menu(self)
        self.cam = Camera()
        self.filters_menu = filters(self)
        self.all_settings = all_settings
        self.init_menu()
        self.init_window_geometry()


        self.cs = ConfigSystem()

        self.info = self.cs.get_site_settings()

        # Connect Camera
        if self.info[0]:
            self.cam.connect()
            self.cam.start_ephemeris_shooter()

    def init_widgets(self):
        a = MainWindow(self)
        self.setCentralWidget(a)

    def init_window_geometry(self):
        # 300, 100, 800, 700
        self.setGeometry(self.screensize[0]/4, self.screensize[1]/4 - self.screensize[1]/6, 0, 0)
        '''qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())'''
        self.setWindowTitle("CCD Controller 1.0.0")
        self.show()
        # self.showMaximized()
    # Creating menubar

    def init_menu(self):
        """
        Creating the Menu Bar
        """
        menubar = self.menuBar()

        a2 = self.open_settings()
        self.add_to_menu(menubar, "System Settings", self.open_settings_system()[0])
        self.add_to_menu(menubar, "Project Settings", a2[0])
        self.add_to_menu(menubar, "Image Settings", self.open_settings_image()[0])
        self.add_to_menu(menubar, "Filters Settings", self.open_settings_filters()[0])
        self.add_to_menu(menubar, "Imager Settings", self.open_settings_CCD()[0])
        self.add_to_menu(menubar, "Open Shutter", self.cam.continuousShooterThread.shutter_control(True))
        self.add_to_menu(menubar, "Close Shutter", self.cam.continuousShooterThread.shutter_control(False))
        # self.add_to_menu(menubar, a2[1], self.open_settings_system()[0], a2[0], self.open_settings_camera()[0])

        # add_to_menu(menubar, open_settings_system(self))

    # All actions needs return a QAction and a menuType, line '&File'
    def action_close(self):
        """
        Creating the button to close the application
        """
        aexit = QtWidgets.QAction(QIcon('\icons\exit.png'), "&Exit", self)
        aexit.setShortcut("Ctrl+Q")
        aexit.setStatusTip("Exit Application")

        # noinspection PyUnresolvedReferences
        aexit.triggered.connect(QtWidgets.qApp.exit)

        return aexit, "&File"

    def action_continuous_shooter(self):
        """
        Inicia e para o modo manual
        """
        actionStart = QtWidgets.QAction('&Start', self)
        actionStop = QtWidgets.QAction('&Stop', self)

        actionStart.triggered.connect(self.cam.start_taking_photo)
        actionStop.triggered.connect(self.cam.stop_taking_photo)

        return actionStart, actionStop

    def action_ephemeris_shooter(self):
        """
        Inicia e para o modo automatico
        """
        actionStart = QtWidgets.QAction('&Start', self)
        actionStop = QtWidgets.QAction('&Stop', self)

        actionStart.triggered.connect(self.cam.start_ephemeris_shooter)
        actionStop.triggered.connect(self.cam.stop_ephemeris_shooter)

        return actionStart, actionStop

    def open_settings(self):
        settings = QtWidgets.QAction('Project Settings', self)
        settings.setShortcut("Ctrl+P")
        settings.setStatusTip("Open Settings window")

        settings.triggered.connect(self.a.show)

        return settings, "&Options"

    def open_settings_system(self):
        setS = QtWidgets.QAction('System Settings', self)
        setS.setShortcut('Ctrl+T')

        setS.triggered.connect(self.b.show)

        return setS, "&Options"

    def open_settings_camera(self):
        setC = QtWidgets.QAction('Camera Settings', self)
        setC.setShortcut("Ctrl+C")

        setC.triggered.connect(self.c.show)

        return setC, "&Options"

    def open_settings_image(self):
        setI = QtWidgets.QAction('Image Settings', self)
        setI.setShortcut("Ctrl+i")

        setI.triggered.connect(self.imag.show)

        return setI, "&Options"

    def open_settings_filters(self):
        setF = QtWidgets.QAction('Filters Settings', self)
        setF.setShortcut("Ctrl+F")

        try:
            setF.triggered.connect(self.filters_menu.show)
        except Exception as e:
            print(e)

        return setF, "&Options"

    def open_settings_CCD(self):
        setCCD = QtWidgets.QAction('Imager Settings', self)

        setCCD.triggered.connect(self.funcao_teste)

        return setCCD, "&Options"

    def funcao_teste(self):
        self.CCD_menu.show()
        self.CCD_menu.show_camera_infos()

    def open_all_settings(self):
        self.all_settings.show()

    def action_connect_disconnect(self):
        setAC = QtWidgets.QAction('Connect', self)
        setAD = QtWidgets.QAction('Disconnect', self)

        setAC.triggered.connect(self.cam.connect)

        setAD.triggered.connect(self.cam.disconnect)

        return 'Connection', setAC, setAD

    def add_to_menu(self, menubar, menu, *args):
        m = menubar.addMenu(menu)
        for w in args:
            m.addAction(w)

        return m

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to quit?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def createActions(self):
        self.connectAction = QAction(QIcon('icons/Connect.png'), 'Connect', self)
        self.connectAction.triggered.connect(self.connect_button)
        '''
        self.connectAction.setCheckable(True)
        self.connectAction.setChecked(True)
        self.setDisabled(True)
        '''

        self.disconnectAction = QAction(QIcon('icons/Disconnect.png'), 'Disconnect', self)
        self.disconnectAction.triggered.connect(self.disconnect_button)

        self.automaticAction = QAction(QIcon('icons/Run_Automatic.png'), 'Run Automatic', self)
        self.automaticAction.triggered.connect(self.ephem_button)
        '''
        self.automaticAction.setCheckable(True)
        self.automaticAction.setChecked(True)
        '''
        self.manualAction = QAction(QIcon('icons/Run_Manual.png'), 'Run Manual', self)
        self.manualAction.triggered.connect(self.manual_button)
        '''
        self.manualAction.setCheckable(True)
        self.manualAction.setChecked(False)
        '''

        self.stopAction = QAction(QIcon('icons/Stop.png'), 'Stop', self)
        self.stopAction.triggered.connect(self.stop_button)

        self.allSettingsAction = QAction(QIcon('icons/Settings.png'), 'Settings', self)
        self.allSettingsAction.triggered.connect(self.open_all_settings)

    def connect_button(self):
        try:
            self.cam.connect()
            if self.cam.is_connected:
                self.connectAction.setEnabled(False)
                self.manualAction.setEnabled(True)
                self.automaticAction.setEnabled(True)
                self.stopAction.setEnabled(False)
                self.disconnectAction.setEnabled(True)
        except Exception as e:
            print(e)

    def disconnect_button(self):
        try:
            self.cam.disconnect()
            self.disconnectAction.setEnabled(False)
            self.manualAction.setEnabled(False)
            self.automaticAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.connectAction.setEnabled(True)
        except Exception as e:
            print(e)

    def ephem_button(self):
        try:
            self.cam.start_ephemeris_shooter()
            self.automaticAction.setEnabled(False)
            self.manualAction.setEnabled(False)
            self.stopAction.setEnabled(True)
        except Exception as e:
            print(e)

    def manual_button(self):
        try:
            self.cam.start_taking_photo()
            self.manualAction.setEnabled(False)
            self.automaticAction.setEnabled(False)
            self.stopAction.setEnabled(True)
        except Exception as e:
            print(e)

    def stop_button(self):
        try:
            if self.cam.continuousShooterThread.isRunning():
                self.cam.stop_taking_photo()
                self.stopAction.setEnabled(False)
                self.manualAction.setEnabled(True)
                self.automaticAction.setEnabled(True)
            elif self.cam.ephemerisShooterThread.isRunning():
                self.cam.stop_ephemeris_shooter()
                self.stopAction.setEnabled(False)
                self.manualAction.setEnabled(True)
                self.automaticAction.setEnabled(True)
        except Exception as e:
            print(e)

    def createToolBars(self):
        self.toolbar = self.addToolBar('Close Toolbar')
        self.toolbar.setIconSize(QtCore.QSize(70, 70))
        self.toolbar.addAction(self.connectAction)
        self.toolbar.addAction(self.disconnectAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.automaticAction)
        self.toolbar.addAction(self.manualAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.stopAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.allSettingsAction)
        self.toolbar.addSeparator()
