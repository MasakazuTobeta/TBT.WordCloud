## coding: UTF-8
import copy
import traceback
import numpy as np
from PIL import Image
import unidic_lite
import MeCab
from wordcloud import WordCloud
from PyQt5.QtCore import pyqtSignal, QThread

class GenerateWordCloud(QThread):
    sig_return_wc = pyqtSignal(object)
    def __init__(self, *args, pref={'use_hinshi': ["名詞", "動詞", "形容詞"],
                                            'font_path': 'C:\\WINDOWS\\fonts\\HGRGE.TTC',
                                            'background_color': "white",
                                            'width': 600,
                                            'height': 400,
                                            }, **kwargs):
        super().__init__(*args, **kwargs)
        self.pref = pref

    def run(self):
        m     = MeCab.Tagger()
        words = []
        try:
            for line in self.read_text_lines():
                node = m.parseToNode(line)
                while node:
                    if node.feature.split(",")[0] in self.pref['use_hinshi']:
                        words.append(node.surface)
                    node = node.next
            if len(words) <= 0:
                words = ['None']
        except:
            traceback.print_exc()
            if len(words) <= 0:
                words = traceback.format_exc()
        pref = copy.deepcopy(self.pref)
        del pref['use_hinshi']
        if 'mask' in pref:
            try:
                pref['mask'] = np.array(Image.open(pref['mask']).resize((pref['width'], pref['height'])))
            except:
                del pref['mask']
        wordcloud = WordCloud(**pref).generate(' '.join(words))
        self.sig_return_wc.emit(wordcloud)