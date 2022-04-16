## coding: UTF-8
import pathlib
import traceback
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from bs4 import BeautifulSoup
import urllib.request as req
import MeCab
from wordcloud import WordCloud
from . import fonts
import matplotlib.pyplot as plt
from matplotlib.figure import SubplotParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import json
import copy
import numpy as np
from PIL import Image

COLOR_MAPS = ['viridis', 'plasma', 'inferno', 'magma'] + [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'] + [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper'] + [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'] + [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c'] + [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']

def getColorMapAsPixmap(cmap, fsize=(2.5,.2), aspect=10):
    sp = SubplotParams(left=0., bottom=0., right=1., top=1.)
    fig = plt.Figure(fsize, subplotpars = sp)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect=aspect, cmap=cmap)
    ax.set_axis_off()
    canvas.draw()
    size = canvas.size()
    width, height = size.width(), size.height()
    im = QtGui.QImage(canvas.buffer_rgba(), width, height, QtGui.QImage.Format_ARGB32)
    return QtGui.QPixmap(im)

class LabeledObject(QWidget):
    def __init__(self, label, objcls, *args, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.label  = QLabel(label)
        self.object = objcls(*args, **kwargs)
        self.l_main = QHBoxLayout()
        self.setLayout(self.l_main)
        self.l_main.addWidget(self.label)
        self.l_main.addWidget(self.object)
        for member in [func for func in dir(self.object) if (callable(getattr(self.object, func)) or isinstance(getattr(self.object, func), pyqtSignal))]:
            if not hasattr(self, member):
                exec(f'self.{member} = self.object.{member}')

class FileLineEdit(QLineEdit):
    sig_return_file = pyqtSignal(object)
    def __init__(self, *args, caption='Selecct mask image file', filter='Image Files (*.png *.jpg *.bmp)', **kwargs):
        super().__init__(*args, **kwargs)
        self.caption = caption
        self.filter = filter
        self.textChanged.connect(self.emit_file_path)
    
    def emit_file_path(self, text):
        self.sig_return_file.emit(text)

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, caption=self.caption, filter=self.filter)
        if fname[0]:
            self.setText(fname[0])

    def mouseDoubleClickEvent(self, *args, **kwargs):
        super().mouseDoubleClickEvent(*args, **kwargs)
        self.openFile()

class SrcGroup(QGroupBox):
    labelChanged = pyqtSignal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.b_radios = QButtonGroup(self)
        self.b_radios.addButton(QRadioButton('Web', parent=self))
#        self.b_radios.addButton(QRadioButton('Twitter', parent=self))
        self.b_radios.addButton(QRadioButton('File', parent=self))
        self.b_radios.addButton(QRadioButton('Folder', parent=self))
        self.b_radios.buttonClicked.connect(lambda _b : self.labelChanged.emit(_b))
        self.l_main = QGridLayout()
        self.setLayout(self.l_main)
        [self.l_main.addWidget(_b, _ii//2, _ii%2) for _ii, _b in enumerate(self.b_radios.buttons())]

class PrefURL():
    def __init__(self, label='URL:'):
        self.url     = LabeledObject('URL:', QLineEdit, 'https://www.mlmarket.jp/')
        self.depth   = LabeledObject('Depth:', QSpinBox)
        self.depth.setMinimum(0)
        self.depth.setMaximum(3)
        self.items   = [self.url, self.depth]
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current == len(self.items):
            raise StopIteration()
        ret = self.items[self.current]
        self.current += 1
        return ret
    
    @staticmethod
    def get_host_name(url):
        return '/'.join(url.split('/')[:4])
    
    @staticmethod
    def get_page_text_only(soup):
        for script in soup(["script", "style"]):
            script.decompose()
        text  = soup.get_text()
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return lines

    def get_text(self, url=None, host=None, depth=None):
        if url is None:
            self.done = []
            url = self.url.text()
        if not url.startswith('http'):
            url = 'http://'+url
        if host is None:
            host = self.get_host_name(url)
        if depth is None:
            depth = self.depth.value()
        if url.startswith(host) and (url not in self.done):
            try:
                res  = req.urlopen(url)
                soup = BeautifulSoup(res, "html.parser")
                for line in self.get_page_text_only(soup):
                    yield line
                self.done.append(url)
                if depth>0:
                    for aa in soup.find_all("a"):
                        link = aa.get("href")
                        for line in self.get_text(url=link, host=host, depth=depth-1):
                            yield line
            except:
                pass

class InputGroup(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pref   = None
        self.l_main = QVBoxLayout()
        self.setLayout(self.l_main)
        self.l_main.addStretch()
    
    def addWidget(self, *args):
        self.l_main.addWidget(*args)
    
    def get_pref_items(self, text):
        if text == 'Web':
            self.pref = PrefURL()
        elif text == 'Twitter':
            self.pref = PrefURL()
        elif text == 'File':
            self.pref = PrefURL()
        elif text == 'Folder':
            self.pref = PrefURL()
        return self.pref

    def setPrefType(self, button):
        while self.l_main.takeAt(0) != None:
            pass
        for items in self.get_pref_items(button.text()):
            self.l_main.addWidget(items)
        self.l_main.addStretch()
    
    def get_text(self):
        for line in self.pref.get_text():
            yield line
        
class PrefGroup(QGroupBox):
    DUMP_PREF_FILE = pathlib.Path('.temp/wc_pref.json')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.l_main = QVBoxLayout()
        self.setLayout(self.l_main)
        self.b_hinshi = [QCheckBox('名詞'), QCheckBox('動詞'), QCheckBox('形容詞'), QCheckBox('副詞')]
        [_b.setChecked(True) for _b in self.b_hinshi]
        w_hinshi = QWidget()
        l_hinshi = QGridLayout()
        w_hinshi.setLayout(l_hinshi)
        [l_hinshi.addWidget(_b, _ii//2, _ii%2) for _ii, _b in enumerate(self.b_hinshi)]
        self.c_font = LabeledObject('フォント:', QComboBox)
        self.d_font = {}
        for _ii, (_name, _vals) in enumerate(fonts.font_path_dict().items()):
            _font = QtGui.QFont(_vals['family'])
            _font.setBold('Bold' in _vals['opt'])
            _font.setItalic('Italic' in _vals['opt'])
            self.c_font.addItem(_name)
            self.c_font.setItemData(_ii, _font, Qt.FontRole)
            self.d_font[_ii] =_vals['path']
        self.c_font.setCurrentText('Meiryo Regular')
        self.s_bg     = LabeledObject('背景色:', QComboBox)
        self.s_bg.addItems(['white','black','red','lime','blue','yellow','magenta','aqua','maroon','green','navy','olive','purple','teal','gray','silver','gold'])
        self.i_width  = LabeledObject('幅:', QSpinBox)
        self.i_width.setMinimum(64)
        self.i_width.setMaximum(4096)
        self.i_width.setValue(640)
        self.i_height = LabeledObject('高さ:', QSpinBox)
        self.i_height.setMinimum(64)
        self.i_height.setMaximum(4096)
        self.i_height.setValue(480)
        self.c_cmap = LabeledObject('文字色:', QComboBox)
        for _ii, _name in enumerate(COLOR_MAPS):
            _pixmap = getColorMapAsPixmap(_name)
            self.c_cmap.addItem(_name)
            self.c_cmap.setItemData(_ii, _pixmap, Qt.DecorationRole)
        self.img_mask = QLabel()
        self.img_mask.setFixedWidth(128)
        self.img_mask.setFixedHeight(128)
        self.s_mask = LabeledObject('マスク:', FileLineEdit, caption='Selecct mask image file', filter='Image Files (*.png *.jpg *.bmp)')
        self.s_mask.sig_return_file.connect(self.set_mask_image)
        [self.l_main.addWidget(_w) for _w in [self.i_width, self.i_height, self.s_bg, self.c_cmap, self.c_font, QLabel('品詞:'), w_hinshi, self.img_mask, self.s_mask]]
        self.load_pref()
    
    def set_mask_image(self, path):
        if pathlib.Path(path).is_file():
            self.img_mask.setPixmap(QtGui.QPixmap(path).scaled(self.img_mask.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.img_mask.setPixmap(QtGui.QPixmap(
                QtGui.QImage(np.ones((1,1), dtype=np.uint8), 1, 1, 1, QtGui.QImage.Format_Grayscale8)
                ).scaled(self.img_mask.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def dump_pref(self, pref):
        self.DUMP_PREF_FILE.parent.mkdir(mode=0x770, parents=True, exist_ok=True)
        with open(self.DUMP_PREF_FILE, 'w') as f:
            json.dump(pref, f, indent=4)
            
    def load_pref(self):
        if self.DUMP_PREF_FILE.is_file():
            with open(self.DUMP_PREF_FILE) as f:
                self.set_pref(json.load(f))
            
    def get_pref(self):
        pref = {'use_hinshi': [_b.text() for _b in self.b_hinshi if _b.isChecked()],
                'font_path': self.d_font[self.c_font.currentIndex()],
                'background_color': self.s_bg.currentText(),
                'colormap': self.c_cmap.currentText(),
                'width': self.i_width.value(),
                'height': self.i_height.value(),
                'mask': self.s_mask.text()}
        self.dump_pref(pref)
        return pref
    
    def set_pref(self, pref):
        try:
            [_b.setChecked(_b.text() in pref['use_hinshi']) for _b in self.b_hinshi]
            ii_font = [_ii for _ii, _path in self.d_font.items() if _path==pref['font_path']]
            if len(ii_font)>0:
                self.c_font.setCurrentIndex(ii_font[0])
            self.s_bg.setCurrentText(pref['background_color'])
            self.c_cmap.setCurrentText(pref['colormap'])
            self.i_width.setValue(pref['width'])
            self.i_height.setValue(pref['height'])
            self.s_mask.setText(pref['mask'])
        except:
            pass


class GenerateWordCloud(QThread):
    sig_return_wc = pyqtSignal(object)
    def __init__(self, *args, g_input, pref={'use_hinshi': ["名詞", "動詞", "形容詞"],
                                            'font_path': 'C:\\WINDOWS\\fonts\\HGRGE.TTC',
                                            'background_color': "white",
                                            'width': 600,
                                            'height': 400,
                                            }, **kwargs):
        super().__init__(*args, **kwargs)
        self.g_input = g_input
        self.pref    = pref

    def run(self):
        m     = MeCab.Tagger()
        words = []
        try:
            for line in self.g_input.get_text():
                node = m.parseToNode(line)
                while node:
                    if node.feature.split(",")[0] in self.pref['use_hinshi']:
                        words.append(node.surface)
                    node = node.next
        except:
            words = traceback.format_exc()
        pref = copy.deepcopy(self.pref)
        del pref['use_hinshi']
        if 'mask' in pref:
            try:
                pref['mask'] = np.array(Image.open(pref['mask']))
            except:
                del pref['mask']
        wordcloud = WordCloud(**pref).generate(' '.join(words))
        self.sig_return_wc.emit(wordcloud)
        

class MenuDock(QDockWidget):
    sig_return_wc = pyqtSignal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w_main = QWidget()
        self.setWidget(self.w_main)
        self.l_main = QVBoxLayout()
        self.w_main.setLayout(self.l_main)
        self.setContentsMargins(0, 0, 0, 0)
        self.g_src   = SrcGroup('Source')
        self.g_input = InputGroup('Input')
        self.g_pref  = PrefGroup('Preference')
        self.g_src.labelChanged.connect(self.g_input.setPrefType)
        self.l_main.addWidget(self.g_src)
        self.l_main.addWidget(self.g_input)
        self.l_main.addWidget(self.g_pref)
    
    def get_wc_pref(self):
        return self.g_pref.get_pref()

    def addWidget(self, *args):
        self.l_main.addWidget(*args)

    def generate_words(self, pref={'use_hinshi': ["名詞", "動詞", "形容詞"],
                                            'font_path': 'C:\\WINDOWS\\fonts\\HGRGE.TTC',
                                            'background_color': "white",
                                            'width': 600,
                                            'height': 400,
                                            }):
        generator = GenerateWordCloud(
            parent=self,
            g_input=self.g_input,
            pref=pref,
        )
        generator.sig_return_wc.connect(lambda wc: self.sig_return_wc.emit(wc))
        generator.start()
        

class MainButtons(QWidget):
    sig_generate = pyqtSignal(object)
    sig_save     = pyqtSignal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.l_main = QVBoxLayout()
        self.b_gen  = QPushButton('Generate')
        self.b_save = QPushButton('Save')
        self.b_gen.clicked.connect(lambda _arg: self.sig_generate.emit(_arg))
        self.b_save.clicked.connect(lambda _arg: self.sig_save.emit(_arg))
        self.l_main.addWidget(self.b_gen)
        self.l_main.addWidget(self.b_save)
        self.setLayout(self.l_main)
        
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
    
    def set_wordclowd(self, wc):
        self.wc = wc
        wc.to_file(str(self.tmp_png))
        for item in self.scene.items():
            self.scene.removeItem(item)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(str(self.tmp_png)))
        self.scene.addPixmap(pixmap)


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.l_main = QVBoxLayout()
        self.l_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.l_main)
    
    def addWidget(self, *args):
        self.l_main.addWidget(*args)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowIcon(QtGui.QIcon('image/icon.png'))
        self.setWindowTitle('ML-WordCloud')
        
        # --- Main widgets
        self.w_main = MainWidget()
        self.setCentralWidget(self.w_main)
        ## --- Canvas widget
        self.w_canvas = MainCanvas(self)
        self.w_main.addWidget(self.w_canvas)
        # --- Menue widget
        self.d_menu = MenuDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.d_menu)
        self.d_menu.sig_return_wc.connect(self.w_canvas.set_wordclowd)
        ## --- Buttons widget
        self.w_buttons = MainButtons(self)
        self.d_menu.addWidget(self.w_buttons)
        self.w_buttons.sig_generate.connect(self.generate)
        self.w_buttons.sig_save.connect(self.export)

    def export(self, *args):
        pass

    def generate(self, *args):
        self.w_canvas.set_loading_gif()
        self.d_menu.generate_words(pref=self.d_menu.get_wc_pref())

    def getPosition(self):
        return self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()
    
    def setPosition(self, px, py, pw, ph):
        self.setGeometry(px, py, pw, ph)