"""
frame.py : Frame class
"""

import json

from .header import MP3Header
from .main_data import MainData
from .sideinfo import SideInfo

class Frame(object):
    """
    Frame : container for all frame things
    """

    def __init__(self, header: MP3Header, side_info: SideInfo, main_data: MainData):
        self.header = header
        self.side_info = side_info
        self.main_data = main_data

    def __str__(self):
        return json.dumps({
            'header' : str(self.header),
            'side_info' : str(self.side_info),
            'main_data' : str(self.main_data),
        }).replace('"', '')
