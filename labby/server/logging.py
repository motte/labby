import logging


logger: logging.Logger = logging.getLogger("labby")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler = logging.FileHandler(".labby/labby.log")
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
