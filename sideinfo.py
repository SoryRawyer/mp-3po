"""
sideinfo.py : get the side information for an MP3 frame
"""

from .header import ChannelEncodings

class SideInfo(object):
    """
    SideInfo : parse the side information for an MP3 frame
    """

    def __init__(self, header, mp3_file):
        """
        __init__ : read the given mp3_file and parse the side information
        this expected the mp3_file file object to already be pointing to the side information
        this will modify the mp3_file file object to point to the first byte
            after the side information
        """
        self.side_info_length = 17
        if header.channel != ChannelEncodings.MONO:
            self.side_info_length = 32
        self.side_info_bytes = mp3_file.read(self.side_info_length)
