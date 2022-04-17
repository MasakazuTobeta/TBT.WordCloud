## coding: UTF-8
import sys
try:
    import pyi_splash
    pyi_splash.update_text('Now loading ...')
except:
    pass
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from gui import MainWindow
from Generator.ReaderWeb import GenerateFromWeb
from Generator.ReaderFile import GenerateFromFile
from Generator.ReaderDir import GenerateFromDir

#--------------
# Main object
#--------------
class Main(QObject):
    sig_return_wc = pyqtSignal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app     = QApplication(sys.argv)
        self.widndow = MainWindow(self.app)
        self.__init_sig_con_definition()
    
    # --- Signal/Connect definitions ---
    def __init_sig_con_definition(self):
        self.widndow.sig_generate.connect(self.generate)
        self.sig_return_wc.connect(self.widndow.set_wordcloud)
    
    def set_wordcloud(self, wc):
        self.sig_return_wc.emit(wc)

    def generate(self, kwargs):
        print(kwargs)
        if kwargs['type'] is None:
            kwargs = {'type':'web', 'kwargs':{'url':'', 'depth':0}}
        if kwargs['type'].lower() == 'web':
            generator = GenerateFromWeb
        elif  kwargs['type'].lower() == 'file':
            generator = GenerateFromFile
        elif  kwargs['type'].lower() == 'folder':
            generator = GenerateFromDir
        gen = generator(parent=self, **kwargs['kwargs'])
        gen.sig_return_wc.connect(self.set_wordcloud)
        gen.start()

    def __call__(self):
        self.widndow.show()
        self.app.exec_()

#--------------
# Main
#--------------
if __name__ == "__main__":
    main = Main()
    pyi_splash.close()
    main()
    sys.exit()