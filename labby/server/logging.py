import logging
import os


class CustomFileHandler(logging.FileHandler):
    def __init__(self, filename: str) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.FileHandler.__init__(self, filename)


logger: logging.Logger = logging.getLogger("labby")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler = CustomFileHandler(".labby/labby.log")
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
