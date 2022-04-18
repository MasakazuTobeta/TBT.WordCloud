## coding: UTF-8
import logging
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
stream_handler.setFormatter(Formatter("%(message)s"))
file_handler = FileHandler("./dump.log")
file_handler.setLevel(DEBUG)
file_handler.setFormatter(Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s"))
logging.basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])
logger = logging.getLogger(__name__)