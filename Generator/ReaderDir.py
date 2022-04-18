## coding: UTF-8
import os
import pathlib
from . import GenerateWordCloud
from .ReaderFile import GenerateFromFile

class GenerateFromDir(GenerateWordCloud):
    def __init__(self, *args, path, depth, **kwargs):
        super().__init__(*args, **kwargs)
        self.path  = str(path.replace('\\', '/'))
        self.depth = int(depth)
        if self.path[-1] != '/':
            self.path += '/'
    
    def read_text_lines(self):
        for crntDir, _, files in os.walk(self.path):
            if len(files) > 0:
                depth = len(crntDir.replace(self.path,'').split('/')) - 1
                if depth > self.depth:
                    continue
                for path in [os.path.join(crntDir, name) for name in files]:
                    for line in GenerateFromFile.read_text(pathlib.Path(path)):
                        yield line