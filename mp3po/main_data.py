"""
main_data.py : a place for all things main data
"""

from .header import MP3Header, ChannelEncodings
from .sideinfo import SideInfo

class MainData(object):
    """
    MainData : store operations related to the main data
    """

    def __init__(self, header: MP3Header, side_info: SideInfo):
        self.header = header
        self.side_info = side_info
        side_info_len = 17
        if header.channel != ChannelEncodings.MONO:
            side_info_len = 32
        # if not mono, side_info is 32 bytes. header is 4 bytes
        self.data_size = header.frame_size - side_info_len - 4
        # remove 2 bytes from frame size for CRC
        if header.error_protection:
            self.data_size -= 2
