## coding: UTF-8
import sys
import os
from PIL import ImageFont
from collections import OrderedDict

# Ref: https://programwiz.org/2021/05/08/python-draw-images-for-font-list
def font_installed_dirs():
    if sys.platform == "win32":
        d = os.environ.get("WINDIR")
        return [os.path.join(d, "fonts")]
    if sys.platform in ("linux", "linux2"):
        dirs = os.environ.get("XDG_DATA_DIRS", "")
        if not dirs:
            dirs = "/usr/share"
        return [os.path.join(d, "fonts") for d in dirs.split(":")]
    if sys.platform == "darwin":
        return ["/Library/Fonts",
                "/System/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")]
    raise Exception(f"unsupported platform:{sys.platform}")
    
def font_path_list():
    dirs = font_installed_dirs()
    l = []
    for d in dirs:
        for parent, _, filenames in os.walk(d):
            for name in filenames:
                l.append(os.path.join(parent, name))
    return l

def font_path_dict():
    ret = OrderedDict()
    for path in font_path_list():
        try:
            f = ImageFont.truetype(path, 24)
            familyName, fontName = f.getname()
            ret[' '.join(f.getname())] = {'path': path, 'pil':f, 'family':familyName, 'opt':fontName}
        except OSError:
            pass
    return ret