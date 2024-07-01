# -*- coding: utf-8 -*-

"""Logger creation."""

__all__ = ['logger']
__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020-2021"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from logging import DEBUG
from colorlog import getLogger, StreamHandler, ColoredFormatter

handler = StreamHandler()
handler.setFormatter(ColoredFormatter("%(log_color)s%(message)s"))
logger = getLogger()
logger.setLevel(DEBUG)
logger.addHandler(handler)
