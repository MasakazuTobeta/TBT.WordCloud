## coding: UTF-8
import pathlib
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QFileDialog,
    QLabel,
)
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal

from .menu import *
        
class MainCanvas(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumWidth(320)
        self.setMinimumHeight(240)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.wc      = None
        self.tmp_png = pathlib.Path('./.temp/wc.png')
        self.tmp_png.parent.mkdir(mode=0x770, parents=False, exist_ok=True)

    def set_loading_gif(self):
        del self.scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        gif     = QtGui.QMovie("./image/loading.gif")
        loading = QLabel()
        loading.setMovie(gif)
        gif.start()
        self.scene.addWidget(loading)
    
    def set_wordcloud(self, wc):
        self.wc = wc
        wc.to_file(str(self.tmp_png))
        for item in self.scene.items():
            self.scene.removeItem(item)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(str(self.tmp_png)))
        self.scene.addPixmap(pixmap)
    
    def get_wordcloud(self):
        return self.wc

class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.l_main = QVBoxLayout()
        self.l_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.l_main)
    
    def addWidget(self, *args):
        self.l_main.addWidget(*args)

class MainWindow(QMainWindow):
    sig_generate = pyqtSignal(object)
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowIcon(QtGui.QIcon('image/icon.png'))
        self.setWindowTitle('TBT.WordCloud')
        
        # --- Main widgets
        self.w_main = MainWidget()
        self.setCentralWidget(self.w_main)
        ## --- Canvas widget
        self.w_canvas = MainCanvas(self)
        self.w_main.addWidget(self.w_canvas)
        # --- Menue widget
        self.d_menu = MenuDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.d_menu)
        self.d_menu.sig_return_wc.connect(self.w_canvas.set_wordcloud)
        ## --- Buttons widget
        self.w_buttons = MainButtons(self)
        self.d_menu.addWidget(self.w_buttons)
        self.w_buttons.sig_generate.connect(self.generate)
        self.w_buttons.sig_save.connect(self.export)
        # --- Initial size ---
        self.resize(640, 480)
    
    def set_wordcloud(self, wc):
        self.w_canvas.set_wordcloud(wc)

    def export(self, *args):
        wc = self.w_canvas.get_wordcloud()
        if wc is not None:
            fname = QFileDialog.getSaveFileName(self, 'Export image file', filter='Image Files (*.png *.jpg *.bmp)')
            if fname[0]:
                wc.to_file(fname[0])

    def generate(self, *args):
        self.w_canvas.set_loading_gif()
        kwargs = {'type': self.d_menu.get_type()}
        kwargs['type'] = kwargs['type'].lower() if kwargs['type'] is not None else None
        if kwargs['type'] == 'web':
            kwargs['kwargs'] = {'url':self.d_menu.url, 'depth':self.d_menu.depth, 'pref':self.d_menu.pref}
        elif kwargs['type'] == 'file':
            kwargs['kwargs'] = {'path':self.d_menu.url, 'pref':self.d_menu.pref}
        elif kwargs['type'] == 'folder':
            kwargs['kwargs'] = {'path':self.d_menu.url, 'depth':self.d_menu.depth, 'pref':self.d_menu.pref}
        self.sig_generate.emit(kwargs)

    def getPosition(self):
        return self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()
    
    def setPosition(self, px, py, pw, ph):
        self.setGeometry(px, py, pw, ph)